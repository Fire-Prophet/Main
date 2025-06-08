import shap
import pickle

def predict_and_explain(x):
    model = pickle.load(open('models/fire_model_latest.pkl', 'rb'))
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(x)
    return model.predict(x), shap_values
