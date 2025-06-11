from sklearn.metrics import classification_report
import pandas as pd
import pickle

df = pd.read_csv('fire_test.csv')
X, y = df[['temp', 'humidity', 'wind']], df['risk_level']

model = pickle.load(open('models/fire_model_latest.pkl', 'rb'))
y_pred = model.predict(X)

print(classification_report(y, y_pred, digits=3))
