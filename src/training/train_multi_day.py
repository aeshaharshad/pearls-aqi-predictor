# src/training/train_multi_day.py

import os
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge

from src.utils.data_loader import load_data
from src.preprocessing.preprocess import clean_data
from src.features.feature_engineering import (
    add_time_features,
    add_lag_features,
    add_rolling_features,
    add_derived_features,
    create_targets
)

from dotenv import load_dotenv

load_dotenv()

# MLflow Setup (REQUIRED for serverless)
import dagshub
import mlflow

dagshub.init(
    repo_owner=os.environ.get("DAGSHUB_USER"),
    repo_name=os.environ.get("DAGSHUB_REPO", "pearls-aqi-predictor"),
    mlflow=True
)
mlflow.set_experiment("AQI_Multi_Day_Forecasting_Production")

print("✅ MLflow tracking enabled")

def get_models():
    return {
        "RandomForest": RandomForestRegressor(
            n_estimators=200, max_depth=12, min_samples_split=5, 
            min_samples_leaf=2, random_state=42, n_jobs=-1
        ),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=200, learning_rate=0.1, max_depth=4, 
            min_samples_split=5, random_state=42
        ),
        "Ridge": Ridge(alpha=1.0),
    }

def train_and_register_best(X, y, horizon_name):
    """Train models, select best, and AUTO-REGISTER to MLflow"""
    
    print(f"\n📊 Training data for {horizon_name}:")
    print(f"  • X shape: {X.shape}")
    print(f"  • y mean: {y.mean():.2f}, std: {y.std():.2f}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    print(f"  • Train: {len(X_train)}, Test: {len(X_test)}")

    best_model = None
    best_rmse = float("inf")
    best_name = None
    best_r2 = -999
    best_run_id = None

    for name, model in get_models().items():
        with mlflow.start_run(run_name=f"{horizon_name}_{name}") as run:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            mae = mean_absolute_error(y_test, preds)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            r2 = r2_score(y_test, preds)

            print(f"\n  [{name}]")
            print(f"    MAE  : {mae:.3f}")
            print(f"    RMSE : {rmse:.3f}")
            print(f"    R²   : {r2:.3f}")

            # Log to MLflow
            mlflow.log_metric("mae", mae)
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2", r2)
            mlflow.log_param("model_type", name)
            mlflow.log_param("horizon", horizon_name)
            mlflow.log_param("n_samples", len(X))
            mlflow.sklearn.log_model(model, "model")

            if rmse < best_rmse:
                best_rmse = rmse
                best_model = model
                best_name = name
                best_r2 = r2
                best_run_id = run.info.run_id

    print(f"\n  🏆 BEST: {best_name} (RMSE={best_rmse:.3f}, R²={best_r2:.3f})")
    
    # AUTO-REGISTER TO MODEL REGISTRY
    model_name = f"aqi_{horizon_name}"
    model_uri = f"runs:/{best_run_id}/model"
    
    try:
        # Register model
        model_version = mlflow.register_model(model_uri, model_name)
        print(f"✅ Registered: {model_name} Version {model_version.version}")
        
        # Set as production
        client = mlflow.tracking.MlflowClient()
        client.set_registered_model_alias(
            model_name, 
            "production", 
            model_version.version
        )
        print(f"✅ Set as @production")
        
    except Exception as e:
        print(f"⚠️ Registration warning: {e}")
        print("   Model logged but not registered. Check DAGsHub manually.")
    
    return best_model

if __name__ == "__main__":
    print("="*60)
    print("🚀 AQI TRAINING PIPELINE (SERVERLESS)")
    print("="*60)
    
    print("\n📥 Loading data...")
    df = load_data()
    df = clean_data(df)
    
    print(f"✅ Raw data: {len(df)} records")
    print(f"📅 Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")

    print("\n🔧 Engineering features...")
    df = add_time_features(df)
    df = add_lag_features(df, target="pm2_5", lags=[24, 48, 72])
    df = add_rolling_features(df)
    df = add_derived_features(df)
    df = create_targets(df)

    df = df.dropna()
    print(f"✅ Final dataset: {df.shape}")
    
    if len(df) < 100:
        print(f"\n⚠️ WARNING: Only {len(df)} samples!")
        print("   Continuing anyway for serverless demo...")
    
    feature_cols = [
        "pm2_5", "pm10", "co", "no2", "o3", "so2", "nh3",
        "hour", "day", "month", "day_of_week", "is_weekend",
        "is_morning_rush", "is_evening_rush",
        "temp", "humidity", "pressure", "wind_speed", "clouds",
        "wind_from_north", "wind_from_east", "wind_from_south", "wind_from_west",
        "temp_high", "temp_low", "stable_atmosphere",
        "pm2_5_lag24", "pm2_5_lag48", "pm2_5_lag72",
        "temp_lag24", "wind_speed_lag24", "humidity_lag24",
        "aqi_roll24", "aqi_roll72", "aqi_std24", "aqi_roll24_max",
        "temp_roll24", "wind_roll24",
        "pm2_5_change_rate", "aqi_change_24h",
        "temp_change_24h", "wind_change_24h",
        "pm2_5_pm10_ratio", "co_no2_ratio"
    ]

    X = df[feature_cols]

    print("\n" + "="*60)
    print("📈 Training & Registering Models")
    print("="*60)
    
    train_and_register_best(X, df["target_t1"], "t_plus_1")
    train_and_register_best(X, df["target_t2"], "t_plus_2")
    train_and_register_best(X, df["target_t3"], "t_plus_3")

    print("\n" + "="*60)
    print("✅ SERVERLESS TRAINING COMPLETE!")
    print("="*60)
    print("\n📍 Models registered in DAGsHub MLflow Registry")
    print("🎯 Tagged with @production alias")
    print("\nNext: Run predictions using registered models")