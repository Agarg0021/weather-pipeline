# 🌍 Weather Data Pipeline & Dashboard

A live, self-hosted data pipeline that collects hourly weather data 
for five global cities, transforms it into analytical tables, and 
surfaces it through an interactive dashboard — including a pipeline 
health panel that reflects the actual state of the ingestion process, 
not just the data.

![Dashboard Screenshot](dashboard/screenshots/dashboard-overview.png)

## Live Demo
🔗 (https://weather-pipeline-4b6nvp2hqqe5scptskotke.streamlit.app/)

*Note: the hosted demo uses a snapshot of the database as of [date]. 
Running the project locally (see Setup below) connects to the live, 
continuously-updating pipeline via cron.*

## The Question This Answers
Which cities have the most stable vs. volatile weather, and how does 
that vary day to day? This kind of question matters for anyone 
planning outdoor events, logistics, or comparing climates across 
locations — the answer isn't obvious from a single day's forecast, 
it requires accumulated historical data.

## Key Findings
*(from 7 days / 238 rows of collected data as of 11 September)*

- **New York** showed the widest average daily temperature swing 
  (5.4°C), making it the least thermally stable of the five cities 
  tracked — consistent with [inland/desert/etc.] climate patterns.
- **Mumbai** was the most stable, with an average daily range of 
  only 1.9°C.
- Humidity patterns diverged sharply by region: the Indian cities 
  (Delhi, Jaipur, Mumbai) trended toward 85%+ overnight humidity, 
  while New York's humidity swung more with time of day than with 
  season.


## Architecture
Open-Meteo API
│
▼
[Python ingestion script] ──hourly cron──▶ [SQLite: raw_readings]
│
▼
[SQL transformation layer]
(daily summaries, volatility,
rolling trends)
│
▼
[Streamlit dashboard]
(charts, filters, health panel)



## Tech Stack
- **Ingestion:** Python, `requests`, cron
- **Storage:** SQLite
- **Transformation:** SQL (window functions, CTEs), Python
- **Visualization:** Streamlit, Plotly
- **Version control:** Git/GitHub

## What Makes This More Than a Tutorial Project

**Data quality awareness, not just data collection.** Early into the 
project, I discovered my hourly cron job was only capturing 6-11 
readings per day instead of the expected ~24 — my Mac was sleeping 
for large parts of the day, silently pausing collection. Rather than 
ignore this, I:
1. Diagnosed it by comparing expected vs. actual row counts per day
2. Fixed the root cause (`pmset` config to prevent sleep while charging)
3. Added an `is_complete_day` flag to my analytical tables so any 
   downstream consumer — dashboard or otherwise — can distinguish 
   trustworthy daily aggregates from partial ones, rather than 
   silently averaging over incomplete data.

**Pipeline observability.** The dashboard includes a live health 
panel showing time-since-last-fetch and total row counts per city, 
with a status indicator (Healthy / Delayed / Stale). This was 
stress-tested by intentionally pausing the cron job and confirming 
the dashboard correctly reflected the outage — the dashboard reports 
on pipeline reality, not just static numbers.

## Setup & Running Locally

```bash
git clone https://github.com/Agarg0021/weather-pipeline.git
cd weather-pipeline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run ingestion once manually
python ingest/fetch_weather.py

# Build/refresh analytical tables
python sql/run_transformations.py

# Launch dashboard
python -m streamlit run dashboard/app.py
```

To collect data continuously, set up an hourly cron job:
```bash
crontab -e
# add:
0 * * * * cd /path/to/weather-pipeline && /path/to/weather-pipeline/venv/bin/python ingest/fetch_weather.py >> logs/pipeline.log 2>&1
```

## Project Structure
weather-pipeline/
├── ingest/ # API fetch + SQLite insert logic
├── sql/ # Transformation scripts (raw → analytical tables)
├── dashboard/ # Streamlit app
├── db/ # SQLite database (gitignored)
├── notes/ # Schema notes, analytical questions, findings
└── logs/ # Cron run logs (gitignored)



## Lessons Learned
- **Partial data is worse than no data if you don't flag it.** A 
  daily average computed from 6 readings looks identical to one from 
  24 readings unless you explicitly track completeness — this cost 
  me a misleading "day-over-day temperature drop" early in the 
  project that was actually just a partial-day artifact, not a real 
  trend.
- **Environment mismatches (conda vs. venv) are a common real-world 
  friction point** — `streamlit run` silently resolved to the wrong 
  Python environment more than once; `python -m streamlit run` fixed 
  it reliably.
- **A pipeline's health is as important as its data.** Building the 
  health panel changed how I thought about the dashboard — from "a 
  place to view numbers" to "a place to trust (or distrust) numbers."

## What I'd Add With More Time
- Deploy the pipeline itself (not just the dashboard) to a cloud 
  scheduler (e.g., GitHub Actions cron) so it doesn't depend on my 
  laptop staying awake
- Migrate from SQLite to Postgres for better concurrent access
- Add anomaly detection (flag readings that deviate sharply from a 
  city's rolling average)
- Expand to more cities for richer climate comparisons

## Author
Arpit Garg 