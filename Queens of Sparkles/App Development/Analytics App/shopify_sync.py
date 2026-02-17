import requests
import json
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SHOP = os.getenv("SHOP_DOMAIN")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION", "2024-10")

if not SHOP or not ACCESS_TOKEN:
    raise ValueError("Missing SHOP_DOMAIN or SHOPIFY_ACCESS_TOKEN in .env file")

BASE_URL = f"https://{SHOP}/admin/api/{API_VERSION}"

headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}


def fetch_all(endpoint):
    if "?" in endpoint:
        url = f"{BASE_URL}/{endpoint}&limit=250"
    else:
        url = f"{BASE_URL}/{endpoint}?limit=250"

    results = []

    while url:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        key = list(data.keys())[0]
        results.extend(data[key])

        # Pagination handling
        link_header = response.headers.get("Link")
        if link_header and 'rel="next"' in link_header:
            next_url = link_header.split("<")[1].split(">")[0]
            url = next_url
        else:
            url = None

        # Avoid Shopify rate limits
        time.sleep(0.5)

    return results


if __name__ == "__main__":
    print("Downloading ALL orders...")
    orders = fetch_all("orders.json?status=any")

    print("Downloading ALL products...")
    products = fetch_all("products.json")

    print("Downloading ALL customers...")
    customers = fetch_all("customers.json")

    with open("orders_full.json", "w") as f:
        json.dump(orders, f, indent=2)

    with open("products_full.json", "w") as f:
        json.dump(products, f, indent=2)

    with open("customers_full.json", "w") as f:
        json.dump(customers, f, indent=2)

    print("DONE — Data saved to files.")
