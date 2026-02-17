# app/dashboard.py

import os
import pandas as pd
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

load_dotenv()

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="AQI Forecast - Karachi",
    layout="wide",
    page_icon="🌫️",
    initial_sidebar_state="collapsed"
)

# -------------------- STYLE --------------------
st.markdown("""
<style>
.main {background-color: #f5f7fa;}
.stAlert {border-radius: 10px;}
h1 {color: #1f2937;}
h3 {color: #374151;}
</style>
""", unsafe_allow_html=True)

# -------------------- DATABASE --------------------
MONGODB_URI = os.getenv("MONGODB_URI")
PREDICTION_DB = os.getenv("MONGODB_PREDICTION_DB", "aqi_db")
PREDICTION_COLLECTION = os.getenv("MONGODB_PREDICTION_COLLECTION", "predictions")
FEATURE_DB = os.getenv("MONGODB_FEATURE_DB", "aqi_db")
FEATURE_COLLECTION = os.getenv("MONGODB_FEATURE_COLLECTION", "aqi_features")

try:
    client = MongoClient(MONGODB_URI, tlsInsecure=True, serverSelectionTimeoutMS=5000)
    prediction_collection = client[PREDICTION_DB][PREDICTION_COLLECTION]
    feature_collection = client[FEATURE_DB][FEATURE_COLLECTION]
except Exception as e:
    st.error(f"❌ Database connection failed: {e}")
    st.stop()

# -------------------- AQI FUNCTION (ABSOLUTELY SAFE) --------------------
def pm25_to_aqi(pm25):
    try:
        pm25 = float(pm25)

        # HARD BLOCK NaN / inf
        if not np.isfinite(pm25) or pm25 < 0:
            return 0

        if pm25 <= 12.0:
            aqi = 50 * pm25 / 12.0
        elif pm25 <= 35.4:
            aqi = ((100 - 51) / (35.4 - 12.1)) * (pm25 - 12.1) + 51
        elif pm25 <= 55.4:
            aqi = ((150 - 101) / (55.4 - 35.5)) * (pm25 - 35.5) + 101
        elif pm25 <= 150.4:
            aqi = ((200 - 151) / (150.4 - 55.5)) * (pm25 - 55.5) + 151
        elif pm25 <= 250.4:
            aqi = ((300 - 201) / (250.4 - 150.5)) * (pm25 - 150.5) + 201
        else:
            aqi = ((500 - 301) / (500.4 - 250.5)) * (pm25 - 250.5) + 301

        if not np.isfinite(aqi):
            return 0

        return int(round(aqi))

    except Exception:
        return 0

# -------------------- UI HELPERS --------------------
def get_aqi_color(aqi):
    if aqi <= 50: return "#00e400"
    elif aqi <= 100: return "#ffff00"
    elif aqi <= 150: return "#ff7e00"
    elif aqi <= 200: return "#ff0000"
    elif aqi <= 300: return "#8f3f97"
    else: return "#7e0023"

def get_health_message(aqi):
    if aqi <= 50:
        return "😊 Excellent air quality."
    elif aqi <= 100:
        return "🙂 Acceptable air quality."
    elif aqi <= 150:
        return "😐 Sensitive groups be cautious."
    elif aqi <= 200:
        return "😷 Unhealthy air."
    elif aqi <= 300:
        return "⚠️ Very unhealthy."
    else:
        return "🚨 Hazardous air quality."

# -------------------- HEADER --------------------
st.title("🌫️ Karachi AQI 3-Day Forecast")

# -------------------- CURRENT AQI --------------------
current = list(feature_collection.find().sort("timestamp", -1).limit(1))
current = current[0] if current else {}

current_aqi = int(current.get("aqi", 0))
current_pm25 = float(current.get("pm2_5", 0))
current_time = current.get("timestamp", datetime.utcnow())

# -------------------- LOAD PREDICTIONS --------------------
data = list(prediction_collection.find().sort("timestamp", -1).limit(48))
if not data:
    st.warning("No forecast data yet.")
    st.stop()

df = pd.json_normalize(data)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

df["t1_pm25"] = pd.to_numeric(df["forecasts.t_plus_1.pm25_prediction"], errors="coerce")
df["t2_pm25"] = pd.to_numeric(df["forecasts.t_plus_2.pm25_prediction"], errors="coerce")
df["t3_pm25"] = pd.to_numeric(df["forecasts.t_plus_3.pm25_prediction"], errors="coerce")

df = df.fillna(0)

df["t1_aqi"] = df["t1_pm25"].apply(pm25_to_aqi)
df["t2_aqi"] = df["t2_pm25"].apply(pm25_to_aqi)
df["t3_aqi"] = df["t3_pm25"].apply(pm25_to_aqi)

# -------------------- DONE --------------------
st.success("✅ Dashboard loaded safely — no NaN crashes")
