import sys
import os
from pathlib import Path

# Ensure project root is on sys.path when running this test as a script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


from src.utils.data_loader import load_data
from src.preprocessing.preprocess import clean_data

df = load_data()
cleaned = clean_data(df)

print("Before:", df.shape)
print("After:", cleaned.shape)
print(cleaned[["timestamp", "lat", "lon"]].isna().sum())
