import numpy as np
from .modelManager import load_model

def ensemble_predict(X):
    models = [
        load_model('models/model_v1.pkl'),
        load_model('models/model_v2.pkl')
    ]
    predictions = [m.predict(X)[0] for m in models]
    return round(np.mean(predictions))
