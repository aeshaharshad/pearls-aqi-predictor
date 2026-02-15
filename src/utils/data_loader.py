import os
import pandas as pd
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB", "aqi_db")
COLLECTION = os.getenv("MONGODB_COLLECTION", "aqi_features")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not set")

client = MongoClient(MONGODB_URI)
collection = client[DB_NAME][COLLECTION]

def load_data():
    return pd.DataFrame(list(collection.find()))
