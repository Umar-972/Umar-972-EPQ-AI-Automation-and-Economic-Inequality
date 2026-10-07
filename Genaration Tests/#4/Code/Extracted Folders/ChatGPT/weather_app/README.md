# Modern Weather App

A fullscreen desktop weather application built with **Python**, **CustomTkinter**, **FastAPI**, **Matplotlib**, and **Open-Meteo**.

## Features

- Search weather by city name.
- Open-Meteo geocoding resolves the city to coordinates.
- Current conditions including:
  - Temperature
  - Feels-like temperature
  - Humidity
  - Wind speed
  - Precipitation
- Seven-day forecast.
- Matplotlib temperature chart.
- Four preset visual themes:
  - Midnight
  - Ocean
  - Sunset
  - Forest
- Fullscreen at startup.
- Press `Esc` to toggle fullscreen.
- Fast, non-blocking weather requests.
- FastAPI runs locally as a lightweight API layer.
- HTTP connection pooling, HTTP/2 support, short timeouts, and a five-minute in-memory cache reduce latency and repeated external requests.
- The GUI stays responsive because network requests run outside Tkinter's main thread.

## Project structure

```text
weather_app/
├── backend.py       # FastAPI service and Open-Meteo integration
├── main.py          # CustomTkinter desktop application
├── requirements.txt # Python dependencies
└── README.md        # Documentation
```

### `backend.py`

Provides:

- `GET /health` — local service health check.
- `GET /weather?city=London` — geocodes the city and returns current, hourly, and daily weather.

The backend uses one reusable `httpx.AsyncClient`, HTTP/2, connection pooling, and a five-minute cache.

### `main.py`

Provides:

- Fullscreen CustomTkinter interface.
- City search controls.
- Theme switching.
- Current-weather presentation.
- Seven-day forecast cards.
- Matplotlib chart.
- Backend process lifecycle management.

When `main.py` starts, it launches Uvicorn on:

```text
http://127.0.0.1:8000
```

The GUI then waits for `/health` before it begins normal operation.

## Installation

Python **3.10+** is recommended.

### 1. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Start the application

```bash
python main.py
```

No API key is required.

## How the request flow works

```text
User enters city
       │
       ▼
CustomTkinter GUI
       │
       ▼
Local FastAPI /weather
       │
       ├── Open-Meteo Geocoding API
       │        │
       │        ▼
       │     latitude/longitude
       │
       └── Open-Meteo Forecast API
                │
                ▼
          weather JSON
                │
                ▼
       FastAPI response
                │
                ▼
       GUI + Matplotlib chart
```

## Performance notes

The application is designed to make the UI feel responsive:

1. **Persistent async HTTP client in FastAPI**
   - Reuses TCP connections.
   - Enables HTTP/2 when available.
   - Limits connections to avoid unnecessary socket churn.

2. **Local five-minute cache**
   - Searching the same city repeatedly does not immediately hit Open-Meteo again.

3. **Short timeouts**
   - Connect timeout is three seconds.
   - Overall request timeout is eight seconds.

4. **GUI threading**
   - Weather HTTP requests are made in a background thread.
   - Tkinter's main loop is not blocked while waiting for network responses.

5. **Compact API request**
   - Only the weather variables needed by the interface are requested.

## Themes

Theme presets are defined in `main.py` under `THEMES`.

To add a new theme, add another dictionary containing:

```python
{
    "bg": "...",
    "panel": "...",
    "panel2": "...",
    "text": "...",
    "muted": "...",
    "accent": "...",
    "accent_hover": "...",
    "border": "...",
}
```

The theme will automatically appear in the theme selector.

## Open-Meteo

The app uses:

- Open-Meteo Geocoding API:
  `https://geocoding-api.open-meteo.com/v1/search`
- Open-Meteo Forecast API:
  `https://api.open-meteo.com/v1/forecast`

Open-Meteo provides weather data without requiring an API key for typical non-commercial usage. Check Open-Meteo's current terms and attribution requirements before deploying the application commercially.

## Troubleshooting

### `ModuleNotFoundError`

Activate the virtual environment and run:

```bash
pip install -r requirements.txt
```

### The backend does not start

Check whether port `8000` is already in use. Stop the process using that port, then run:

```bash
python main.py
```

### Weather requests time out

Check your internet connection and whether Open-Meteo is reachable from your network.

### Fullscreen behavior

The app starts fullscreen by design. Press `Esc` to toggle fullscreen, or use the `Fullscreen` / `Exit Fullscreen` button in the header.

## License

This project is provided as a starter application. Review the licenses and usage terms of all third-party libraries and data providers before redistribution.
