import os
import requests
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd

# Load environment variables
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

LAT = 31.5497   # Lahore
LON = 74.3436

BASE_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
RAW_DATA_PATH = "data/raw"


def fetch_aqi_data():
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY not found in .env")

    params = {
        "lat": LAT,
        "lon": LON,
        "appid": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    data = response.json()
    record = data["list"][0]

    result = {
        "timestamp": datetime.utcfromtimestamp(record["dt"]),
        "aqi": record["main"]["aqi"],
        "pm2_5": record["components"]["pm2_5"],
        "pm10": record["components"]["pm10"],
        "lat": LAT,
        "lon": LON
    }

    return result


def save_raw_data(record: dict):
    os.makedirs(RAW_DATA_PATH, exist_ok=True)

    df = pd.DataFrame([record])

    filename = f"aqi_{record['timestamp'].strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(RAW_DATA_PATH, filename)

    df.to_csv(filepath, index=False)
    print(f"📁 Raw data saved: {filepath}")


if __name__ == "__main__":
    aqi_data = fetch_aqi_data()
    save_raw_data(aqi_data)
