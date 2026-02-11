import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pymongo import MongoClient

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION")

client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLLECTION_NAME]

LAT = 31.5497
LON = 74.3436
CITY = "Lahore"

BASE_URL = "http://api.openweathermap.org/data/2.5/air_pollution/history"


def backfill(days=30):
    end = datetime.utcnow()
    start = end - timedelta(days=days)

    params = {
        "lat": LAT,
        "lon": LON,
        "start": int(start.timestamp()),
        "end": int(end.timestamp()),
        "appid": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    data = response.json()["list"]

    docs = []
    for record in data:
        components = record["components"]
        ts = datetime.utcfromtimestamp(record["dt"])

        doc = {
            "city": CITY,
            "lat": LAT,
            "lon": LON,
            "timestamp": ts,
            "aqi": record["main"]["aqi"],
            "pm2_5": components["pm2_5"],
            "pm10": components["pm10"],
            "co": components["co"],
            "no2": components["no2"],
            "o3": components["o3"],
            "so2": components["so2"],
            "nh3": components["nh3"],
            "hour": ts.hour,
            "day": ts.day,
            "month": ts.month,
            "day_of_week": ts.weekday(),
            "ingestion_time": datetime.utcnow(),
            "source": "historical"
        }
        docs.append(doc)

    if docs:
        collection.insert_many(docs)
        print(f"✅ Backfilled {len(docs)} AQI records")


if __name__ == "__main__":
    backfill(days=30)
