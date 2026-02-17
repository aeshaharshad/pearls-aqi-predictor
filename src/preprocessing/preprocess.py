# src/preprocessing/preprocess.py

import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw AQI dataset - STRICT cleaning for better models"""
    
    df = df.copy()
    
    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Drop rows with missing critical data
    df = df.dropna(subset=["timestamp", "pm2_5", "aqi"])
    
    # CRITICAL: Remove invalid data
    df = df[df["pm2_5"] > 0]  # PM2.5 cannot be 0
    df = df[df["pm2_5"] < 500]  # Remove extreme outliers (500+ is sensor error)
    df = df[df["aqi"] > 0]  # AQI cannot be 0
    df = df[df["aqi"] < 500]  # AQI max is 500
    
    # Remove impossible pollutant values
    if "pm10" in df.columns:
        df = df[df["pm10"] < 1000]  # PM10 shouldn't exceed 1000
    
    # Fill missing pollutants with 0 (some can legitimately be 0)
    pollutant_cols = ["pm10", "co", "no2", "o3", "so2", "nh3"]
    for col in pollutant_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0)
            df.loc[df[col] < 0, col] = 0  # No negative values
    
    # Sort and remove duplicates
    df = df.sort_values("timestamp").reset_index(drop=True)
    df = df.drop_duplicates(subset=["timestamp"], keep='last')
    
    print(f"✅ Cleaned: {len(df)} records (removed {len(df) - len(df)} invalid)")
    
    return df