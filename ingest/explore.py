# ingest/explore.py
import requests
import json

CITIES = {
    "Jaipur":    (26.91962, 75.78781),
    "Delhi":     (28.65195, 77.23149),
    "Mumbai":    (19.07283, 72.88261),
    "New York":  (40.71427, -74.00597),
    "Singapore": (1.28967, 103.85007),
}

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
        "hourly": "temperature_2m,precipitation,wind_speed_10m",
        "timezone": "auto"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    for city, (lat, lon) in CITIES.items():
        data = get_weather(lat, lon)
        current = data["current"]
        print(f"\n{city}:")
        print(f"  Time (local): {current['time']}")
        print(f"  Temp: {current['temperature_2m']}°C")
        print(f"  Humidity: {current['relative_humidity_2m']}%")
        print(f"  Wind: {current['wind_speed_10m']} km/h")
        print(f"  Precipitation: {current['precipitation']} mm")
