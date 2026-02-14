import os
import joblib
from datetime import datetime


def save_model(model, model_name: str):
    """
    Save model with timestamp versioning
    """

    os.makedirs("models", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"models/{model_name}_{timestamp}.pkl"

    joblib.dump(model, filename)

    print(f"✅ Model saved: {filename}")
