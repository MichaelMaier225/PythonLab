import json

# Load data
with open("products_full.json") as f:
    products_data = json.load(f)

with open("orders_full.json") as f:
    orders_data = json.load(f)


# Build variant inventory lookup
inventory = {}

for product in products_data:
    for variant in product["variants"]:
        variant_id = variant["id"]
        qty = variant["inventory_quantity"]
        title = f'{product["title"]} — {variant["title"]}'
        inventory[variant_id] = (qty, title)


# Track ordered variants
ordered_variants = {}

for order in orders_data:
    for item in order["line_items"]:
        vid = item["variant_id"]
        name = item["name"]

        if vid not in ordered_variants:
            ordered_variants[vid] = name


print("\n=== ORDERED BUT OUT OF STOCK ===")

found = False

for vid, name in ordered_variants.items():
    if vid in inventory:
        qty, title = inventory[vid]

        if qty <= 0:
            print(f"OUT OF STOCK: {title}")
            found = True
    else:
        print(f"NOT FOUND IN INVENTORY: {name}")
        found = True


if not found:
    print("No issues found.")
