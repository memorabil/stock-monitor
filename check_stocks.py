import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import time
import random

DATA_FILE = "data/history.json"
PRODUCTS_FILE = "data/products.json"
SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY", "")

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_stock(url):
    for attempt in range(3):
        try:
            scraper_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}&country_code=ro"
            resp = requests.get(scraper_url, timeout=60)
            print(f"    HTTP {resp.status_code}")

            if resp.status_code == 403:
                print(f"    Attempt {attempt+1}: blocked, retrying...")
                time.sleep(random.uniform(3, 6))
                continue

            if resp.status_code == 404:
                print(f"    Product page not found (404)")
                return "error"

            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            for tag in soup.find_all(class_=lambda c: c and any(x in c.lower() for x in [
                "stock", "availability", "disponibil", "stoc", "add-to-cart", "out-of-stock"
            ])):
                tag_text = tag.get_text(strip=True).upper()
                if any(x in tag_text for x in ["INDISPONIBIL", "OUT OF STOCK", "STOC EPUIZAT"]):
                    return "nostock"
                if any(x in tag_text for x in ["ÎN STOC", "IN STOC", "IN STOCK", "DISPONIBIL", "ADAUGA IN COS", "ADAUGĂ ÎN COȘ"]):
                    return "stock"

            full_text = soup.get_text(separator=" ", strip=True).upper()
            if any(x in full_text for x in ["INDISPONIBIL", "OUT OF STOCK", "STOC EPUIZAT"]):
                return "nostock"
            if any(x in full_text for x in ["ÎN STOC", "IN STOC", "IN STOCK", "ADAUGA IN COS"]):
                return "stock"

            return "unknown"

        except requests.exceptions.Timeout:
            print(f"    Attempt {attempt+1}: timeout")
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            print(f"    Attempt {attempt+1}: error - {e}")
            time.sleep(random.uniform(2, 4))

    return "error"

def main():
    if not SCRAPER_API_KEY:
        print("ERROR: SCRAPER_API_KEY not set!")
        return

    products = load_json(PRODUCTS_FILE, [])
    history = load_json(DATA_FILE, {})

    if not products:
        print("No products found in data/products.json")
        return

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Checking {len(products)} products for {today}...")

    for prod in products:
        pid = prod["id"]
        url = prod["url"]
        print(f"\n  Checking: {prod.get('name', url)}")

        new_status = check_stock(url)

        if pid not in history:
            history[pid] = {}

        prev_dates = sorted(history[pid].keys())
        prev_status = None
        if prev_dates:
            last = prev_dates[-1]
            if last != today:
                prev_status = history[pid][last].get("status")

        changed = (
            prev_status is not None
            and prev_status not in ("unknown", "error")
            and prev_status != new_status
            and new_status not in ("unknown", "error")
        )

        history[pid][today] = {
            "status": new_status,
            "changed": changed,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }

        prod["status"] = new_status
        prod["lastCheck"] = datetime.now(timezone.utc).isoformat()
        if changed:
            prod["lastChanged"] = today

        print(f"  -> {new_status}{' (STATUS CHANGED!)' if changed else ''}")
        time.sleep(random.uniform(1, 2))

    save_json(DATA_FILE, history)
    save_json(PRODUCTS_FILE, products)
    print("\nDone. Data saved.")

if __name__ == "__main__":
    main()
