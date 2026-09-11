import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone

DB_PATH = "db/weather.db"

st.set_page_config(page_title="Weather Pipeline Dashboard", page_icon="🌍", layout="wide")

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
    }

    div[data-testid="stMetric"] {
        background-color: #1A1F2B;
        border: 1px solid #2A2F3B;
        border-radius: 12px;
        padding: 16px 20px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: #4FC3F7;
    }

    h2, h3 {
        margin-top: 1.5rem !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #12161F;
        border-right: 1px solid #2A2F3B;
    }

    hr {
        border-color: #2A2F3B !important;
    }

    .health-ok {
        color: #4ADE80;
        font-weight: 600;
    }
    .health-warn {
        color: #FBBF24;
        font-weight: 600;
    }
    .health-bad {
        color: #F87171;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_daily_summary():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM daily_city_summary ORDER BY reading_date", conn)
    conn.close()
    return df

@st.cache_data(ttl=300)
def load_volatility():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM daily_temp_volatility ORDER BY reading_date", conn)
    conn.close()
    return df

@st.cache_data(ttl=300)
def load_latest_readings():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT city, observation_time_local, temperature_c, humidity_pct, wind_speed_kmh, precipitation_mm
        FROM raw_readings
        WHERE (city, observation_time_local) IN (
            SELECT city, MAX(observation_time_local)
            FROM raw_readings
            GROUP BY city
        )
        ORDER BY city
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=60)
def load_pipeline_health():
    conn = sqlite3.connect(DB_PATH)
    total_rows = pd.read_sql_query("SELECT COUNT(*) AS n FROM raw_readings", conn)["n"][0]
    last_fetch = pd.read_sql_query("SELECT MAX(fetched_at_utc) AS t FROM raw_readings", conn)["t"][0]
    per_city_counts = pd.read_sql_query(
        "SELECT city, COUNT(*) AS reading_count FROM raw_readings GROUP BY city ORDER BY city", conn
    )
    conn.close()
    return total_rows, last_fetch, per_city_counts

df = load_daily_summary()
volatility = load_volatility()
latest_readings = load_latest_readings()
total_rows, last_fetch, per_city_counts = load_pipeline_health()
cities = sorted(df["city"].unique())

# ---------- Sidebar ----------
st.sidebar.header("Filters")
selected_cities = st.sidebar.multiselect("Cities", cities, default=cities)
date_range = st.sidebar.date_input(
    "Date range",
    value=(pd.to_datetime(df["reading_date"]).min(), pd.to_datetime(df["reading_date"]).max()),
)

auto_refresh = st.sidebar.checkbox("Auto-refresh every 5 min", value=False)
if auto_refresh:
    st.sidebar.caption("Page will refresh automatically.")

filtered = df[df["city"].isin(selected_cities)]
if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[
        (pd.to_datetime(filtered["reading_date"]) >= start) &
        (pd.to_datetime(filtered["reading_date"]) <= end)
    ]

filtered_volatility = volatility[volatility["city"].isin(selected_cities)]
filtered_latest = latest_readings[latest_readings["city"].isin(selected_cities)]

# ---------- Header ----------
st.title("🌍 Weather Data Pipeline Dashboard")
st.caption("Live weather data collected hourly via the Open-Meteo API")

# ---------- Metric cards ----------
latest_date = filtered["reading_date"].max()
latest = filtered[filtered["reading_date"] == latest_date]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Cities tracked", len(selected_cities))
col2.metric("Latest date", latest_date if latest_date else "—")
if not latest.empty:
    hottest = latest.loc[latest["avg_temp_c"].idxmax()]
    coolest = latest.loc[latest["avg_temp_c"].idxmin()]
    col3.metric("Hottest (latest day)", f"{hottest['city']}", f"{hottest['avg_temp_c']}°C")
    col4.metric("Coolest (latest day)", f"{coolest['city']}", f"{coolest['avg_temp_c']}°C")

# ---------- Pipeline Health Panel ----------
with st.expander("🩺 Pipeline Health", expanded=True):
    if last_fetch:
        last_fetch_dt = pd.to_datetime(last_fetch)

        if last_fetch_dt.tzinfo is None:
            last_fetch_dt = last_fetch_dt.tz_localize("UTC")
        else:
            last_fetch_dt = last_fetch_dt.tz_convert("UTC")

        minutes_since = (datetime.now(timezone.utc) - last_fetch_dt).total_seconds() / 60

        if minutes_since < 90:
            status_html = '<span class="health-ok">● Healthy</span>'
        elif minutes_since < 300:
            status_html = '<span class="health-warn">● Delayed</span>'
        else:
            status_html = '<span class="health-bad">● Stale</span>'

        hc1, hc2, hc3 = st.columns(3)
        hc1.markdown(f"**Status:** {status_html}", unsafe_allow_html=True)
        hc2.metric("Last fetch (min ago)", f"{minutes_since:.0f}")
        hc3.metric("Total rows collected", f"{total_rows:,}")

        st.caption("Reading count per city (all-time):")
        st.dataframe(per_city_counts, use_container_width=True, hide_index=True)
    else:
        st.warning("No pipeline data found yet.")

st.divider()

# ---------- Chart: Temperature ----------
st.subheader("Daily Average Temperature by City")
fig = px.line(
    filtered,
    x="reading_date",
    y="avg_temp_c",
    color="city",
    markers=True,
    template="plotly_dark",
    labels={"reading_date": "Date", "avg_temp_c": "Avg Temp (°C)", "city": "City"},
)
fig.update_layout(
    hovermode="x unified",
    legend_title_text="",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

# ---------- Chart: Humidity ----------
st.subheader("Daily Average Humidity by City")
fig2 = px.bar(
    filtered,
    x="reading_date",
    y="avg_humidity_pct",
    color="city",
    barmode="group",
    template="plotly_dark",
    labels={"reading_date": "Date", "avg_humidity_pct": "Avg Humidity (%)", "city": "City"},
)
fig2.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig2, use_container_width=True)

# ---------- Chart: Temperature Volatility ----------
st.subheader("Temperature Volatility by City")
st.caption("Daily temperature range (max − min). Higher bars = more variable weather that day.")
fig3 = px.bar(
    filtered_volatility,
    x="reading_date",
    y="temp_range_c",
    color="city",
    barmode="group",
    template="plotly_dark",
    labels={"reading_date": "Date", "temp_range_c": "Temp Range (°C)", "city": "City"},
)
fig3.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig3, use_container_width=True)

# ---------- City comparison snapshot ----------
st.subheader("Latest Reading per City")
st.dataframe(
    filtered_latest.rename(columns={
        "city": "City",
        "observation_time_local": "Observed At (Local)",
        "temperature_c": "Temp (°C)",
        "humidity_pct": "Humidity (%)",
        "wind_speed_kmh": "Wind (km/h)",
        "precipitation_mm": "Precip (mm)",
    }),
    use_container_width=True,
    hide_index=True,
)

# ---------- Raw data (collapsed by default) ----------
with st.expander("View raw daily summary table"):
    st.dataframe(filtered, use_container_width=True)

st.caption(f"Data as of {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')} · Rows marked `is_complete_day = 0` reflect partial-day coverage.")

# ---------- Auto-refresh logic ----------
if auto_refresh:
    import time
    time.sleep(300)
    st.rerun()