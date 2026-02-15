# src/inference/predict_multi_day.py

import os
from datetime import datetime

# Load environment variables early to avoid import-time errors
from dotenv import load_dotenv
load_dotenv()

import mlflow
import pandas as pd

# Import utilities after environment is loaded
from src.utils.data_loader import load_data, get_client
from src.preprocessing.preprocess import clean_data
from src.features.feature_engineering import (
    add_time_features,
    add_lag_features,
    add_rolling_features,
    add_derived_features,
    create_targets,
)
from src.utils.aqi_converter import pm25_to_aqi_category

# -------------------------------------------------
# 1️⃣ Initialize MLflow + DagsHub
# -------------------------------------------------
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
print("🔗 Connecting to MongoDB...")
client = get_client()

# Feature store
FEATURE_DB = os.getenv("MONGODB_FEATURE_DB", "aqi_db")
FEATURE_COLLECTION = os.getenv("MONGODB_FEATURE_COLLECTION", "aqi_features")

# Prediction store
PREDICTION_DB = os.getenv("MONGODB_PREDICTION_DB", "aqi_db")
PREDICTION_COLLECTION = os.getenv("MONGODB_PREDICTION_COLLECTION", "predictions")
prediction_collection = client[PREDICTION_DB][PREDICTION_COLLECTION]

print("✅ MongoDB connection established")

# -------------------------------------------------
# 3️⃣ Build Latest Feature Row
# -------------------------------------------------
def build_latest_features():
    """Build features from latest data"""
    print("📥 Loading data from MongoDB...")
    df = load_data()
    print(f"✅ Loaded {len(df)} records")
    
    print("🧹 Cleaning data...")
    df = clean_data(df)

    print("🔧 Engineering features...")
    df = add_time_features(df)
    df = add_lag_features(df, target="pm2_5")
    df = add_rolling_features(df)
    df = add_derived_features(df)
    df = create_targets(df)

    df = df.dropna()
    latest_row = df.iloc[[-1]]
    print(f"✅ Latest data point: {latest_row['timestamp'].values[0] if 'timestamp' in latest_row.columns else 'N/A'}")

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
    """Run prediction pipeline"""
    try:
        print("=" * 60)
        print("🚀 Starting AQI Multi-Day Prediction")
        print("=" * 60)
        
        print("\n🔄 Loading production models from MLflow...")
        models = {
            "t_plus_1": load_production_model("aqi_t_plus_1"),
            "t_plus_2": load_production_model("aqi_t_plus_2"),
            "t_plus_3": load_production_model("aqi_t_plus_3"),
        }
        print("✅ All models loaded successfully")

        print("\n📊 Building latest features...")
        X_latest = build_latest_features()

        print("\n🔮 Generating forecasts...")
        forecasts = {}
        for horizon, model in models.items():
            pm25_pred = float(model.predict(X_latest)[0])
            aqi_code, aqi_label = pm25_to_aqi_category(pm25_pred)
            forecasts[horizon] = {
                "pm25_prediction": round(pm25_pred, 2),
                "aqi_category": aqi_code,
                "aqi_category_label": aqi_label
            }
            print(f"  • {horizon}: PM2.5={pm25_pred:.2f} → {aqi_label} (Code: {aqi_code})")

        # Store all horizons in ONE document
        record = {
            "timestamp": datetime.utcnow(),
            "model_source": "MLflow Registry",
            "forecasts": forecasts
        }
        
        print("\n💾 Storing predictions to MongoDB...")
        result = prediction_collection.insert_one(record)
        print(f"✅ Predictions stored with ID: {result.inserted_id}")

        print("\n" + "=" * 60)
        print("✅ PREDICTION PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"Message: {e}")
        import traceback
        traceback.print_exc()
        raise

# -------------------------------------------------
# 5️⃣ Main
# -------------------------------------------------
if __name__ == "__main__":
    run_prediction()