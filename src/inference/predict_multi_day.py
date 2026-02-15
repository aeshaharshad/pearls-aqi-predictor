# src/inference/predict_multi_day.py

import os
from datetime import datetime

import dagshub
import mlflow
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

from src.utils.data_loader import load_data
from src.preprocessing.preprocess import clean_data
from src.features.feature_engineering import (
    add_time_features,
    add_lag_features,
    add_rolling_features,
    add_derived_features,
    create_targets,
)
from src.utils.aqi_converter import pm25_to_aqi_category  # updated function

# -------------------------------------------------
# 1️⃣ Initialize MLflow + DagsHub
# -------------------------------------------------
# Set DagsHub auth via environment variables
DAGSHUB_USER = os.environ["DAGSHUB_USER"]
DAGSHUB_TOKEN = os.environ["DAGSHUB_TOKEN"]

mlflow.set_tracking_uri(
    f"https://{DAGSHUB_USER}:{DAGSHUB_TOKEN}@dagshub.com/{DAGSHUB_USER}/pearls-aqi-predictor.mlflow"
)
def load_production_model(model_name):
    """Load model from MLflow production stage"""
    return mlflow.sklearn.load_model(f"models:/{model_name}@production")

# -------------------------------------------------
# 2️⃣ MongoDB Connection
# -------------------------------------------------
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")  # fallback
client = MongoClient(MONGODB_URI)
db = client["aqi_db"]
prediction_collection = db["aqi_predictions"]

# -------------------------------------------------
# 3️⃣ Build Latest Feature Row
# -------------------------------------------------
def build_latest_features():
    df = load_data()
    df = clean_data(df)

    df = add_time_features(df)
    df = add_lag_features(df, target="pm2_5")
    df = add_rolling_features(df)
    df = add_derived_features(df)
    df = create_targets(df)

    df = df.dropna()
    latest_row = df.iloc[[-1]]

    feature_cols = [
        "pm2_5", "pm10", "co", "no2", "o3", "so2", "nh3",
        "hour", "day", "month", "day_of_week",
        "pm2_5_lag1", "pm2_5_lag2", "pm2_5_lag3", 
        "pm2_5_lag4", "pm2_5_lag5", "pm2_5_lag6",
        "aqi_roll3", "aqi_roll6", "aqi_std3",
        "pm2_5_change_rate", "pm10_change_rate",
        "pm2_5_pm10_ratio",
    ]
    return latest_row[feature_cols]

# -------------------------------------------------
# 4️⃣ Run Multi-Day Forecast
# -------------------------------------------------
def run_prediction():
    print("🔄 Loading production models...")
    models = {
        "t_plus_1": load_production_model("aqi_t_plus_1"),
        "t_plus_2": load_production_model("aqi_t_plus_2"),
        "t_plus_3": load_production_model("aqi_t_plus_3"),
    }

    print("📊 Building latest features...")
    X_latest = build_latest_features()

    print("🔮 Generating forecasts...")
    forecasts = {}
    for horizon, model in models.items():
        pm25_pred = float(model.predict(X_latest)[0])
        aqi_code, aqi_label = pm25_to_aqi_category(pm25_pred)
        forecasts[horizon] = {
            "pm25_prediction": pm25_pred,
            "aqi_category": aqi_code,
            "aqi_category_label": aqi_label
        }

    # Store all horizons in ONE document
    record = {
        "timestamp": datetime.utcnow(),
        "model_source": "MLflow Registry",
        "forecasts": forecasts
    }
    prediction_collection.insert_one(record)

    print("✅ All predictions stored in a single MongoDB document:")
    print(record)

# -------------------------------------------------
# 5️⃣ Main
# -------------------------------------------------
if __name__ == "__main__":
    run_prediction()
