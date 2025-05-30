# 4_api_server.py

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "🔥 Fire Risk Prediction API"

if __name__ == '__main__':
    app.run(debug=True)
