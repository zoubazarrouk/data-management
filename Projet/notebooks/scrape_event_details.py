import os
import json
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dateutil import parser
import pytz

# --------------------
# CONFIG
# --------------------
TZ = pytz.timezone("Europe/Rome")
HEADERS = {"User-Agent": "DM-Project-Student/1.0 (educational use)"}

URLS_PATH = r"C:\Users\dell\DM_Project\data\raw\event_urls_2025-05-22_2025-12-22.csv"
OUT_RAW   = r"C:\Users\dell\DM_Project\data\raw\events_raw_milanotoday_2025-05-22_2025-12-22.csv"
OUT_CLEAN = r"C:\Users\dell\DM_Project\data\processed\events_clean_milanotoday_2025-05-22_2025-12-22.csv"
FAILED_LOG = r"C:\Users\dell\DM_Project\data\raw\events_failed_urls_2025-05-22_2025-12-22.txt"

CHECKPOINT_EVERY = 25   # save raw CSV every N collected events
PRINT_EVERY = 50        # print progress every N collected events


# --------------------
# NETWORK HELPERS (RETRIES + TIMEOUT)
# --------------------
def safe_get(url: str, retries: int = 5) -> str:
    """
    Download a page with retries + backoff.
    Helps with timeouts / DNS issues.
    """
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            time.sleep(random.uniform(0.3, 0.8))  # faster but still polite
            r = requests.get(url, headers=HEADERS, timeout=60)
            r.raise_for_status()
            return r.text
        except Exception as e:
            last_err = e
            # backoff: wait longer each retry
            time.sleep(1.5 * attempt + random.uniform(0, 1.0))
    raise last_err


# --------------------
# PARSING HELPERS
# --------------------
def normalize_dt(dt_str):
    if not dt_str or pd.isna(dt_str):
        return None
    dt = parser.parse(dt_str, dayfirst=True, fuzzy=True)
    if dt.tzinfo is None:
        dt = TZ.localize(dt)
    else:
        dt = dt.astimezone(TZ)
    return dt.isoformat()

def extract_jsonld_event(soup: BeautifulSoup):
    """
    Try to find schema.org Event JSON-LD.
    This is the most reliable way to extract startDate/location.
    """
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    for sc in scripts:
        txt = sc.get_text(strip=True)
        if not txt:
            continue
        try:
            data = json.loads(txt)
        except Exception:
            continue

        candidates = []
        if isinstance(data, list):
            candidates = data
        elif isinstance(data, dict) and "@graph" in data:
            candidates = data["@graph"]
        elif isinstance(data, dict):
            candidates = [data]

        for obj in candidates:
            if isinstance(obj, dict) and obj.get("@type") in ("Event", "Festival", "ScreeningEvent"):
                return obj
    return None

def parse_event_page(url: str) -> dict:
    html = safe_get(url)
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else None

    start_dt = None
    end_dt = None
    location_name = None
    address_text = None
    category = None

    obj = extract_jsonld_event(soup)
    if obj:
        start_dt = normalize_dt(obj.get("startDate"))
        end_dt = normalize_dt(obj.get("endDate"))

        loc = obj.get("location", {})
        if isinstance(loc, dict):
            location_name = loc.get("name")
            addr = loc.get("address")
            if isinstance(addr, dict):
                parts = [
                    addr.get("streetAddress"),
                    addr.get("addressLocality"),
                    addr.get("postalCode"),
                    addr.get("addressRegion"),
                    addr.get("addressCountry"),
                ]
                address_text = ", ".join([p for p in parts if p])
            elif isinstance(addr, str):
                address_text = addr

    # Category fallback
    kw = soup.find("meta", attrs={"name": "keywords"})
    if kw and kw.get("content"):
        category = kw["content"].split(",")[0].strip()

    return {
        "title": title,
        "category": category,
        "start_datetime_local": start_dt,
        "end_datetime_local": end_dt,
        "location_name": location_name,
        "address_text": address_text,
        "city": "Milan",
        "source": "milanotoday",
        "source_url": url,
        "scraped_at": pd.Timestamp.now(tz=TZ).isoformat(),
    }


# --------------------
# MAIN
# --------------------
def main():
    # Load URL list
    df_urls = pd.read_csv(URLS_PATH)
    urls = df_urls["event_url"].dropna().unique().tolist()
    print("URLs loaded:", len(urls))

    # Resume if OUT_RAW exists
    rows = []
    done_urls = set()
    errors = 0

    if os.path.exists(OUT_RAW):
        try:
            df_prev = pd.read_csv(OUT_RAW)
            if "source_url" in df_prev.columns:
                rows = df_prev.to_dict("records")
                done_urls = set(df_prev["source_url"].dropna().tolist())
                print("Resuming from checkpoint. Already scraped:", len(done_urls))
        except Exception as e:
            print("Warning: could not read existing checkpoint file. Starting fresh.", e)

    # Load failed log so we don't spam it with duplicates
    failed_set = set()
    if os.path.exists(FAILED_LOG):
        with open(FAILED_LOG, "r", encoding="utf-8") as f:
            failed_set = set(line.strip() for line in f if line.strip())

    collected_before = len(rows)

    # Scrape loop
    for url in urls:
        if url in done_urls:
            continue

        try:
            rows.append(parse_event_page(url))
            done_urls.add(url)
        except Exception as e:
            errors += 1
            # log failed URL
            if url not in failed_set:
                with open(FAILED_LOG, "a", encoding="utf-8") as f:
                    f.write(url + "\n")
                failed_set.add(url)

            if errors <= 15:
                print("ERROR:", url, "|", repr(e))

        # Save checkpoint every N collected rows
        if len(rows) % CHECKPOINT_EVERY == 0:
            pd.DataFrame(rows).to_csv(OUT_RAW, index=False)
            print(f"Checkpoint saved | rows: {len(rows)} | errors: {errors}")

        # Print progress every M collected rows
        if len(rows) % PRINT_EVERY == 0:
            print(f"Progress | collected {len(rows)} / {len(urls)}")

    # Final save raw
    df_raw = pd.DataFrame(rows)
    df_raw.to_csv(OUT_RAW, index=False)
    print("Saved raw:", OUT_RAW, "rows:", len(df_raw), "errors:", errors)

    # Cleaning
    df = df_raw.copy()

    # Robust parsing: force UTC to handle mixed offsets, then convert to Europe/Rome
    df["start_dt"] = pd.to_datetime(df["start_datetime_local"], errors="coerce", utc=True)
    df["end_dt"]   = pd.to_datetime(df["end_datetime_local"], errors="coerce", utc=True)

    # Convert timezone (NaT stays NaT)
    df["start_dt"] = df["start_dt"].dt.tz_convert("Europe/Rome")
    df["end_dt"]   = df["end_dt"].dt.tz_convert("Europe/Rome")

    # Now .dt accessor works
    df["start_date"] = df["start_dt"].dt.date
    df["start_hour"] = df["start_dt"].dt.hour


    # Deduplicate
    df = df.drop_duplicates(subset=["source_url"], keep="first")
    df = df.drop_duplicates(subset=["title", "start_datetime_local", "location_name"], keep="first")

    df.to_csv(OUT_CLEAN, index=False)
    print("Saved clean:", OUT_CLEAN, "rows:", len(df))

    # Quality quick check
    print("\nMissingness rates:")
    print(
        df[["title", "start_datetime_local", "location_name", "address_text", "category"]]
        .isna()
        .mean()
        .sort_values(ascending=False)
    )

    print("\nDone.")
    if collected_before > 0:
        print(f"Resumed from {collected_before} rows and ended with {len(df_raw)} raw rows.")


if __name__ == "__main__":
    main()
