-- =========================================================
-- 04_indexes.sql  |  Indexes + constraints for performance & quality
-- =========================================================

-- Time indexes (for temporal analysis / joins)
CREATE INDEX IF NOT EXISTS idx_weather_time
ON raw.weather(timestamp);

CREATE INDEX IF NOT EXISTS idx_bikemi_status_time
ON raw.bikemi_status(timestamp);

-- Helpful for station-based queries
CREATE INDEX IF NOT EXISTS idx_bikemi_status_station
ON raw.bikemi_status(station_id);

-- Spatial index (PostGIS) for spatial joins / nearest station queries
CREATE INDEX IF NOT EXISTS idx_bikemi_stations_geom
ON raw.bikemi_stations
USING GIST (geom);

-- Basic data-quality constraint for events
-- (end_datetime should not be before start_datetime)
ALTER TABLE raw.events
DROP CONSTRAINT IF EXISTS chk_event_dates;

ALTER TABLE raw.events
ADD CONSTRAINT chk_event_dates
CHECK (end_datetime IS NULL OR end_datetime >= start_datetime);

