import dagshub
import mlflow

dagshub.init(
    repo_owner="aaa2633522",
    repo_name="pearls-aqi-predictor",
    mlflow=True
)

def load_production_model(model_name):
    model_uri = f"models:/{model_name}@production"
    return mlflow.sklearn.load_model(model_uri)

model_t1 = load_production_model("aqi_t_plus_1")
model_t2 = load_production_model("aqi_t_plus_2")
model_t3 = load_production_model("aqi_t_plus_3")
