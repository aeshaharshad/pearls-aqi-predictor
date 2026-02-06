import os

PROJECT_STRUCTURE = [
    "data/raw",
    "data/processed",

    "notebooks",

    "src/config",
    "src/ingestion",
    "src/features",
    "src/training",
    "src/prediction",
    "src/explainability",
    "src/utils",
    "src/app",

    ".github/workflows"
]

FILES = [
    "src/config/config.yaml",

    "src/ingestion/fetch_data.py",

    "src/features/feature_pipeline.py",

    "src/training/train.py",
    "src/training/evaluate.py",
    "src/training/register_model.py",

    "src/prediction/predict.py",
    "src/prediction/forecast.py",

    "src/explainability/shap_explainer.py",

    "src/utils/logger.py",
    "src/utils/helpers.py",

    "src/app/api.py",
    "src/app/dashboard.py",

    "requirements.txt",
    "README.md",
    ".env"
]

def create_structure():
    for folder in PROJECT_STRUCTURE:
        os.makedirs(folder, exist_ok=True)

    for file in FILES:
        if not os.path.exists(file):
            with open(file, "w") as f:
                pass

    print("✅ Project structure created successfully")

if __name__ == "__main__":
    create_structure()
