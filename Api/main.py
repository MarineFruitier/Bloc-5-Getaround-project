import uvicorn
import pandas as pd
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import joblib
import numpy as np

description = """
Welcome to the Getaround pricing optimizer API   

## Why using this API

The goal of the machine learning endpoint is to predict the price for a car rental depending of differents Keys. 

How is working the endpoint : 

* `/predict` which accepts this format ✅  

    { "model_key": string among this list : ['Citroën', 'Renault', 'BMW', 'Peugeot', 'Audi', 'Nissan', 'Mitsubishi', 'Mercedes', 'Volkswagen', 'Toyota', 'SEAT', 'Subaru', 'PGO', 'Opel', 'Ferrari', 'Maserati'],  
    "mileage": integer,  
    "engine_power": integer,  
    "fuel": string among this list : ['diesel', 'petrol', 'hybrid_petrol'],  
    "paint_color": string among this list : ['black', 'grey', 'blue', 'white', 'brown', 'silver', 'red', 'beige', 'green', 'orange'],  
    "car_type": string among this list : ['estate', 'sedan', 'suv', 'hatchback', 'subcompact', 'coupe', 'convertible', 'van'],  
    "private_parking_available": boolean,  
    "has_gps": boolean,  
    "has_air_conditioning": boolean,  
    "automatic_car": boolean,  
    "has_getaround_connect": boolean,  
    "has_speed_regulator": boolean,  
    "winter_tires": boolean }  

"""

tags_metadata = [
    {
        "name": "Endpoints",
        "description": "Make your prediction."
    }
]

app = FastAPI(
    title="🚗 Getaround pricing : API",
    description=description,
    version="0.1",
    openapi_tags=tags_metadata
)


class FormFeatures(BaseModel):
    model_key: str
    mileage: int
    engine_power: int
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Welcome to the Getaround Pricing Optimizer API</title>
        <style>
            
            h1 {
                color: purple !important;
            }
            
            .swagger-ui .topbar-wrapper .topbar h1 {
                color: purple !important;
            }
        </style>
    </head>
    <body>
        <h1>🚗 Getaround Pricing Optimizer</h1>
        <p>Welcome to the Getaround Pricing Optimizer API. You can use <strong>/predict</strong> endpoint to make predictions.</p>
        <p>If you want to know how to use the API, you can check <a href="/docs">documentation</a>.</p>
        <p> Thank you for your visit</p>
    </body>
    </html>
    """


@app.post("/prediction", tags=["Machine_Learning"])
async def predict(formFeatures: FormFeatures):
    """
    Enter your car's features here  
    """
    
    features_list = ['model_key', 'mileage', 'engine_power', 'fuel', 'paint_color', 'car_type', 'private_parking_available', 'has_gps', 'has_air_conditioning', 'automatic_car', 'has_getaround_connect', 'has_speed_regulator', 'winter_tires', 'mileage_inverse']
    features_values = [formFeatures.model_key, formFeatures.mileage, formFeatures.engine_power, formFeatures.fuel, formFeatures.paint_color, formFeatures.car_type, formFeatures.private_parking_available, formFeatures.has_gps, formFeatures.has_air_conditioning, formFeatures.automatic_car, formFeatures.has_getaround_connect, formFeatures.has_speed_regulator, formFeatures.winter_tires, 1/formFeatures.mileage]
    X_topredict = pd.DataFrame([features_values], columns=features_list)
    
    list_bool = ['private_parking_available', 'has_gps', 'has_air_conditioning', 'automatic_car', 'has_getaround_connect', 'has_speed_regulator', 'winter_tires']
    for item in list_bool :
        X_topredict[item] = X_topredict[item].map({'True': True, 'False': False}) 
    
    # Load model
    loaded_model = joblib.load('final_model.joblib')
    
    # Prediction
    prediction = loaded_model.predict(X_topredict)
    response = {"prediction": prediction.tolist()}

    return response

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)
