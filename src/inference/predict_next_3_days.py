import pandas as pd
import joblib
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta



load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "aqi_feature_store")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "aqi_features")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Load latest data to build features
data = pd.DataFrame(list(collection.find()))
data.sort_values("timestamp", inplace=True)
latest = data.iloc[-3:]  # last 3 records to build lag features

pollutants = ["aqi", "pm2_5", "pm10", "co", "no2", "o3", "so2", "nh3"]
features = []

X_new = {}
for lag, rec in enumerate(reversed(latest.to_dict(orient="records")), 1):
    for p in pollutants:
        X_new[f"{p}_lag_{lag}"] = rec[p]
        features.append(f"{p}_lag_{lag}")

X_new_df = pd.DataFrame([X_new])[features]

# Load models
models = {}
predictions = {}
for horizon in ["t+1", "t+2", "t+3"]:
    models[horizon] = joblib.load(f"models/rf_{horizon}.pkl")
    predictions[horizon] = models[horizon].predict(X_new_df)[0]

# Save predictions to MongoDB
future_dates = [latest["timestamp"].iloc[-1] + pd.Timedelta(days=i) for i in range(1, 4)]
for i, horizon in enumerate(["t+1", "t+2", "t+3"]):
    record = {
        "timestamp": future_dates[i],
        "predicted_aqi": predictions[horizon],
    }
    collection.insert_one(record)
    print(f"✅ Inserted prediction for {future_dates[i]}: {predictions[horizon]}")
