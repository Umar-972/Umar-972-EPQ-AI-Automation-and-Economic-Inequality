
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="Open-Meteo Weather API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
session = requests.Session()

@app.get('/weather')
def weather(city: str):
    geo = session.get(GEOCODE_URL, params={"name": city, "count": 1}, timeout=10)
    geo.raise_for_status()
    data = geo.json()

    if not data.get('results'):
        return {'error': 'City not found'}

    loc = data['results'][0]

    weather = session.get(
        WEATHER_URL,
        params={
            'latitude': loc['latitude'],
            'longitude': loc['longitude'],
            'current': 'temperature_2m,relative_humidity_2m,wind_speed_10m',
            'hourly': 'temperature_2m',
            'forecast_days': 2
        },
        timeout=10
    )
    weather.raise_for_status()

    return {
        'city': loc['name'],
        'country': loc.get('country'),
        'weather': weather.json()
    }
