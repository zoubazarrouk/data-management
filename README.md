# Data Management Project – Urban Mobility & City Activity Patterns (Milan)

## Team
- Zaineb has done this Person A: API acquisition (Weather + BikeMi), database modeling, temporal integration
- Oumaima has doen this Person B: Web scraping (MilanoToday events), events profiling, spatial integration + quality assessment

## Research Questions (RQs)
1. How do weather conditions influence bike-sharing demand across different areas and time periods?
2. To what extent do city events correlate with mobility anomalies (bike stations / traffic counts / pedestrian flows)?
3. Which zones exhibit the most irregular usage patterns during weekends or holidays?

## Data Sources
### 1) Events (Scraping) – MilanoToday (Person B)
- Source: MilanoToday “Eventi a Milano”
- Method: Web scraping (list pages + event detail pages)
- Time window scraped: **2025-05-22 → 2025-12-22**
- Output size: **882 events (clean dataset)**
- Files:
  - `Projet/data/processed/events_clean_milanotoday_2025-05-22_2025-12-22.csv`
- Scripts:
  - `Projet/notebooks/collect_event_urls.py` (collects event URLs with pagination)
  - `Projet/notebooks/scrape_event_details.py` (scrapes event details + produces clean CSV)

Fields extracted (main):
- title, category, start/end datetime, location name, address text, city, source_url, scraped_at

Known limitations:
- Some events have missing category/location/address (site does not always provide them).
- A small number of pages may return errors (timeouts/404); errors are logged.

### 2) Weather (API) – Open-Meteo (Person A)
- Method: API calls (hourly/daily: temperature, precipitation, wind, humidity)
- Files stored in: `Projet/data/raw/`

### 3) Bike-sharing / Mobility (API) – BikeMi / mobility data (Person A)
- Method: API acquisition (station info / availability)
- Files stored in: `Projet/data/raw/`

## Pipeline (Project Phases)
1. Data acquisition (API + scraping)
2. Storage & modeling (PostgreSQL + PostGIS)
3. Data profiling (before integration)
4. Data integration:
   - Weather + mobility (temporal join)
   - Events + stations/mobility (spatial enrichment + time join)
5. Data quality assessment (before vs after integration)
6. Exploratory analysis & insights
7. Final report (PDF) + slides (PPT) + reproducibility guide

## Reproducibility (quick start)
- Python scripts for events scraping are in `Projet/notebooks/`
- Raw and processed datasets are under `Projet/data/`
- Database schema / ETL scripts will be added in `Projet/sql/` and `Projet/etl/`
