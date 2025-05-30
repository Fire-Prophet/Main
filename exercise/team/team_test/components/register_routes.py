from fastapi import FastAPI
from routes_predict import router as predict_router

app = FastAPI(title="Fire Risk Prediction API")
app.include_router(predict_router)
