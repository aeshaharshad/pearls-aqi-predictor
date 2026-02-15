import os
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

# Load env vars for defaults; actual connection is lazy
load_dotenv()

DEFAULT_DB = os.getenv("MONGODB_DB", "aqi_db")
DEFAULT_COLLECTION = os.getenv("MONGODB_COLLECTION", "aqi_features")


def get_mongo_uri() -> Optional[str]:
    return os.getenv("MONGODB_URI")


def get_client(uri: Optional[str] = None) -> MongoClient:
    """Return a MongoClient. Raises ValueError if URI is not set."""
    uri = uri or get_mongo_uri()
    if not uri:
        raise ValueError("MONGODB_URI is not set")
    # Ensure a trusted CA bundle is provided for TLS connections (helps in CI)
    return MongoClient(uri, tlsCAFile=certifi.where())


def load_data(
    client: Optional[MongoClient] = None,
    feature_db: Optional[str] = None,
    feature_collection: Optional[str] = None,
) -> pd.DataFrame:
    """Load feature data from MongoDB into a pandas DataFrame.

    Parameters are optional; when omitted the function uses environment defaults.
    This function does not import other modules to avoid circular imports.
    """
    if client is None:
        client = get_client()

    feature_db = feature_db or os.getenv("MONGODB_FEATURE_DB", DEFAULT_DB)
    feature_collection = (
        feature_collection or os.getenv("MONGODB_FEATURE_COLLECTION", DEFAULT_COLLECTION)
    )

    coll = client[feature_db][feature_collection]
    return pd.DataFrame(list(coll.find()))
