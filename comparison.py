from api import get_weather

def compare_cities(city1, city2):
    """Fetch and return weather data for two cities side by side."""
    data1 = get_weather(city1)
    data2 = get_weather(city2)

    if data1.get("cod") != 200 or data2.get("cod") != 200:
        return None, None

    result1 = {
        "city": city1.title(),
        "temp": data1["main"]["temp"],
        "desc": data1["weather"][0]["description"].capitalize()
    }

    result2 = {
        "city": city2.title(),
        "temp": data2["main"]["temp"],
        "desc": data2["weather"][0]["description"].capitalize()
    }

    return result1, result2