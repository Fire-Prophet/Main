# 2_train_model.py

import pandas as pd
from sklearn.linear_model import LogisticRegression
import pickle

df = pd.read_csv('fire_data.csv')

X = df[['temp', 'humidity', 'wind']]
y = df['risk_level']

model = LogisticRegression(max_iter=300)
model.fit(X, y)

# 모델 저장
with open('fire_model.pkl', 'wb') as f:
    pickle.dump(model, f)
