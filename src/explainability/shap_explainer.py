import shap


def explain_model(model, X_sample):
    explainer = shap.Explainer(model)
    shap_values = explainer(X_sample)

    shap.summary_plot(shap_values, X_sample)
