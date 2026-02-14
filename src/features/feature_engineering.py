import pandas as pd


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add time-based features from timestamp"""
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day
    df["month"] = df["timestamp"].dt.month
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    return df


def add_lag_features(df: pd.DataFrame, target="aqi"):
    """Add lagged features for time-series modeling"""
    for lag in range(1, 7):
        df[f"{target}_lag{lag}"] = df[target].shift(lag)
    return df


def create_targets(df: pd.DataFrame):
    df["target_t1"] = df["pm2_5"].shift(-1)
    df["target_t2"] = df["pm2_5"].shift(-2)
    df["target_t3"] = df["pm2_5"].shift(-3)
    return df



def add_rolling_features(df: pd.DataFrame):
    """Add rolling statistics features"""
    df["aqi_roll3"] = df["aqi"].rolling(3).mean()
    df["aqi_roll6"] = df["aqi"].rolling(6).mean()
    df["aqi_std3"] = df["aqi"].rolling(3).std()
    df["aqi_roll3_max"] = df["aqi"].rolling(3).max()
    df["aqi_roll6_max"] = df["aqi"].rolling(6).max()
    return df


def add_change_rate_features(df: pd.DataFrame):
    """Add AQI change rate and derived features"""
    # AQI change rate (1-hour difference)
    df["aqi_change_rate_1h"] = df["aqi"].diff(1)
    
    # AQI change rate (3-hour difference)
    df["aqi_change_rate_3h"] = df["aqi"].diff(3)
    
    # AQI change rate (6-hour difference)
    df["aqi_change_rate_6h"] = df["aqi"].diff(6)
    
    # Rate of change of PM2.5 (most important pollutant)
    df["pm2_5_change_rate"] = df["pm2_5"].diff(1)
    
    # Rate of change of PM10
    df["pm10_change_rate"] = df["pm10"].diff(1)
    
    # Volatility: standard deviation of change rates (3-hour window)
    df["aqi_volatility_3h"] = df["aqi_change_rate_1h"].rolling(3).std()
    
    # Momentum: acceleration (2nd derivative)
    df["aqi_momentum"] = df["aqi_change_rate_1h"].diff(1)
    
    return df


def add_pollutant_ratio_features(df: pd.DataFrame):
    """Add pollutant ratio features"""
    # Ratios indicate pollution composition
    df["pm2_5_pm10_ratio"] = df["pm2_5"] / (df["pm10"] + 1)  # +1 to avoid division by zero
    df["co_no2_ratio"] = df["co"] / (df["no2"] + 1)
    df["o3_no2_ratio"] = df["o3"] / (df["no2"] + 1)
    
    return df


def add_derived_features(df: pd.DataFrame):
    """Add all derived features at once"""
    df = add_change_rate_features(df)
    df = add_pollutant_ratio_features(df)
    return df
