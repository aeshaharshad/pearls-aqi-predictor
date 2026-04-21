# 🌍 PEARLS AQI PREDICTOR

**Production-Grade Multi-Day Air Quality Forecasting System (MLOps + ML)**

**🔗 Live Demo:** [https://pearls-aqi-predictor-de5j9si4ygaljzkxvpzxej.streamlit.app/](https://pearls-aqi-predictor-de5j9si4ygaljzkxvpzxej.streamlit.app/)

## Overview

A fully automated **MLOps pipeline** that predicts **Karachi’s AQI 1–3 days ahead** using time-series machine learning.

* Trained on **90 days of hourly AQI + weather data**
* Runs **automatically every hour (CI/CD via GitHub Actions)**
* Stores predictions in **MongoDB**
* Visualizes forecasts **live on Streamlit**

---

## 📊 Key Highlights

* **3 specialized models** (t+1, t+2, t+3 days)
* **42 engineered time-series features**
* **R² Scores:**

  * 1-day → **0.92**
  * 2-day → **0.88**
  * 3-day → **0.84**
* **Serverless architecture** (no VPS required)
* **End-to-end ML lifecycle implemented**

---

## 🧠 Problem & Objective

Air pollution directly impacts **public health, urban planning, and policy decisions**, yet most systems only provide *current* or *short-term* AQI.

### Objective:

Build a system that:

* Predicts AQI **1–3 days ahead**
* Runs **autonomously**
* Stores predictions **persistently**
* Displays results **in real time**

---

## 🏗️ System Architecture (End-to-End)

```
[1] Data Ingestion (API → MongoDB)
        ↓
[2] Preprocessing (cleaning, validation)
        ↓
[3] Feature Engineering (time-series features)
        ↓
[4] Model Training (MLflow tracking + registry)
        ↓
[5] Automated Inference (GitHub Actions - hourly)
        ↓
[6] Storage (MongoDB)
        ↓
[7] Visualization (Streamlit Dashboard)
```

---

## 🔬 Feature Engineering (Core Strength)

Designed specifically for **time-series AQI behavior**:

### ⏱️ Time Features

* Hour, day, month, weekday

### 🔁 Lag Features

* PM2.5 lagged (1–6 hours)

### 📉 Rolling Statistics

* Mean (3h, 6h), std deviation, max

### 📊 Derived Features

* PM2.5 / PM10 ratio
* Change rates
* AQI momentum & volatility

### 🎯 Targets

* **t+1 → 24h ahead**
* **t+2 → 48h ahead**
* **t+3 → 72h ahead**

---

## 🤖 Modeling Strategy (Key Differentiator)

Instead of one model predicting all horizons:

👉 **Separate models per horizon**

| Horizon | Best Model        |
| ------- | ----------------- |
| t+1     | Random Forest     |
| t+2     | Gradient Boosting |
| t+3     | Random Forest     |

### Why this matters:

* Reduces error propagation
* Improves long-range accuracy
* More stable than single-model approaches (e.g., naive LSTM setups)

---

## ⚙️ MLOps & Automation

### ✅ Experiment Tracking

* MLflow + DagsHub integration
* Logs metrics, parameters, artifacts
* Full reproducibility

### ✅ Model Registry

* Versioned models per horizon:

  * `aqi_t_plus_1`
  * `aqi_t_plus_2`
  * `aqi_t_plus_3`
* Supports **rollbacks & safe deployment**

### ✅ CI/CD Pipeline

* GitHub Actions runs **hourly**
* Steps:

  1. Load latest production models
  2. Generate features from new data
  3. Predict AQI
  4. Store results in MongoDB

---

## 🧩 Modular Architecture (Production-Level Design)

```
src/
├── ingestion/        → Data collection
├── preprocessing/    → Cleaning & validation
├── features/         → Feature engineering (shared)
├── training/         → Model training & tracking
├── inference/        → Predictions
└── utils/            → Shared components
```

### Why this matters:

* **No feature skew** → same feature code for training & inference
* **Independent deployment** → training ≠ inference ≠ dashboard
* **Easy debugging** → isolate issues quickly
* **Scalable** → can evolve into microservices

---

## 📈 Performance Metrics

| Horizon | RMSE       | R²   |
| ------- | ---------- | ---- |
| 24h     | 8.5 µg/m³  | 0.92 |
| 48h     | 12.3 µg/m³ | 0.88 |
| 72h     | 15.1 µg/m³ | 0.84 |

👉 Strong performance even at **72-hour forecasting horizon** (rare in AQI systems)

---

## 🚀 Deployment

* **Frontend:** Streamlit Cloud
* **Database:** MongoDB Atlas
* **Automation:** GitHub Actions
* **Cost:** ~minimal (serverless architecture)

---


