# 3_load_model.py

import pickle
import numpy as np

with open('fire_model.pkl', 'rb') as f:
    model = pickle.load(f)

# 예측 테스트
sample = np.array([[31, 25, 5]])
prediction = model.predict(sample)[0]
print(f'예측 위험도: {prediction}')
