import requests

url = 'http://localhost:5000/predict'
data = {
    "temp": 29,
    "humidity": 30,
    "wind": 4
}

response = requests.post(url, json=data)
print(response.json())  # 예: {'risk': '높음'}
