import pickle
import numpy as np

with open('fire_model.pkl', 'rb') as f:
    model = pickle.load(f)

x = np.array([[31, 25, 5]])
print("예측 위험도:", model.predict(x)[0])
