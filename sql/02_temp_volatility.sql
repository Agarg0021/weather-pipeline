-- Which city has the widest daily temperature swing?
SELECT
    city,
    DATE(observation_time_local) AS reading_date,
    ROUND(MAX(temperature_c) - MIN(temperature_c), 1) AS temp_range_c
FROM raw_readings
GROUP BY city, DATE(observation_time_local)
ORDER BY temp_range_c DESC;
