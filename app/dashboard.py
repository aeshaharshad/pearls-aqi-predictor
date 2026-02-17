# app/dashboard.py

import os
import pandas as pd
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import plotly.graph_objects as go
from datetime import datetime

load_dotenv()

# Page config
st.set_page_config(
    page_title="AQI Forecast - Karachi", 
    layout="wide", 
    page_icon="🌫️",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #f5f7fa;}
    .stAlert {border-radius: 10px;}
    h1 {color: #1f2937;}
    h3 {color: #374151;}
</style>
""", unsafe_allow_html=True)

# MongoDB
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

# AQI Functions
def pm25_to_aqi(pm25):
    """Convert PM2.5 to AQI"""
    if pm25 <= 12.0:
        return int((50 - 0) / (12.0 - 0.0) * (pm25 - 0.0) + 0)
    elif pm25 <= 35.4:
        return int((100 - 51) / (35.4 - 12.1) * (pm25 - 12.1) + 51)
    elif pm25 <= 55.4:
        return int((150 - 101) / (55.4 - 35.5) * (pm25 - 35.5) + 101)
    elif pm25 <= 150.4:
        return int((200 - 151) / (150.4 - 55.5) * (pm25 - 55.5) + 151)
    elif pm25 <= 250.4:
        return int((300 - 201) / (250.4 - 150.5) * (pm25 - 150.5) + 201)
    else:
        return int((500 - 301) / (500.4 - 250.5) * (pm25 - 250.5) + 301)

def get_aqi_color(aqi):
    """Get color for AQI level"""
    if aqi <= 50: return "#00e400"
    elif aqi <= 100: return "#ffff00"
    elif aqi <= 150: return "#ff7e00"
    elif aqi <= 200: return "#ff0000"
    elif aqi <= 300: return "#8f3f97"
    else: return "#7e0023"

def get_health_message(aqi):
    """Get health advice"""
    if aqi <= 50:
        return "😊 **Excellent!** Perfect for all outdoor activities."
    elif aqi <= 100:
        return "🙂 **Good!** Air quality acceptable for most people."
    elif aqi <= 150:
        return "😐 **Moderate.** Sensitive individuals should limit prolonged outdoor exertion."
    elif aqi <= 200:
        return "😷 **Unhealthy!** Everyone may begin to experience health effects. Reduce outdoor activities."
    elif aqi <= 300:
        return "⚠️ **Very Unhealthy!** Health alert. Avoid outdoor activities."
    else:
        return "🚨 **HAZARDOUS!** Emergency conditions. Stay indoors with air purifiers."

# Header
st.title("🌫️ Karachi AQI 3-Day Forecast")
st.caption("Real-time Air Quality Predictions | Updated Hourly")

# Load current AQI
try:
    current_data = list(feature_collection.find().sort("timestamp", -1).limit(1))
    if current_data:
        current_aqi = current_data[0].get('aqi', 0)
        current_pm25 = current_data[0].get('pm2_5', 0)
        current_time = current_data[0].get('timestamp', datetime.utcnow())
    else:
        current_aqi = 0
        current_pm25 = 0
        current_time = datetime.utcnow()
except:
    current_aqi = 0
    current_pm25 = 0
    current_time = datetime.utcnow()

# Load predictions
data = list(prediction_collection.find().sort("timestamp", -1).limit(48))

if not data:
    st.warning("⚠️ No forecast data available yet. Please check back soon.")
    st.info("💡 The system generates predictions automatically. First predictions may take a few hours.")
    st.stop()

df = pd.json_normalize(data)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

# Extract forecasts
df["t1_pm25"] = df["forecasts.t_plus_1.pm25_prediction"]
df["t2_pm25"] = df["forecasts.t_plus_2.pm25_prediction"]
df["t3_pm25"] = df["forecasts.t_plus_3.pm25_prediction"]
df["t1_label"] = df["forecasts.t_plus_1.aqi_category_label"]
df["t2_label"] = df["forecasts.t_plus_2.aqi_category_label"]
df["t3_label"] = df["forecasts.t_plus_3.aqi_category_label"]

latest = df.iloc[-1]

# Current AQI Banner
current_aqi_color = get_aqi_color(current_aqi)
st.markdown(f"""
<div style="padding: 20px; border-radius: 15px; background: linear-gradient(135deg, {current_aqi_color}30 0%, {current_aqi_color}10 100%); border-left: 5px solid {current_aqi_color}; margin-bottom: 20px;">
    <h2 style="margin: 0; color: #1f2937;">Current AQI: <span style="color: {current_aqi_color};">{current_aqi}</span></h2>
    <p style="margin: 5px 0 0 0; font-size: 16px; color: #6b7280;">PM2.5: {current_pm25:.1f} µg/m³ • Last updated: {pd.to_datetime(current_time).strftime('%H:%M %p')}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 📅 3-Day Forecast")

# Forecast Cards
col1, col2, col3 = st.columns(3)

# T+1
t1_pm25 = latest['t1_pm25']
t1_aqi = pm25_to_aqi(t1_pm25)
t1_color = get_aqi_color(t1_aqi)

with col1:
    st.markdown(f"""
    <div style="padding: 25px; border-radius: 15px; background-color: {t1_color}15; border: 2px solid {t1_color}40; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3 style="margin: 0; color: #374151;">Tomorrow</h3>
        <h1 style="margin: 10px 0; color: {t1_color}; font-size: 48px;">{t1_aqi}</h1>
        <p style="font-size: 20px; font-weight: 600; margin: 5px 0; color: #1f2937;">{latest['t1_label']}</p>
        <p style="font-size: 14px; color: #6b7280; margin: 5px 0;">PM2.5: {t1_pm25:.1f} µg/m³</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(get_health_message(t1_aqi))

# T+2
t2_pm25 = latest['t2_pm25']
t2_aqi = pm25_to_aqi(t2_pm25)
t2_color = get_aqi_color(t2_aqi)

with col2:
    st.markdown(f"""
    <div style="padding: 25px; border-radius: 15px; background-color: {t2_color}15; border: 2px solid {t2_color}40; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3 style="margin: 0; color: #374151;">Day After</h3>
        <h1 style="margin: 10px 0; color: {t2_color}; font-size: 48px;">{t2_aqi}</h1>
        <p style="font-size: 20px; font-weight: 600; margin: 5px 0; color: #1f2937;">{latest['t2_label']}</p>
        <p style="font-size: 14px; color: #6b7280; margin: 5px 0;">PM2.5: {t2_pm25:.1f} µg/m³</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(get_health_message(t2_aqi))

# T+3
t3_pm25 = latest['t3_pm25']
t3_aqi = pm25_to_aqi(t3_pm25)
t3_color = get_aqi_color(t3_aqi)

with col3:
    st.markdown(f"""
    <div style="padding: 25px; border-radius: 15px; background-color: {t3_color}15; border: 2px solid {t3_color}40; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h3 style="margin: 0; color: #374151;">Third Day</h3>
        <h1 style="margin: 10px 0; color: {t3_color}; font-size: 48px;">{t3_aqi}</h1>
        <p style="font-size: 20px; font-weight: 600; margin: 5px 0; color: #1f2937;">{latest['t3_label']}</p>
        <p style="font-size: 14px; color: #6b7280; margin: 5px 0;">PM2.5: {t3_pm25:.1f} µg/m³</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(get_health_message(t3_aqi))

st.divider()

# Trend Chart
st.subheader("📈 AQI Forecast Trend")

df["t1_pm25"] = df["t1_pm25"].fillna(0)
df["t1_aqi"] = df["t1_pm25"].apply(pm25_to_aqi)
df["t2_pm25"] = df["t2_pm25"].fillna(0)
df["t2_aqi"] = df["t2_pm25"].apply(pm25_to_aqi)
df["t3_pm25"] = df["t3_pm25"].fillna(0)
df["t3_aqi"] = df["t3_pm25"].apply(pm25_to_aqi)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df["timestamp"], y=df["t1_aqi"],
    mode='lines+markers', name='Tomorrow',
    line=dict(color='#3b82f6', width=3),
    marker=dict(size=8)
))

fig.add_trace(go.Scatter(
    x=df["timestamp"], y=df["t2_aqi"],
    mode='lines+markers', name='Day After',
    line=dict(color='#8b5cf6', width=3),
    marker=dict(size=8)
))

fig.add_trace(go.Scatter(
    x=df["timestamp"], y=df["t3_aqi"],
    mode='lines+markers', name='Third Day',
    line=dict(color='#ec4899', width=3),
    marker=dict(size=8)
))

# AQI threshold lines
fig.add_hline(y=50, line_dash="dash", line_color="green", opacity=0.5, annotation_text="Good", annotation_position="right")
fig.add_hline(y=100, line_dash="dash", line_color="yellow", opacity=0.5, annotation_text="Moderate")
fig.add_hline(y=150, line_dash="dash", line_color="orange", opacity=0.5, annotation_text="Unhealthy (Sensitive)")
fig.add_hline(y=200, line_dash="dash", line_color="red", opacity=0.5, annotation_text="Unhealthy")

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="AQI",
    hovermode='x unified',
    height=450,
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(family="Arial", size=12)
)

st.plotly_chart(fig, use_container_width=True)

# AQI Reference
with st.expander("ℹ️ Understanding AQI Levels"):
    st.markdown("""
    | AQI | Level | Color | Health Impact |
    |-----|-------|-------|---------------|
    | 0-50 | Good | 🟢 Green | Air quality is satisfactory |
    | 51-100 | Moderate | 🟡 Yellow | Acceptable for most people |
    | 101-150 | Unhealthy for Sensitive | 🟠 Orange | Sensitive groups may experience effects |
    | 151-200 | Unhealthy | 🔴 Red | Everyone may experience health effects |
    | 201-300 | Very Unhealthy | 🟣 Purple | Health alert for everyone |
    | 301-500 | Hazardous | 🟤 Maroon | Emergency conditions |
    
    **Sensitive Groups:** Children, elderly, people with asthma or heart disease
    """)

# Footer
st.divider()
st.caption("💡 Data Source: OpenWeather API | Predictions: ML Models (Random Forest, Gradient Boosting)")
st.caption(f"🔄 Last forecast: {latest['timestamp'].strftime('%Y-%m-%d %H:%M UTC')}")