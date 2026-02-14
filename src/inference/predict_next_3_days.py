import joblib
import pandas as pd
from src.utils.data_loader import load_data
from src.preprocessing.preprocess import clean_data
from src.features.feature_engineering import (
    add_time_features,
    add_lag_features,
    add_rolling_features,
    add_derived_features,
)
from src.utils.aqi_converter import pm25_to_aqi


def predict_next_3_days():
    df = load_data()
    df = clean_data(df)

    df = add_time_features(df)
    df = add_lag_features(df)
    df = add_rolling_features(df)
    df = add_derived_features(df)

    df = df.dropna()

    feature_cols = [
        "pm2_5",
        "pm10",
        "co",
        "no2",
        "o3",
        "so2",
        "nh3",
        "hour",
        "day",
        "month",
        "day_of_week",
        "aqi_lag1",
        "aqi_lag2",
        "aqi_lag3",
        "aqi_roll3",
        "aqi_roll6",
        "aqi_std3",
        "pm2_5_change_rate",
        "pm10_change_rate",
        "pm2_5_pm10_ratio",
    ]

    X_latest = df[feature_cols].iloc[[-1]]

    preds = {}

    for horizon in ["t_plus_1", "t_plus_2", "t_plus_3"]:
        import glob

        model_path = sorted(glob.glob("models/best_t_plus_1_*"))[-1]
        model = joblib.load(model_path)

        pm25_pred = model.predict(X_latest)[0]
        preds[horizon] = {
            "pm2_5": pm25_pred,
            "aqi": pm25_to_aqi(pm25_pred),
        }

    return preds


if __name__ == "__main__":
    predictions = predict_next_3_days()
    for k, v in predictions.items():
        print(k, "→ PM2.5:", round(v["pm2_5"], 2), "| AQI:", v["aqi"])
