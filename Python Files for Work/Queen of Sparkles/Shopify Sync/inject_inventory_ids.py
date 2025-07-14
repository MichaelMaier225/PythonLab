import os
import requests
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

VARIANT_ID = "46693821087982"  # this is the Variant ID, NOT inventory_item_id

url = f"https://{SHOPIFY_DOMAIN}/admin/api/2023-07/variants/{VARIANT_ID}.json"
headers = {
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    data = response.json()
    inventory_item_id = data['variant']['inventory_item_id']
    print(f"✅ Inventory Item ID: {inventory_item_id}")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
