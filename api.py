import os
import requests
from datetime import datetime
import collections
from dotenv import load_dotenv

# Load once at module level
load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

def search_city_options(query):
    """
    Get city options from Geocoding API, return list of formatted strings.
    """
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": query,
        "limit": 5,
        "appid": API_KEY
    }
    r = requests.get(url, params=params)
    data = r.json()

    options = []
    for loc in data:
        name = loc.get("name", query)
        state = loc.get("state")
        country = loc.get("country", "")
        if state:
            full = f"{name}, {state}, {country}"
        else:
            full = f"{name}, {country}"
        options.append(full)

    return options

def fetch_weather(city):
    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    r = requests.get(url)
    data = r.json()
    if r.status_code != 200:
        raise Exception(data.get("message", "API error"))
    wind_deg = data["wind"].get("deg")
    wind_deg_str = f"{wind_deg:.0f}°" if wind_deg is not None else "N/A"
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

def fetch_5day_forecast(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url)
    data = r.json()
    if "list" not in data:
        raise Exception("Forecast data unavailable")

    daily_data = collections.defaultdict(list)
    for entry in data["list"]:
        date_str = entry["dt_txt"].split(" ")[0]
        daily_data[date_str].append(entry)

    forecast_days = []
    for date, entries in list(daily_data.items())[:5]:
        temps = [e["main"]["temp"] for e in entries]
        hums = [e["main"]["humidity"] for e in entries]
        weather_desc = entries[0]["weather"][0]["description"]

        visibilities = [e["visibility"] for e in entries if "visibility" in e]
        if visibilities:
            avg_visibility = round(sum(visibilities) / len(visibilities) / 1000, 1)
            visibility_str = f"{avg_visibility}"
        else:
            visibility_str = "N/A"

        wind_speeds = [e["wind"]["speed"] for e in entries if "wind" in e]
        wind_degs = [e["wind"].get("deg") for e in entries if "wind" in e and e["wind"].get("deg") is not None]
        if wind_speeds and wind_degs:
            avg_speed = round(sum(wind_speeds) / len(wind_speeds), 2)
            avg_deg = round(sum(wind_degs) / len(wind_degs))
            wind_str = f"{avg_speed} m/s, {avg_deg}°"
        else:
            wind_str = "N/A"

        # Format date for friendlier display
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%a, %b %d")

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

    return forecast_days
