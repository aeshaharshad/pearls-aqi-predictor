import sys
import os
from pathlib import Path

# Ensure project root is on sys.path when running this test as a script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.data_loader import load_data

df = load_data()

print("Shape:", df.shape)
print(df.head())
