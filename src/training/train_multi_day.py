import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression

from src.utils.data_loader import load_data
from src.preprocessing.preprocess import clean_data
from src.features.feature_engineering import (
    add_time_features,
    add_lag_features,
    add_rolling_features,
    add_derived_features,
    create_targets,
)
from src.registry.model_registry import save_model

import dagshub
import mlflow

dagshub.init(
    repo_owner="aaa2633522",
    repo_name="pearls-aqi-predictor",
    mlflow=True
)

mlflow.set_experiment("aqi_forecasting")

# -----------------------------
# MODEL CANDIDATES
# -----------------------------
def get_models():
    return {
        "RandomForest": RandomForestRegressor(
            n_estimators=300,
            max_depth=12,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1,
        ),
        "GradientBoosting": GradientBoostingRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=4,
            random_state=42,
        ),
        "LinearRegression": LinearRegression(),
    }


# -----------------------------
# TRAIN + EVALUATE
# -----------------------------
def train_and_select_best(X, y, horizon_name):

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    best_model = None
    best_rmse = float("inf")
    best_name = None

    for name, model in get_models().items():

        with mlflow.start_run(run_name=f"{horizon_name}_{name}"):

            model.fit(X_train, y_train)
            preds = model.predict(X_test)

            mae = mean_absolute_error(y_test, preds)
            rmse = np.sqrt(mean_squared_error(y_test, preds))
            r2 = r2_score(y_test, preds)

            print(f"\n[{horizon_name}] {name}")
            print(f"MAE : {mae:.3f}")
            print(f"RMSE: {rmse:.3f}")
            print(f"R2  : {r2:.3f}")

            # Log metrics
            mlflow.log_metric("mae", mae)
            mlflow.log_metric("rmse", rmse)
            mlflow.log_metric("r2", r2)

            # Log parameters
            mlflow.log_param("model_type", name)
            mlflow.log_param("horizon", horizon_name)

            # Log model artifact
            mlflow.sklearn.log_model(model, "model")

            if rmse < best_rmse:
                best_rmse = rmse
                best_model = model
                best_name = name

    print(f"\n🏆 BEST MODEL for {horizon_name}: {best_name} (RMSE={best_rmse:.3f})")

    save_model(best_model, f"best_{horizon_name}_{best_name}")

    return best_model



# -----------------------------
# MAIN PIPELINE
# -----------------------------
if __name__ == "__main__":

    df = load_data()
    df = clean_data(df)

    # Feature engineering
    df = add_time_features(df)
    df = add_lag_features(df, target="pm2_5")
    df = add_rolling_features(df)
    df = add_derived_features(df)
    df = create_targets(df)

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
        "pm2_5_lag1",
        "pm2_5_lag2",
        "pm2_5_lag3",
        "pm2_5_lag4",
        "pm2_5_lag5",
        "pm2_5_lag6",
        "aqi_roll3",
        "aqi_roll6",
        "aqi_std3",
        "pm2_5_change_rate",
        "pm10_change_rate",
        "pm2_5_pm10_ratio",
    ]

    X = df[feature_cols]

    print("\n==============================")
    print("Training models for t+1")
    print("==============================")
    train_and_select_best(X, df["target_t1"], "t_plus_1")

    print("\n==============================")
    print("Training models for t+2")
    print("==============================")
    train_and_select_best(X, df["target_t2"], "t_plus_2")

    print("\n==============================")
    print("Training models for t+3")
    print("==============================")
    train_and_select_best(X, df["target_t3"], "t_plus_3")

    print("\n✅ Multi-model training & selection complete")
