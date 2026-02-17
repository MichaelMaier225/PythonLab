from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()

SHOP = os.getenv("SHOP_DOMAIN")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION", "2024-10")

def _config() -> tuple[str, dict[str, str]]:
    if not SHOP or not ACCESS_TOKEN:
        raise ValueError("Missing SHOP_DOMAIN or SHOPIFY_ACCESS_TOKEN in .env file")

    base_url = f"https://{SHOP}/admin/api/{API_VERSION}"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    return base_url, headers


def _paginate_endpoint(base_url: str, endpoint: str) -> str:
    join = "&" if "?" in endpoint else "?"
    return f"{base_url}/{endpoint}{join}limit=250"


def fetch_all(endpoint: str, pause_seconds: float = 0.35) -> List[Dict[str, Any]]:
    """Fetch all records from a Shopify REST endpoint using pagination links."""
    base_url, headers = _config()
    url = _paginate_endpoint(base_url, endpoint)
    results: List[Dict[str, Any]] = []

    while url:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        payload = response.json()
        root_key = next(iter(payload.keys()))
        results.extend(payload[root_key])

        link_header = response.headers.get("Link", "")
        next_link = None
        for part in link_header.split(","):
            if 'rel="next"' in part:
                next_link = part.split("<")[1].split(">", 1)[0]
                break

        url = next_link
        if url:
            time.sleep(pause_seconds)

    return results


def sync_shopify_data(output_dir: Path) -> Dict[str, int]:
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Downloading ALL orders...")
    orders = fetch_all("orders.json?status=any")

    print("Downloading ALL products...")
    products = fetch_all("products.json")

    print("Downloading ALL customers...")
    customers = fetch_all("customers.json")

    (output_dir / "orders_full.json").write_text(json.dumps(orders, indent=2))
    (output_dir / "products_full.json").write_text(json.dumps(products, indent=2))
    (output_dir / "customers_full.json").write_text(json.dumps(customers, indent=2))

    stats = {
        "orders": len(orders),
        "products": len(products),
        "customers": len(customers),
    }
    print(f"DONE — Saved data to {output_dir.resolve()} :: {stats}")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Shopify data locally for analytics.")
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Directory for synced JSON files (default: data)",
    )
    args = parser.parse_args()

    sync_shopify_data(Path(args.output_dir))


if __name__ == "__main__":
    main()
