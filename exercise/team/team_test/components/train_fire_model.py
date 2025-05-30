import pandas as pd
from sklearn.linear_model import LogisticRegression
import pickle

df = pd.read_csv('fire_data.csv')
X = df[['temp', 'humidity', 'wind']]
y = df['risk_level']

model = LogisticRegression(max_iter=300)
model.fit(X, y)

with open('fire_model.pkl', 'wb') as f:
    pickle.dump(model, f)
