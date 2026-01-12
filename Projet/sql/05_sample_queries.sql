-- =========================================================
-- 05_sample_queries.sql
-- Sample analytical queries for the project
-- =========================================================

-- ---------------------------------------------------------
-- QUERY 1
-- Number of events per day (MilanoToday)
-- Helps analyze city activity intensity over time
-- ---------------------------------------------------------
SELECT
    DATE(start_datetime) AS event_day,
    COUNT(*) AS total_events
FROM raw.events
GROUP BY event_day
ORDER BY event_day;


-- ---------------------------------------------------------
-- QUERY 2
-- Average bike availability vs weather (hourly)
-- Links mobility demand with temperature
-- ---------------------------------------------------------
SELECT
    w.timestamp,
    w.temperature,
    AVG(b.bikes_available) AS avg_bikes_available
FROM raw.weather w
JOIN raw.bikemi_status b
    ON DATE_TRUNC('hour', w.timestamp) = DATE_TRUNC('hour', b.timestamp)
GROUP BY w.timestamp, w.temperature
ORDER BY w.timestamp;


-- ---------------------------------------------------------
-- QUERY 3 (optional but good)
-- Average bike availability per station
-- ---------------------------------------------------------
SELECT
    s.station_id,
    s.name,
    AVG(b.bikes_available) AS avg_bikes_available
FROM raw.bikemi_stations s
JOIN raw.bikemi_status b
    ON s.station_id = b.station_id
GROUP BY s.station_id, s.name
ORDER BY avg_bikes_available DESC;

