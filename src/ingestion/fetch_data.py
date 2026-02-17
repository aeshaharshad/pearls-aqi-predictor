# src/ingestion/fetch_data.py

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# KARACHI coordinates (not Lahore!)
LAT = 24.8607
LON = 67.0011
CITY = "Karachi"

BASE_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

def fetch_aqi_data():
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY not found in .env")

    params = {
        "lat": LAT,
        "lon": LON,
        "appid": OPENWEATHER_API_KEY
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
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
        "pm2_5": components.get("pm2_5", 0),
        "pm10": components.get("pm10", 0),
        "co": components.get("co", 0),
        "no2": components.get("no2", 0),
        "o3": components.get("o3", 0),
        "so2": components.get("so2", 0),
        "nh3": components.get("nh3", 0)
    }

    return result

if __name__ == "__main__":
    print(fetch_aqi_data())