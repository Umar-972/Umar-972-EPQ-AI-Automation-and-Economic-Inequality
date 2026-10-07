import httpx
from fastapi import FastAPI, HTTPException, Query
from datetime import datetime
from typing import Dict, Any

app = FastAPI(title="Weather App Backend")

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Weather Backend is running."}

@app.get("/weather")
async def get_weather(city: str = Query(..., description="Name of the city to search")):
    """
    Geocodes city name and fetches current + 24h hourly forecast data from Open-Meteo.
    """
    async with httpx.AsyncClient(timeout=8.0) as client:
        # Step 1: Resolve city to lat/lon coordinates via Geocoding API
        geo_resp = await client.get(GEOCODING_URL, params={"name": city, "count": 1, "language": "en"})
        if geo_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error reaching geocoding service.")
        
        geo_data = geo_resp.json()
        if not geo_data.get("results"):
            raise HTTPException(status_code=404, detail=f"City '{city}' not found.")
        
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        city_name = location["name"]
        country = location.get("country", "")

        # Step 2: Query Open-Meteo Weather Forecast API
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
            "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            "timezone": "auto",
            "forecast_days": 2
        }
        
        forecast_resp = await client.get(FORECAST_URL, params=params)
        if forecast_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Error reaching weather service.")
            
        forecast_data = forecast_resp.json()
        
        # Step 3: Format current weather & next 24 hours of hourly data
        current = forecast_data.get("current_weather", {})
        hourly = forecast_data.get("hourly", {})
        
        # Take the next 24 hourly data points starting from now
        times = hourly.get("time", [])[:24]
        temps = hourly.get("temperature_2m", [])[:24]
        
        formatted_times = [
            datetime.fromisoformat(t).strftime("%H:%M") for t in times
        ]

        return {
            "city": f"{city_name}, {country}" if country else city_name,
            "latitude": lat,
            "longitude": lon,
            "current_temperature": current.get("temperature"),
            "windspeed": current.get("windspeed"),
            "weathercode": current.get("weathercode"),
            "hourly_times": formatted_times,
            "hourly_temps": temps
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)