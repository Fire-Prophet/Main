# 5_api_predict.py

from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

with open('fire_model.pkl', 'rb') as f:
    model = pickle.load(f)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    features = np.array([[data['temp'], data['humidity'], data['wind']]])
    pred = model.predict(features)[0]
    labels = ['낮음', '보통', '높음', '위험']
    return jsonify({ 'risk': labels[pred] })

if __name__ == '__main__':
    app.run(debug=True)
