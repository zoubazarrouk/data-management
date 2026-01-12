-- =========================================================
-- 03_tables.sql  |  Core RAW tables (events, weather, bikemi)
-- =========================================================

-- Make sure schemas exist
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS processed;

-- =========================================================
-- EVENTS (MilanoToday)
-- =========================================================
CREATE TABLE IF NOT EXISTS raw.events (
    event_id SERIAL PRIMARY KEY,
    title TEXT,
    category TEXT,
    start_datetime TIMESTAMP,
    end_datetime TIMESTAMP,
    location_name TEXT,
    address TEXT,
    city TEXT,
    source_url TEXT UNIQUE,
    scraped_at TIMESTAMP
);

-- =========================================================
-- WEATHER (Open-Meteo)
-- =========================================================
CREATE TABLE IF NOT EXISTS raw.weather (
    weather_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    temperature REAL,
    precipitation REAL,
    wind_speed REAL,
    humidity REAL
);

-- =========================================================
-- BIKEMI STATIONS (static info)
-- geom = point in WGS84 (EPSG:4326)
-- =========================================================
CREATE TABLE IF NOT EXISTS raw.bikemi_stations (
    station_id INTEGER PRIMARY KEY,
    name TEXT,
    capacity INTEGER,
    geom GEOMETRY(Point, 4326)
);

-- =========================================================
-- BIKEMI STATUS (time series)
-- station_id links to bikemi_stations
-- =========================================================
CREATE TABLE IF NOT EXISTS raw.bikemi_status (
    status_id SERIAL PRIMARY KEY,
    station_id INTEGER REFERENCES raw.bikemi_stations(station_id),
    timestamp TIMESTAMP NOT NULL,
    bikes_available INTEGER,
    docks_available INTEGER
);

