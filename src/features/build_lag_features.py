import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB config
MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "aqi_feature_store")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "aqi_features")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Load all data
data = pd.DataFrame(list(collection.find()))
data.sort_values("timestamp", inplace=True)

# Build lag features for last 3 days
lags = [1, 2, 3]  # 1-day, 2-day, 3-day
pollutants = ["aqi", "pm2_5", "pm10", "co", "no2", "o3", "so2", "nh3"]

for lag in lags:
    for col in pollutants:
        data[f"{col}_lag_{lag}"] = data[col].shift(lag)

# Drop rows with NaNs (first 3 rows)
data.dropna(inplace=True)

# Save prepared dataset to CSV (optional, useful for training)
data.to_csv("data/processed/aqi_lag_features.csv", index=False)
print(f"✅ Lag features built. Shape: {data.shape}")
