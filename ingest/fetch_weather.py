# ingest/fetch_weather.py
import requests
import sqlite3
import time
from datetime import datetime, timezone

DB_PATH = "db/weather.db"

CITIES = {
    "Jaipur":    (26.91962, 75.78781),
    "Delhi":     (28.65195, 77.23149),
    "Mumbai":    (19.07283, 72.88261),
    "New York":  (40.71427, -74.00597),
    "Singapore": (1.28967, 103.85007),
}

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            observation_time_local TEXT NOT NULL,
            fetched_at_utc TEXT NOT NULL,
            temperature_c REAL,
            humidity_pct INTEGER,
            wind_speed_kmh REAL,
            precipitation_mm REAL
        )
    """)
    conn.commit()
    conn.close()

def fetch_weather(lat, lon, retries=3):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
        "timezone": "auto"
    }
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            print(f"  Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(2 * attempt)  # backoff: 2s, 4s
    return None

def validate(current):
    # Basic sanity checks — catch obviously broken data before it hits the DB
    temp = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    if temp is None or not (-90 <= temp <= 60):
        return False
    if humidity is None or not (0 <= humidity <= 100):
        return False
    return True

def insert_reading(conn, city, current):
    conn.execute("""
        INSERT INTO raw_readings
        (city, observation_time_local, fetched_at_utc, temperature_c, humidity_pct, wind_speed_kmh, precipitation_mm)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        city,
        current["time"],
        datetime.now(timezone.utc).isoformat(),
        current["temperature_2m"],
        current["relative_humidity_2m"],
        current["wind_speed_10m"],
        current["precipitation"],
    ))

def run():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    success_count = 0
    fail_count = 0

    for city, (lat, lon) in CITIES.items():
        print(f"Fetching {city}...")
        data = fetch_weather(lat, lon)

        if data is None:
            print(f"  FAILED — no response after retries")
            fail_count += 1
            continue

        current = data.get("current")
        if not current or not validate(current):
            print(f"  FAILED — invalid data received")
            fail_count += 1
            continue

        insert_reading(conn, city, current)
        success_count += 1
        print(f"  OK — {current['temperature_2m']}°C, {current['relative_humidity_2m']}% humidity")

    conn.commit()
    conn.close()
    print(f"\nRun complete: {success_count} succeeded, {fail_count} failed")

if __name__ == "__main__":
    run()