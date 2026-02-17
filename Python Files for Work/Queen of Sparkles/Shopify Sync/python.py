import os
import requests
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")  # shop-queen-of-sparkles.myshopify.com
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

def get_locations():
    url = f"https://{SHOPIFY_DOMAIN}/admin/api/2023-07/locations.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    locations = response.json().get("locations", [])
    
    for loc in locations:
        print(f"Name: {loc['name']} | ID: {loc['id']}")
    
if __name__ == "__main__":
    get_locations()
