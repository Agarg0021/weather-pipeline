-- Daily min/max/avg temperature, humidity, and total precipitation per city
SELECT
    city,
    DATE(observation_time_local) AS reading_date,
    ROUND(MIN(temperature_c), 1) AS min_temp_c,
    ROUND(MAX(temperature_c), 1) AS max_temp_c,
    ROUND(AVG(temperature_c), 1) AS avg_temp_c,
    ROUND(AVG(humidity_pct), 1) AS avg_humidity_pct,
    ROUND(SUM(precipitation_mm), 2) AS total_precipitation_mm,
    COUNT(*) AS reading_count
FROM raw_readings
GROUP BY city, DATE(observation_time_local)
ORDER BY reading_date, city;
