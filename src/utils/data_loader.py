# src/utils/data_loader.py

import os
import pandas as pd
from pymongo import MongoClient

def get_client():
    """Create MongoDB client with fallback connection strategies"""
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("MONGODB_URI environment variable not set")
    
    # Try standard connection first
    try:
        return MongoClient(
            uri,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000
        )
    except Exception as e:
        print(f"⚠️ Standard connection failed: {e}")
        print("🔄 Retrying with tlsInsecure=True...")
        
        # Fallback to insecure TLS
        return MongoClient(
            uri,
            tlsInsecure=True,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000
        )

def load_data():
    """Load data from MongoDB feature collection"""
    client = get_client()
    
    db_name = os.getenv("MONGODB_FEATURE_DB", "aqi_db")
    collection_name = os.getenv("MONGODB_FEATURE_COLLECTION", "aqi_features")
    
    coll = client[db_name][collection_name]
    return pd.DataFrame(list(coll.find()))