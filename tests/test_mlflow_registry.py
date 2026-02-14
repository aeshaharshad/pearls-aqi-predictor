import dagshub
import mlflow

# Initialize DagsHub + MLflow
dagshub.init(
    repo_owner="aaa2633522",
    repo_name="pearls-aqi-predictor",
    mlflow=True
)

# Load production model using alias
model = mlflow.sklearn.load_model(
    "models:/aqi_t_plus_1@production"
)

print("✅ Model loaded successfully")
print("Model type:", type(model))
