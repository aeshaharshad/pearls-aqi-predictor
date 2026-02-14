import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from src.training.build_dataset import load_dataset
import joblib
import os

MODEL_DIR = "models"
os.makedirs(MODEL_DIR, exist_ok=True)


def train_model():
    df = load_dataset()

    features = [
        "pm2_5", "pm10", "co", "no2", "o3", "so2", "nh3",
        "hour", "day", "month", "day_of_week"
    ]

    X = df[features]
    y = df["aqi"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
        )

    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    print("MAE:", mean_absolute_error(y_test, preds))
    mse = mean_squared_error(y_test, preds)
    rmse = mse ** 0.5
    print("RMSE:", rmse)

    print("R2:", r2_score(y_test, preds))

    joblib.dump(model, f"{MODEL_DIR}/rf_aqi_model.pkl")
    print("✅ Model saved")
    print("AQI min:", y.min())
    print("AQI max:", y.max())



if __name__ == "__main__":
    train_model()
