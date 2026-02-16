from pydantic import BaseModel, Field
from enum import Enum

class FuelType(str, Enum):
    Petrol = "Petrol"
    Diesel = "Diesel"
    CNG = "CNG"

class SellerType(str, Enum):
    Dealer = "Dealer"
    Individual = "Individual"

class TransmissionType(str, Enum):
    Manual = "Manual"
    Automatic = "Automatic"


class Car_Features(BaseModel):
    Car_Name: str = Field(..., example="Defender")
    Year: int = Field(..., example=2020)
    Present_Price: float = Field(..., example=10.5)
    Kms_Driven: int = Field(..., example=27000)
    Fuel_Type: FuelType
    Seller_Type: SellerType
    Transmission: TransmissionType
    Owner: int = Field(..., ge=0, le=3, example=1)


class PredictionResponse(BaseModel):
    prediction_price: float
