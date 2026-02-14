import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw AQI dataset
    """

    # Drop bad records and ensure we have a writable copy
    df = df.dropna(subset=["timestamp", "lat", "lon"]).copy()

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Sort by time
    df = df.sort_values("timestamp")

    # Remove duplicates
    df = df.drop_duplicates(subset=["timestamp"])

    return df
