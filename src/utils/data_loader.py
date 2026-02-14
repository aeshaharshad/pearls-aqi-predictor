import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv


def load_data():
    load_dotenv()

    MONGO_URI = os.getenv("MONGODB_URI")
    DB_NAME = os.getenv("MONGODB_DB")
    COLLECTION = os.getenv("MONGODB_COLLECTION")

    client = MongoClient(MONGO_URI)
    df = pd.DataFrame(list(client[DB_NAME][COLLECTION].find()))

    return df
