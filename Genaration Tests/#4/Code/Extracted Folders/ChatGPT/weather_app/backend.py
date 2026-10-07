"""
FastAPI backend for the Open-Meteo Weather App.

The backend keeps all Open-Meteo HTTP calls in one place, uses an async
HTTP client with connection pooling, and exposes a small JSON API to the GUI.
"""

from __future__ import annotations

import time
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

OPEN_METEO_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"

app = FastAPI(
    title="Modern Weather App API",
    version="1.0.0",
    description="Fast local API wrapper around Open-Meteo.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A small in-memory cache avoids repeated requests when users revisit a city.
_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 300

_CLIENT: httpx.AsyncClient | None = None


@app.on_event("startup")
async def startup() -> None:
    global _CLIENT
    _CLIENT = httpx.AsyncClient(
        timeout=httpx.Timeout(8.0, connect=3.0),
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
        http2=True,
        headers={"User-Agent": "ModernWeatherApp/1.0"},
    )


@app.on_event("shutdown")
async def shutdown() -> None:
    global _CLIENT
    if _CLIENT is not None:
        await _CLIENT.aclose()
        _CLIENT = None


async def _get(url: str, params: dict[str, Any]) -> dict[str, Any]:
    if _CLIENT is None:
        raise HTTPException(status_code=503, detail="Weather service is starting.")
    try:
        response = await _CLIENT.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="Open-Meteo request timed out.") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502, detail="Could not reach Open-Meteo."
        ) from exc


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/weather")
async def weather(
    city: str = Query(..., min_length=1, max_length=100, description="City to search")
) -> dict[str, Any]:
    normalized = " ".join(city.strip().split()).lower()
    if not normalized:
        raise HTTPException(status_code=400, detail="City is required.")

    now = time.monotonic()
    cached = _CACHE.get(normalized)
    if cached and now - cached[0] < CACHE_TTL_SECONDS:
        return cached[1]

    # Geocode first, then request a compact forecast for the selected location.
    geo = await _get(
        OPEN_METEO_GEOCODING,
        {
            "name": normalized,
            "count": 1,
            "language": "en",
            "format": "json",
        },
    )
    results = geo.get("results") or []
    if not results:
        raise HTTPException(status_code=404, detail=f"City not found: {city}")

    place = results[0]
    latitude = place["latitude"]
    longitude = place["longitude"]

    forecast = await _get(
        OPEN_METEO_FORECAST,
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "is_day,precipitation,weather_code,wind_speed_10m"
            ),
            "hourly": (
                "temperature_2m,precipitation_probability,weather_code,"
                "relative_humidity_2m"
            ),
            "daily": (
                "weather_code,temperature_2m_max,temperature_2m_min,"
                "precipitation_probability_max,sunrise,sunset"
            ),
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
            "timezone": "auto",
            "forecast_days": 7,
        },
    )

    payload = {
        "location": {
            "name": place.get("name", city),
            "country": place.get("country", ""),
            "admin1": place.get("admin1", ""),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": forecast.get("timezone", "auto"),
        },
        "current": forecast.get("current", {}),
        "current_units": forecast.get("current_units", {}),
        "hourly": forecast.get("hourly", {}),
        "hourly_units": forecast.get("hourly_units", {}),
        "daily": forecast.get("daily", {}),
        "daily_units": forecast.get("daily_units", {}),
    }

    _CACHE[normalized] = (now, payload)
    return payload
