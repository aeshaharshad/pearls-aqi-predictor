# src/utils/data_loader.py

import os
import certifi
import pandas as pd
from pymongo import MongoClient

def get_client():
    """Create MongoDB client with proper TLS configuration"""
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("MONGODB_URI environment variable not set")
    
    # Explicit TLS configuration for MongoDB Atlas
    return MongoClient(
        uri,
        tls=True,
        tlsCAFile=certifi.where(),
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