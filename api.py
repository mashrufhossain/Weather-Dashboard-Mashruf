import os
import requests
from datetime import datetime
import collections

def get_api_key():
    # Assumes .env file contains: OPENWEATHER_API_KEY=xxxx
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("OPENWEATHER_API_KEY")

API_KEY = get_api_key()
BASE_URL = "http://api.openweathermap.org/data/2.5/forecast"

def fetch_weather(city):
    url = (
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    r = requests.get(url)
    data = r.json()
    if r.status_code != 200:
        raise Exception(data.get("message", "API error"))
    w = data["weather"][0]["description"]
    return {
        "temp": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "visibility": data.get("visibility", "N/A"),
        "wind": f"{data['wind']['speed']:.2f} m/s, {data['wind'].get('deg', 0):.0f}°",
        "wind_gust": data["wind"].get("gust", "N/A"),
        "sea_level": data["main"].get("sea_level", "N/A"),
        "grnd_level": data["main"].get("grnd_level", "N/A"),
        "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M'),
        "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M'),
        "weather": data["weather"][0]["description"]
    }

def fetch_5day_forecast(city):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
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

        # Optional approximate wind & visibility from first entry of day
        wind = f"{entries[0]['wind']['speed']:.2f} m/s" if 'wind' in entries[0] else "N/A"
        visibility = round(entries[0].get("visibility", 0) / 1000, 1) if 'visibility' in entries[0] else "N/A"

        day = {
            "date": date,
            "temp_min": min(temps),
            "temp_max": max(temps),
            "humidity": round(sum(hums) / len(hums)),
            "weather": weather_desc,
            "wind": wind,
            "visibility": visibility,
        }
        forecast_days.append(day)

    return forecast_days
