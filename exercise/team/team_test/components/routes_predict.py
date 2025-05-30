from fastapi import APIRouter
from pydantic import BaseModel
import numpy as np
from model_loader import load_model

router = APIRouter()
model = load_model()

class InputData(BaseModel):
    temp: float
    humidity: float
    wind: float

@router.post("/predict")
def predict(data: InputData):
    x = np.array([[data.temp, data.humidity, data.wind]])
    pred = model.predict(x)[0]
    risk = ['낮음', '보통', '높음', '위험'][pred]
    return {"risk": risk}
