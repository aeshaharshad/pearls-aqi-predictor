import joblib
import os

models = os.listdir("models")
print("Models found:", models)

model = joblib.load(os.path.join("models", models[0]))
print("Model loaded:", type(model))
