import pandas as pd
import pickle
import pymysql

conn = pymysql.connect(host='localhost', user='user', password='pw', db='fire_db')
df = pd.read_sql('SELECT temp, humidity, wind FROM predictions WHERE risk IS NULL', conn)

model = pickle.load(open('models/fire_model_latest.pkl', 'rb'))
df['risk'] = model.predict(df[['temp', 'humidity', 'wind']])

# Optional: DB에 저장 로직 추가
