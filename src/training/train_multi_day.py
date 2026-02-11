import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
import numpy as np

# Load processed data
df = pd.read_csv("data/processed/aqi_lag_features.csv")

# Features = lagged pollutants
features = [col for col in df.columns if "lag" in col]
X = df[features]

# Target = next 1, 2, 3 day AQI
y = df[["aqi", "aqi_lag_1", "aqi_lag_2"]].copy()
y.columns = ["t+1", "t+2", "t+3"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Train one model per horizon
models = {}
preds = pd.DataFrame(index=y_test.index)

for horizon in ["t+1", "t+2", "t+3"]:
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train[horizon])
    models[horizon] = model
    preds[horizon] = model.predict(X_test)
    print(f"✅ Trained model for {horizon}")

# Evaluate
for horizon in ["t+1", "t+2", "t+3"]:
    print(f"\n--- {horizon} ---")
    print("MAE:", mean_absolute_error(y_test[horizon], preds[horizon]))
    rmse = np.sqrt(mean_squared_error(y_test[horizon], preds[horizon]))
    print("RMSE:", rmse)
    print("R2:", r2_score(y_test[horizon], preds[horizon]))

# Save models
os.makedirs("models", exist_ok=True)
for horizon, model in models.items():
    joblib.dump(model, f"models/rf_{horizon}.pkl")

print("✅ Multi-day models saved in /models folder")
