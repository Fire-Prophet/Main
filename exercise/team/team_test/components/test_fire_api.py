import requests

data = {
    "temp": 29,
    "humidity": 30,
    "wind": 4
}

res = requests.post("http://localhost:8000/predict", json=data)
print(res.json())  # 예: {"risk": "높음"}
