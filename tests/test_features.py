
import sys
import os
from pathlib import Path

# Ensure project root is on sys.path when running this test as a script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.data_loader import load_data
from src.preprocessing.preprocess import clean_data
from src.features.feature_engineering import (
    add_time_features,
    add_lag_features,
    create_targets,
)

df = load_data()
df = clean_data(df)

df = add_time_features(df)
df = add_lag_features(df)
df = create_targets(df)

print(df.columns)
print(df.tail())
