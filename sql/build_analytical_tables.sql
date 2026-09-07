
DROP TABLE IF EXISTS daily_temp_volatility;
CREATE TABLE daily_temp_volatility AS
SELECT
    city,
    reading_date,
    ROUND(max_temp_c - min_temp_c, 1) AS temp_range_c
FROM daily_city_summary;

DROP TABLE IF EXISTS daily_rolling_trends;
CREATE TABLE daily_rolling_trends AS
SELECT
    city,
    reading_date,
    avg_temp_c,
    ROUND(avg_temp_c - LAG(avg_temp_c) OVER (PARTITION BY city ORDER BY reading_date), 1) AS change_from_previous_day,
    ROUND(AVG(avg_temp_c) OVER (
        PARTITION BY city ORDER BY reading_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 1) AS rolling_3day_avg_temp_c
FROM daily_city_summary
ORDER BY city, reading_date;
