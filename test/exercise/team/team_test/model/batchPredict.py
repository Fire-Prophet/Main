import pandas as pd
from .modelManager import load_model

def batch_predict_csv(csv_path):
    df = pd.read_csv(csv_path)
    model = load_model('models/model_v1.pkl')
    df['prediction'] = model.predict(df[['temp', 'humidity', 'wind']])
    return df
