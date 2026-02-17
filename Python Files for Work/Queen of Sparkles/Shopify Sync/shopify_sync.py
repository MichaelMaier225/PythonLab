import os
import requests
from dotenv import load_dotenv
from supabase import create_client

# Load credentials from .env
load_dotenv()

# === Shopify Credentials ===
SHOPIFY_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

# === Supabase Credentials ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Pull Products from Shopify ===
def get_all_products():
    url = f"https://{SHOPIFY_DOMAIN}/admin/api/2023-07/products.json?limit=50"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("products", [])

# === Push to Supabase ===
def sync_products_to_supabase():
    products = get_all_products()
    for product in products:
        title = product.get("title", "")
        for variant in product.get("variants", []):
            sku = variant.get("sku")
            if not sku:
                continue  # Skip if SKU is missing

            data = {
                "product_id": str(variant["id"]),
                "title": title,
                "sku": sku,
                "barcode": variant.get("barcode") or "",
                "count": variant.get("inventory_quantity", 0),
                "price": float(variant.get("price", 0)),
                "size": variant.get("option1") or "",
                "color": variant.get("option2") or "",
                "style_number": variant.get("option3") or ""
            }

            supabase.table("inventory").insert(data).execute()

if __name__ == "__main__":
    sync_products_to_supabase()
