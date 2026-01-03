import re, time, random
import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE = "https://www.milanotoday.it"
HEADERS = {"User-Agent": "DM-Project-Student/1.0 (educational use)"}

EVENT_LINK_RE = re.compile(r"^https?://(www\.)?milanotoday\.it/.+\.html?$")

def safe_get(url):
    time.sleep(random.uniform(1.0, 2.0))  # polite delay
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text

def listing_url(start_date, end_date, page=1):
    if page == 1:
        return f"{BASE}/eventi/dal/{start_date}/al/{end_date}/"
    return f"{BASE}/eventi/dal/{start_date}/al/{end_date}/pag/{page}/"

def extract_event_urls(html):
    soup = BeautifulSoup(html, "html.parser")
    urls = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("/"):
            href = BASE + href
        if EVENT_LINK_RE.match(href) and "/eventi/" in href:
            urls.add(href)
    return urls

def main():
    start_date = "2025-05-22"
    end_date = "2025-12-22"

    all_urls = set()
    page = 1

    while True:
        url = listing_url(start_date, end_date, page)
        print("Fetching:", url)
        html = safe_get(url)

        urls = extract_event_urls(html)
        new_urls = urls - all_urls

        # stop when a page adds no new events
        if not new_urls:
            print("No new URLs found. Stopping at page", page)
            break

        all_urls |= new_urls
        print(f"Page {page}: +{len(new_urls)} (total {len(all_urls)})")
        page += 1

    df = pd.DataFrame({"event_url": sorted(all_urls)})
    out = r"C:\Users\dell\DM_Project\data\raw\event_urls_2025-05-22_2025-12-22.csv"
    df.to_csv(out, index=False)
    print("Saved:", out)
    print("TOTAL URLs:", len(df))

if __name__ == "__main__":
    main()
