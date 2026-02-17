import os
import requests
from dotenv import load_dotenv
from supabase import create_client
from flask import Flask, request, render_template_string
from threading import Thread

# Load .env credentials
load_dotenv()

# === Credentials ===
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SHOPIFY_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_LOCATION_ID = int(os.getenv("SHOPIFY_LOCATION_ID"))

# === Setup Supabase + Flask ===
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
app = Flask(__name__)

# === Shared HTML Template ===
BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 50px;
        }
        h2 {
            color: #333;
        }
        form {
            background-color: white;
            padding: 20px 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        input[name="barcode"] {
            padding: 10px;
            font-size: 16px;
            width: 250px;
            margin-right: 10px;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        p {
            font-weight: bold;
            color: #28a745;
        }
        table {
            margin-top: 30px;
            border-collapse: collapse;
            width: 80%;
        }
        th, td {
            border: 1px solid #ccc;
            padding: 10px;
        }
        th {
            background-color: #007bff;
            color: white;
        }
        td {
            background-color: white;
        }
    </style>
</head>
<body>
    <h2>{{ title }}</h2>
    {{ content | safe }}
</body>
</html>
"""

def render_page(title, content):
    return render_template_string(BASE_TEMPLATE, title=title, content=content)

# === Shopify Inventory Sync ===
def update_shopify_inventory(inventory_item_id, location_id, new_quantity):
    url = f"https://{SHOPIFY_DOMAIN}/admin/api/2023-07/inventory_levels/set.json"
    headers = {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "location_id": location_id,
        "inventory_item_id": inventory_item_id,
        "available": new_quantity
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"[SHOPIFY ERROR] {response.status_code}: {response.text}")
    return response.status_code == 200

def async_shopify_update(product, new_count):
    def task():
        update_shopify_inventory(product["inventory_item_id"], SHOPIFY_LOCATION_ID, new_count)
    Thread(target=task).start()

# === Routes ===
@app.route("/", methods=["GET", "POST"])
def add_inventory():
    message = ""
    if request.method == "POST":
        barcode = request.form.get("barcode", "").strip()
        if barcode:
            res = supabase.table("inventory").select("*").eq("barcode", barcode).single().execute()
            product = res.data
            if product:
                new_count = product["count"] + 1
                supabase.table("inventory").update({"count": new_count}).eq("barcode", barcode).execute()
                if product.get("inventory_item_id"):
                    async_shopify_update(product, new_count)
                message = f"✅ Added: {product['title']} (Size: {product['size']}) → New Count: {new_count}"
            else:
                message = f"❌ Product with barcode {barcode} not found."
    form = """
    <form method="POST">
        <input autofocus name="barcode" placeholder="Scan barcode" />
        <button type="submit">Add</button>
    </form>
    """
    if message:
        form += f"<p>{message}</p>"
    return render_page("Add to Inventory", form)

@app.route("/deduct", methods=["GET", "POST"])
def deduct_inventory():
    message = ""
    if request.method == "POST":
        barcode = request.form.get("barcode", "").strip()
        if barcode:
            res = supabase.table("inventory").select("*").eq("barcode", barcode).single().execute()
            product = res.data
            if product:
                new_count = max(0, product["count"] - 1)
                supabase.table("inventory").update({"count": new_count}).eq("barcode", barcode).execute()
                if product.get("inventory_item_id"):
                    async_shopify_update(product, new_count)
                message = f"✅ Deducted: {product['title']} (Size: {product['size']}) → New Count: {new_count}"
            else:
                message = f"❌ Product with barcode {barcode} not found."
    form = """
    <form method="POST">
        <input autofocus name="barcode" placeholder="Scan barcode to deduct" />
        <button type="submit">Deduct</button>
    </form>
    """
    if message:
        form += f"<p>{message}</p>"
    return render_page("Deduct from Inventory", form)

@app.route("/inventory")
def view_inventory():
    res = supabase.table("inventory").select("*").order("title").execute()
    products = res.data or []
    table = """
    <table>
        <tr><th>Title</th><th>Size</th><th>Barcode</th><th>Count</th></tr>
    """
    for item in products:
        table += f"<tr><td>{item['title']}</td><td>{item['size']}</td><td>{item['barcode']}</td><td>{item['count']}</td></tr>"
    table += "</table>"
    return render_page("Current Inventory", table)

# === Run ===
if __name__ == "__main__":
    print("[APP] Running on http://localhost:5050")
    app.run(debug=True, port=5050)
