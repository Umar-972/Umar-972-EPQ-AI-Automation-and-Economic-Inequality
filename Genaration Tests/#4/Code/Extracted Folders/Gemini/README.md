# Modern Open-Meteo Weather App

A fast, responsive desktop Weather application written in Python. Built using **FastAPI** for an asynchronous backend service and **CustomTkinter** + **Matplotlib** for a dark/light-themed GUI.

## Project Structure

weather_app/
├── backend.py        # FastAPI server for geocoding & Open-Meteo API requests
├── main.py           # CustomTkinter GUI client displaying weather metrics & charts
├── requirements.txt  # Dependencies list
└── README.md         # Documentation & running instructions

## Setup & Installation Instructions

### 1. Install Dependencies
Ensure you have Python 3.9+ installed, then install required libraries:

```bash
pip install -r requirements.txt