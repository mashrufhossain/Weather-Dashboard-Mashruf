import os
from dotenv import load_dotenv
import requests
import time

# Load the .env file
load_dotenv()
API_KEY = os.getenv('OPENWEATHER_API_KEY')

def get_weather(city, retries=3, initial_delay=2):
    """
    Fetch current weather data for a given city from OpenWeatherMap API
    with exponential backoff retry mechanism.

    Args:
        city (str): City name.
        retries (int): Number of retry attempts.
        initial_delay (int): Initial wait time in seconds.

    Returns:
        dict: JSON data or error dictionary.
    """
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    attempt = 0
    delay = initial_delay
    while attempt < retries:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[Retry] Attempt {attempt + 1} failed: {e}")
            attempt += 1
            if attempt < retries:
                print(f"Waiting {delay} seconds before next attempt...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
    return {"cod": "error", "message": "Failed to fetch data after multiple attempts."}