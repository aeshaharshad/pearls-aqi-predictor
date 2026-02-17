# src/features/feature_engineering.py

import pandas as pd
import numpy as np

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add time features"""
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day
    df["month"] = df["timestamp"].dt.month
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    
    # Rush hour features (traffic impact)
    df["is_morning_rush"] = ((df["hour"] >= 7) & (df["hour"] <= 9)).astype(int)
    df["is_evening_rush"] = ((df["hour"] >= 17) & (df["hour"] <= 19)).astype(int)
    
    return df

def add_weather_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add weather-based features"""
    # Wind direction categories (important for pollution dispersion)
    if "wind_deg" in df.columns:
        df["wind_from_north"] = ((df["wind_deg"] >= 315) | (df["wind_deg"] < 45)).astype(int)
        df["wind_from_east"] = ((df["wind_deg"] >= 45) & (df["wind_deg"] < 135)).astype(int)
        df["wind_from_south"] = ((df["wind_deg"] >= 135) & (df["wind_deg"] < 225)).astype(int)
        df["wind_from_west"] = ((df["wind_deg"] >= 225) & (df["wind_deg"] < 315)).astype(int)
    
    # Temperature bands
    if "temp" in df.columns:
        df["temp_high"] = (df["temp"] > 30).astype(int)  # High temp increases ozone
        df["temp_low"] = (df["temp"] < 15).astype(int)   # Low temp traps pollution
    
    # Atmospheric stability (low wind + low pressure = trapped pollution)
    if "wind_speed" in df.columns and "pressure" in df.columns:
        df["stable_atmosphere"] = ((df["wind_speed"] < 2) & (df["pressure"] < 1010)).astype(int)
    
    return df

def add_lag_features(df: pd.DataFrame, target="pm2_5", lags=[24, 48, 72]) -> pd.DataFrame:
    """Daily lags"""
    for lag in lags:
        df[f"{target}_lag{lag}"] = df[target].shift(lag)
        
        # Also add weather lags (yesterday's weather affects today's AQI)
        if "temp" in df.columns:
            df[f"temp_lag{lag}"] = df["temp"].shift(lag)
        if "wind_speed" in df.columns:
            df[f"wind_speed_lag{lag}"] = df["wind_speed"].shift(lag)
        if "humidity" in df.columns:
            df[f"humidity_lag{lag}"] = df["humidity"].shift(lag)
    
    return df

def add_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    """Rolling features"""
    df["aqi_roll24"] = df["aqi"].rolling(24, min_periods=12).mean()
    df["aqi_roll72"] = df["aqi"].rolling(72, min_periods=36).mean()
    df["aqi_std24"] = df["aqi"].rolling(24, min_periods=12).std()
    df["aqi_roll24_max"] = df["aqi"].rolling(24, min_periods=12).max()
    
    # Weather rolling averages
    if "temp" in df.columns:
        df["temp_roll24"] = df["temp"].rolling(24, min_periods=12).mean()
    if "wind_speed" in df.columns:
        df["wind_roll24"] = df["wind_speed"].rolling(24, min_periods=12).mean()
    
    return df

def add_change_rate_features(df: pd.DataFrame) -> pd.DataFrame:
    """Change rates"""
    df["pm2_5_change_rate"] = df["pm2_5"].diff(24)
    df["aqi_change_24h"] = df["aqi"].diff(24)
    
    # Weather changes
    if "temp" in df.columns:
        df["temp_change_24h"] = df["temp"].diff(24)
    if "wind_speed" in df.columns:
        df["wind_change_24h"] = df["wind_speed"].diff(24)
    
    return df

def add_pollutant_ratio_features(df: pd.DataFrame) -> pd.DataFrame:
    """Pollutant ratios"""
    df["pm2_5_pm10_ratio"] = df["pm2_5"] / (df["pm10"] + 1)
    df["co_no2_ratio"] = df["co"] / (df["no2"] + 1)
    return df

def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """All derived features"""
    df = add_weather_features(df)
    df = add_change_rate_features(df)
    df = add_pollutant_ratio_features(df)
    return df

def create_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Create daily targets"""
    df["target_t1"] = df["pm2_5"].shift(-24)  # Tomorrow
    df["target_t2"] = df["pm2_5"].shift(-48)  # Day after
    df["target_t3"] = df["pm2_5"].shift(-72)  # 3rd day
    return df