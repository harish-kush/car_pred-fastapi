from fastapi import FastAPI
from fastapi.responses import JSONResponse
from schema import Car_Features, PredictionResponse
from model import load_artifacts,predict_price
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later you can restrict to your streamlit domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    load_artifacts()


@app.get("/")
def test():
    return JSONResponse(status_code=200, content={"message": "this is test route"})


@app.post("/predict",response_model=PredictionResponse)
def predict(features: Car_Features):
    price = predict_price(features.model_dump())
    return PredictionResponse(prediction_price=price)
