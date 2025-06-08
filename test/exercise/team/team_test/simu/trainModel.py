import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os
from datetime import datetime

df = pd.read_csv('fire_data.csv')
X, y = df[['temp', 'humidity', 'wind']], df['risk_level']

model = RandomForestClassifier()
model.fit(X, y)

version = datetime.now().strftime('%Y%m%d_%H%M')
with open(f'models/fire_model_{version}.pkl', 'wb') as f:
    pickle.dump(model, f)
