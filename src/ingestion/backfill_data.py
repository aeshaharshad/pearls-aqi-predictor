# #src\ingestion\backfill_data.py
# import os
# import requests
# from dotenv import load_dotenv
# from datetime import datetime, timedelta
# from pymongo import MongoClient

# load_dotenv()

# API_KEY = os.getenv("OPENWEATHER_API_KEY")
# MONGO_URI = os.getenv("MONGODB_URI")
# DB_NAME = os.getenv("MONGODB_DB")
# COLLECTION_NAME = os.getenv("MONGODB_COLLECTION")

# client = MongoClient(MONGO_URI)
# collection = client[DB_NAME][COLLECTION_NAME]

# LAT = 31.5497
# LON = 74.3436
# CITY = "Lahore"

# BASE_URL = "http://api.openweathermap.org/data/2.5/air_pollution/history"


# def backfill(days=30):
#     end = datetime.utcnow()
#     start = end - timedelta(days=days)

#     params = {
#         "lat": LAT,
#         "lon": LON,
#         "start": int(start.timestamp()),
#         "end": int(end.timestamp()),
#         "appid": API_KEY
#     }

#     response = requests.get(BASE_URL, params=params)
#     response.raise_for_status()

#     data = response.json()["list"]

#     docs = []
#     for record in data:
#         components = record["components"]
#         ts = datetime.utcfromtimestamp(record["dt"])

#         doc = {
#             "city": CITY,
#             "lat": LAT,
#             "lon": LON,
#             "timestamp": ts,
#             "aqi": record["main"]["aqi"],
#             "pm2_5": components["pm2_5"],
#             "pm10": components["pm10"],
#             "co": components["co"],
#             "no2": components["no2"],
#             "o3": components["o3"],
#             "so2": components["so2"],
#             "nh3": components["nh3"],
#             "hour": ts.hour,
#             "day": ts.day,
#             "month": ts.month,
#             "day_of_week": ts.weekday(),
#             "ingestion_time": datetime.utcnow(),
#             "source": "historical"
#         }
#         docs.append(doc)

#     if docs:
#         collection.insert_many(docs)
#         print(f"✅ Backfilled {len(docs)} AQI records")


# if __name__ == "__main__":
#     backfill(days=30)

# src/ingestion/backfill_with_weather.py

import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pymongo import MongoClient

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_FEATURE_DB", "aqi_db")
COLLECTION_NAME = os.getenv("MONGODB_FEATURE_COLLECTION", "aqi_features")

client = MongoClient(MONGO_URI, tlsInsecure=True)
collection = client[DB_NAME][COLLECTION_NAME]

# Karachi
LAT = 24.8607
LON = 67.0011
CITY = "Karachi"

AQI_URL = "http://api.openweathermap.org/data/2.5/air_pollution/history"
WEATHER_URL = "http://api.openweathermap.org/data/2.5/onecall/timemachine"

def fetch_weather_for_timestamp(ts):
    """Fetch weather data for specific timestamp"""
    params = {
        "lat": LAT,
        "lon": LON,
        "dt": int(ts.timestamp()),
        "appid": API_KEY
    }
    
    try:
        response = requests.get(WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'current' in data:
            weather = data['current']
            return {
                "temp": weather.get("temp", 0) - 273.15,  # Convert to Celsius
                "humidity": weather.get("humidity", 0),
                "pressure": weather.get("pressure", 0),
                "wind_speed": weather.get("wind_speed", 0),
                "wind_deg": weather.get("wind_deg", 0),
                "clouds": weather.get("clouds", 0),
                "weather_main": weather.get("weather", [{}])[0].get("main", "Clear") if weather.get("weather") else "Clear"
            }
    except:
        pass
    
    return {
        "temp": 0, "humidity": 0, "pressure": 0,
        "wind_speed": 0, "wind_deg": 0, "clouds": 0,
        "weather_main": "Unknown"
    }

def backfill_with_weather(days=90):
    """Backfill AQI + Weather data"""
    end = datetime.utcnow()
    start = end - timedelta(days=days)

    # Fetch AQI data
    params = {
        "lat": LAT,
        "lon": LON,
        "start": int(start.timestamp()),
        "end": int(end.timestamp()),
        "appid": API_KEY
    }

    print(f"📡 Fetching AQI for {days} days...")
    response = requests.get(AQI_URL, params=params, timeout=30)
    response.raise_for_status()

    aqi_data = response.json()["list"]
    print(f"✅ Received {len(aqi_data)} AQI records")
    
    # Sample weather data (every 24 hours to save API calls)
    print(f"🌤️ Fetching weather data (sampling every 24h)...")
    weather_cache = {}
    
    for i in range(0, len(aqi_data), 24):  # Every 24 hours
        record = aqi_data[i]
        ts = datetime.utcfromtimestamp(record["dt"])
        weather = fetch_weather_for_timestamp(ts)
        weather_cache[ts.date()] = weather
        
        if i % 240 == 0:  # Progress every 10 days
            print(f"  Fetched weather for {ts.date()}")

    # Merge AQI + Weather
    print(f"🔄 Merging AQI + Weather...")
    docs = []
    for record in aqi_data:
        components = record["components"]
        ts = datetime.utcfromtimestamp(record["dt"])
        
        # Get weather (use cached data from same day)
        weather = weather_cache.get(ts.date(), {
            "temp": 0, "humidity": 0, "pressure": 0,
            "wind_speed": 0, "wind_deg": 0, "clouds": 0,
            "weather_main": "Unknown"
        })

        doc = {
            "city": CITY,
            "lat": LAT,
            "lon": LON,
            "timestamp": ts,
            # AQI data
            "aqi": record["main"]["aqi"],
            "pm2_5": components.get("pm2_5", 0),
            "pm10": components.get("pm10", 0),
            "co": components.get("co", 0),
            "no2": components.get("no2", 0),
            "o3": components.get("o3", 0),
            "so2": components.get("so2", 0),
            "nh3": components.get("nh3", 0),
            # Weather data
            "temp": weather.get("temp", 0),
            "humidity": weather.get("humidity", 0),
            "pressure": weather.get("pressure", 0),
            "wind_speed": weather.get("wind_speed", 0),
            "wind_deg": weather.get("wind_deg", 0),
            "clouds": weather.get("clouds", 0),
            "weather_main": weather.get("weather_main", "Unknown"),
            "ingestion_time": datetime.utcnow(),
            "source": "backfill_with_weather"
        }
        docs.append(doc)

    if docs:
        collection.delete_many({"source": "backfill_with_weather"})
        collection.insert_many(docs)
        print(f"✅ Inserted {len(docs)} records with weather data")
        print(f"📊 Total in DB: {collection.count_documents({})}")

if __name__ == "__main__":
    if not os.getenv("OPENWEATHER_API_KEY"):
        print("❌ Get API key at: https://openweathermap.org/api")
        exit(1)
    
    backfill_with_weather(days=90)