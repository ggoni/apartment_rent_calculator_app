from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import uvicorn
import logging
import numpy as np
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Apartment Rent Predictor API")

# Load models in a try-except block
try:
    model = joblib.load('rent_model.joblib')
    conformal_model = joblib.load('conformal_model.joblib')
    le_floor = joblib.load('le_floor.joblib')
    le_style = joblib.load('le_style.joblib')
    logger.info("Models loaded successfully")
except Exception as e:
    logger.error(f"Error loading models: {str(e)}")
    raise

class ApartmentFeatures(BaseModel):
    rooms: int = Field(..., ge=1, le=5, description="Number of rooms (1-5)")
    bathrooms: int = Field(..., ge=1, le=3, description="Number of bathrooms (1-3)")
    total_surface: float = Field(..., ge=30, le=200, description="Total surface in square meters (30-200)")
    building_age: int = Field(..., ge=0, le=50, description="Building age in years (0-50)")
    floor_material: str = Field(..., description="Type of floor material")
    style: str = Field(..., description="Architectural style")

    class Config:
        json_schema_extra = {
            "example": {
                "rooms": 2,
                "bathrooms": 1,
                "total_surface": 80,
                "building_age": 10,
                "floor_material": "Hardwood",
                "style": "Modern"
            }
        }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Apartment Rent Predictor API",
        "endpoints": {
            "/predict": "POST - Predict rent based on apartment features",
            "/info": "GET - Get model information and valid feature values"
        }
    }

@app.post("/predict")
async def predict_rent(features: ApartmentFeatures):
    """Predict rent based on apartment features with confidence intervals"""
    try:
        # Validate categorical features
        if features.floor_material not in le_floor.classes_:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid floor_material. Valid values are: {le_floor.classes_.tolist()}"
            )
        if features.style not in le_style.classes_:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid style. Valid values are: {le_style.classes_.tolist()}"
            )

        # Transform categorical features
        floor_encoded = le_floor.transform([features.floor_material])[0]
        style_encoded = le_style.transform([features.style])[0]
        
        # Prepare features for prediction
        features_array = [[
            features.rooms,
            features.bathrooms,
            features.total_surface,
            features.building_age,
            floor_encoded,
            style_encoded
        ]]
        
        # Make prediction with confidence intervals
        prediction, prediction_intervals = conformal_model.predict(
            features_array, alpha=0.05
        )
        
        return {
            "predicted_rent": round(float(prediction[0]), 2),
            "confidence_interval": {
                "lower": round(float(prediction_intervals[0, 0, 0]), 2),
                "upper": round(float(prediction_intervals[0, 1, 0]), 2)
            },
            "confidence_level": "95%",
            "currency": "USD",
            "features": features.model_dump()  # Updated from dict() to model_dump()
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/info")
async def model_info():
    """Get model information and valid feature values"""
    return {
        "model_type": "RandomForestRegressor",
        "features": {
            "rooms": {"min": 1, "max": 5},
            "bathrooms": {"min": 1, "max": 3},
            "total_surface": {"min": 30, "max": 200},
            "building_age": {"min": 0, "max": 50},
            "floor_materials": le_floor.classes_.tolist(),
            "styles": le_style.classes_.tolist()
        }
    }

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
