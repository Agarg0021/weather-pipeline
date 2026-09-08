import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

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
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_daily_summary():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM daily_city_summary ORDER BY reading_date", conn)
    conn.close()
    return df

df = load_daily_summary()
cities = sorted(df["city"].unique())

# ---------- Sidebar ----------
st.sidebar.header("Filters")
selected_cities = st.sidebar.multiselect("Cities", cities, default=cities)
date_range = st.sidebar.date_input(
    "Date range",
    value=(pd.to_datetime(df["reading_date"]).min(), pd.to_datetime(df["reading_date"]).max()),
)

filtered = df[df["city"].isin(selected_cities)]
if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = filtered[
        (pd.to_datetime(filtered["reading_date"]) >= start) &
        (pd.to_datetime(filtered["reading_date"]) <= end)
    ]

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

# ---------- Raw data (collapsed by default) ----------
with st.expander("View raw daily summary table"):
    st.dataframe(filtered, use_container_width=True)

st.caption(f"Data as of {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')} · Rows marked `is_complete_day = 0` reflect partial-day coverage.")
