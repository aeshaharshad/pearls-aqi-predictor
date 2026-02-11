import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from src.ingestion.fetch_data import fetch_aqi_data

load_dotenv()

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB")]
collection = db[os.getenv("MONGODB_COLLECTION")]


def engineer_features(raw: dict):
    ts = raw["timestamp"]

    raw["hour"] = ts.hour
    raw["day"] = ts.day
    raw["month"] = ts.month
    raw["day_of_week"] = ts.weekday()

    raw["ingestion_time"] = datetime.utcnow()
    return raw


def insert_live_aqi_features():
    raw_data = fetch_aqi_data()
    features = engineer_features(raw_data)

    collection.insert_one(features)
    print("✅ Live AQI features inserted into MongoDB")


if __name__ == "__main__":
    insert_live_aqi_features()
