import os
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# MongoDB config
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("MONGODB_DB")]
collection = db[os.getenv("MONGODB_COLLECTION")]


def load_dataset(city="Lahore"):
    cursor = collection.find(
        {"city": city},
        {"_id": 0}  # exclude MongoDB internal id
    )

    df = pd.DataFrame(list(cursor))
    if df.empty:
        raise ValueError("No data found in MongoDB")

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = load_dataset()
    print("Dataset shape:", df.shape)
    print(df.head())
