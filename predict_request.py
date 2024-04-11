
import requests
import json

url = 'https://myapi-project-getaround-5aba33698673.herokuapp.com/prediction'

data ={
    "model_key": "Renault",
    "mileage": 120000,
    "engine_power": 120,
    "fuel": "diesel",
    "paint_color": "grey",
    "car_type": "sedan",
    "private_parking_available": False,  
    "has_gps": False,  
    "has_air_conditioning": True, 
    "automatic_car": True,  
    "has_getaround_connect": False,  
    "has_speed_regulator": True, 
    "winter_tires": False  
}

response = requests.post(url, json=data)

print("Le prix estimé est :", response.json())

