import os
import requests
from datetime import datetime

def get_api_key():
    # Assumes .env file contains: OPENWEATHER_API_KEY=xxxx
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("OPENWEATHER_API_KEY")

API_KEY = get_api_key()

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
    url = (
        f"http://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    r = requests.get(url)
    data = r.json()
    if r.status_code != 200:
        raise Exception(data.get("message", "API error"))
    days = {}
    for entry in data["list"]:
        dt = entry["dt_txt"].split()[0]
        temp = entry["main"]["temp"]
        temp_min = entry["main"]["temp_min"]
        temp_max = entry["main"]["temp_max"]
        weather = entry["weather"][0]["description"]
        humidity = entry["main"]["humidity"]
        if dt not in days:
            days[dt] = {
                "temp_min": temp_min, "temp_max": temp_max,
                "weather": weather, "humidity": humidity, "count": 1
            }
        else:
            days[dt]["temp_min"] = min(days[dt]["temp_min"], temp_min)
            days[dt]["temp_max"] = max(days[dt]["temp_max"], temp_max)
            if humidity > days[dt]["humidity"]:
                days[dt]["humidity"] = humidity
            # Favor latest weather description for the day
            days[dt]["weather"] = weather
            days[dt]["count"] += 1
    sorted_days = sorted(days.items())
    result = []
    for dt, v in sorted_days[:5]:
        result.append({
            "date": dt,
            "temp_min": v["temp_min"],
            "temp_max": v["temp_max"],
            "weather": v["weather"],
            "humidity": v["humidity"]
        })
    return result
