import os
from dotenv import load_dotenv
import requests

# Load the .env file
load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')

def get_weather(city):
    """
    Fetch current weather data for a given city from OpenWeatherMap API.
    Returns JSON data or error message.
    """
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except requests.RequestException as e:
        return {"cod": "error", "message": str(e)}
