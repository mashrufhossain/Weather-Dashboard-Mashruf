"""
api.py

API module for Weather Dashboard.

Provides functions to interact with the OpenWeatherMap API:
- search_city_options(query): Retrieve a list of matching cities with formatted display names and coordinates.
- fetch_weather_by_coords(lat, lon): Fetch current weather data (temperature, humidity, wind, sunrise/sunset, etc.).
- fetch_5day_forecast_by_coords(lat, lon): Retrieve 5-day forecast data and summarize it into daily entries (min/max temps, humidity, wind, visibility).
"""

import os                             # For accessing environment variables
import requests                       # To make HTTP requests to the weather API
from datetime import datetime         # For formatting UNIX timestamps into readable times
import collections                    # For grouping forecast data by day
from dotenv import load_dotenv        # To load API keys from a .env file

# Load environment variables from .env file
load_dotenv()

# Fetch the OpenWeatherMap API key from environment variables
API_KEY = os.getenv("OPENWEATHER_API_KEY")


class APIError(Exception):
    """Custom exception for API-related errors."""
    pass


def _get_json(url, params=None):

    """
    Internal helper to perform a GET request with timeout and HTTP-status checks.

    Args:
        url (str): Endpoint URL.
        params (dict, optional): Query parameters to include in the request.

    Returns:
        dict or list: Parsed JSON payload on success.

    Raises:
        APIError: On timeout, network error, or non-200 HTTP status.
    """
    
    try:
        # Attempt the HTTP GET with a short timeout to avoid hanging the app
        response = requests.get(url, params=params, timeout=5)

    except requests.Timeout:
        # Raised when the request exceeds the timeout limit
        raise APIError(f"Request to {url} timed out after 5 seconds")
    
    except requests.RequestException as e:
        # Catches other network-related errors (DNS failure, refused connection, etc.)
        raise APIError(f"Network error contacting {url}: {e}")

    # If the status code is not 200 OK, extract the API's error message if possible
    if response.status_code != 200:
        try:
            error_info = response.json().get("message", response.text)

        except ValueError:
            # JSON decoding failed, fall back to raw text
            error_info = response.text
        raise APIError(f"API returned status {response.status_code} for {url}: {error_info}")

    # If successful, Return the parsed JSON
    return response.json()


def search_city_options(query):

    '''
    Get city options from Geocoding API, return list of dicts:
    { 'display': formatted string, 'lat': ..., 'lon': ... }
    '''

    # Define the geocoding endpoint for searching cities
    url = "http://api.openweathermap.org/geo/1.0/direct"

    # Set request parameters: city query, limit results to 5, include API key
    params = {
        "q": query,
        "limit": 5,
        "appid": API_KEY
    }

    data = _get_json(url, params)

    options = []     # Store city suggestions

    for loc in data:
        # Extract location details
        name = loc.get("name", "")
        state = loc.get("state", "")
        if state:
            state = state.title()     # Capitalize state name
        country = loc.get("country", "").upper()

        # Format display string (with or without state)
        if state:
            display = f"{name}, {state}, {country}"
        else:
            display = f"{name}, {country}"

        # Append formatted city option with lat/lon
        options.append({
            "display": display,
            "lat": loc["lat"],
            "lon": loc["lon"]
        })
    return options     # Return list of location choices

def fetch_weather_by_coords(lat, lon):

    '''
    Fetch current weather data for given latitude and longitude.
    Returns a dict with temperature, humidity, wind, sunrise/sunset, etc.
    '''

    # Build API URL for current weather based on coordinates
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    data = _get_json(url)

    # Get wind direction in degrees (if available)
    wind_deg = data["wind"].get("deg")
    wind_deg_str = f"{wind_deg:.0f}°" if wind_deg is not None else "N/A"

    # Return a dictionary of cleaned and formatted weather info
    return {
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "visibility": data.get("visibility", "N/A"),
        "wind": f"{data['wind']['speed']:.2f} m/s, {wind_deg_str}",
        "wind_gust": data["wind"].get("gust", "N/A"),
        "sea_level": data["main"].get("sea_level", "N/A"),
        "grnd_level": data["main"].get("grnd_level", "N/A"),
        "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M'),
        "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M'),
        "weather": data["weather"][0]["description"]
    }

def fetch_5day_forecast_by_coords(lat, lon):

    '''
    Fetch 5-day weather forecast (in 3-hour intervals) for given latitude and longitude.
    Groups data by day and returns a list of 5 daily summaries.
    '''

    # Build URL for 5-day forecast
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    data = _get_json(url)

    # Raise exception if forecast data is missing
    if "list" not in data:
        raise Exception("Forecast data unavailable")

    # Group entries by date using defaultdict
    daily_data = collections.defaultdict(list)
    for entry in data["list"]:
        date_str = entry["dt_txt"].split(" ")[0]
        daily_data[date_str].append(entry)

    forecast_days = []     # Final list of daily forecasts

    # Process up to 5 days of forecast
    for date, entries in list(daily_data.items())[:5]:
        temps = [e["main"]["temp"] for e in entries]
        hums = [e["main"]["humidity"] for e in entries]
        weather_desc = entries[0]["weather"][0]["description"]

        # Compute average visibility in km if available
        visibilities = [e["visibility"] for e in entries if "visibility" in e]
        if visibilities:
            avg_visibility = round(sum(visibilities) / len(visibilities) / 1000, 1)
            visibility_str = f"{avg_visibility}"
        else:
            visibility_str = "N/A"

        # Compute average wind speed and direction
        wind_speeds = [e["wind"]["speed"] for e in entries if "wind" in e]
        wind_degs = [e["wind"].get("deg") for e in entries if "wind" in e and e["wind"].get("deg") is not None]
        if wind_speeds and wind_degs:
            avg_speed = round(sum(wind_speeds) / len(wind_speeds), 2)
            avg_deg = round(sum(wind_degs) / len(wind_degs))
            wind_str = f"{avg_speed} m/s, {avg_deg}°"
        else:
            wind_str = "N/A"

        # Format date for display (e.g., Fri, Jul 18)
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%a, %b %d")

        # Build the day's forecast summary
        day = {
            "date": formatted_date,
            "temp_min": min(temps),
            "temp_max": max(temps),
            "humidity": round(sum(hums) / len(hums)),
            "weather": weather_desc,
            "wind": wind_str,
            "visibility": visibility_str,
        }
        forecast_days.append(day)

    return forecast_days     # Return list of 5-day summaries
