import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

LAT = 31.5497   # Lahore
LON = 74.3436
CITY = "Lahore"

BASE_URL = "https://api.openweathermap.org/data/2.5/air_pollution"


def fetch_aqi_data():
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY not found in .env")

    params = {
        "lat": LAT,
        "lon": LON,
        "appid": OPENWEATHER_API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    data = response.json()
    record = data["list"][0]
    components = record["components"]

    result = {
        "city": CITY,
        "lat": LAT,
        "lon": LON,
        "timestamp": datetime.utcfromtimestamp(record["dt"]),
        "aqi": record["main"]["aqi"],
        "pm2_5": components["pm2_5"],
        "pm10": components["pm10"],
        "co": components["co"],
        "no2": components["no2"],
        "o3": components["o3"],
        "so2": components["so2"],
        "nh3": components["nh3"]
    }

    return result


if __name__ == "__main__":
    print(fetch_aqi_data())
