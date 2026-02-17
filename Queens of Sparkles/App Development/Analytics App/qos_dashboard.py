import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="QOS Operations Dashboard", layout="wide")

st.title("Queen of Sparkles — Store Operations Dashboard")


# ---------- LOAD DATA ----------

@st.cache_data
def load_data():
    with open("orders_full.json") as f:
        orders = json.load(f)

    with open("products_full.json") as f:
        products = json.load(f)

    return orders, products


orders_data, products_data = load_data()


# ---------- BUILD SALES TABLE ----------

rows = []

for order in orders_data:
    date = order["created_at"]
    total = float(order["total_price"])

    for item in order["line_items"]:
        rows.append({
            "date": pd.to_datetime(date),
            "order_id": order["id"],
            "product": item["name"],
            "variant_id": item["variant_id"],
            "quantity": item["quantity"],
            "price": float(item["price"]),
            "customer": order.get("customer", {}).get("email", "Guest")
        })

sales_df = pd.DataFrame(rows)


# ---------- BUILD INVENTORY TABLE ----------

inventory_rows = []

for product in products_data:
    for variant in product["variants"]:
        inventory_rows.append({
            "variant_id": variant["id"],
            "product": f'{product["title"]} — {variant["title"]}',
            "stock": variant["inventory_quantity"]
        })

inventory_df = pd.DataFrame(inventory_rows)


# ---------- REVENUE TREND ----------

st.header("Revenue Trend")

daily = sales_df.groupby(sales_df["date"].dt.date)["price"].sum().reset_index()

fig = px.line(daily, x="date", y="price")
st.plotly_chart(fig, use_container_width=True)


# ---------- TOP SELLERS ----------

st.header("Top Selling Products")

top_products = (
    sales_df.groupby("product")["quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig2 = px.bar(top_products, x="quantity", y="product", orientation="h")
st.plotly_chart(fig2, use_container_width=True)


# ---------- OUT OF STOCK BUT RECENTLY SOLD ----------

st.header("🚨 Out of Stock BUT Recently Sold")

recent_cutoff = datetime.now() - timedelta(days=30)

recent_sales = sales_df[sales_df["date"] >= recent_cutoff]

recent_variants = recent_sales["variant_id"].unique()

risk_items = inventory_df[
    (inventory_df["variant_id"].isin(recent_variants)) &
    (inventory_df["stock"] <= 0)
]

st.dataframe(risk_items)


# ---------- DEAD INVENTORY ----------

st.header("💤 Dead Inventory (Stock but No Sales in 60 Days)")

old_cutoff = datetime.now() - timedelta(days=60)

recent_sales_60 = sales_df[sales_df["date"] >= old_cutoff]

recent_variants_60 = recent_sales_60["variant_id"].unique()

dead_inventory = inventory_df[
    (~inventory_df["variant_id"].isin(recent_variants_60)) &
    (inventory_df["stock"] > 0)
]

st.dataframe(dead_inventory)


# ---------- VIP CUSTOMERS ----------

st.header("🏆 Top Customers")

top_customers = (
    sales_df.groupby("customer")["price"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig3 = px.bar(top_customers, x="price", y="customer", orientation="h")
st.plotly_chart(fig3, use_container_width=True)
