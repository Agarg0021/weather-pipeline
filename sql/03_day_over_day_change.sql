-- Day-over-day change in average temperature, per city
WITH daily_avg AS (
    SELECT
        city,
        DATE(observation_time_local) AS reading_date,
        AVG(temperature_c) AS avg_temp_c
    FROM raw_readings
    GROUP BY city, reading_date
)
SELECT
    city,
    reading_date,
    ROUND(avg_temp_c, 1) AS avg_temp_c,
    ROUND(avg_temp_c - LAG(avg_temp_c) OVER (PARTITION BY city ORDER BY reading_date), 1) AS change_from_previous_day
FROM daily_avg
ORDER BY city, reading_date;
