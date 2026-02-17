from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="QOS Operations Dashboard", layout="wide")
st.title("Queen of Sparkles — Shopify Analytics Command Center")

DATA_DIR = Path(__file__).parent / "data"
ORDERS_FILE = DATA_DIR / "orders_full.json"
PRODUCTS_FILE = DATA_DIR / "products_full.json"


@st.cache_data
def load_data() -> tuple[list[dict], list[dict]]:
    if not ORDERS_FILE.exists() or not PRODUCTS_FILE.exists():
        st.error(
            "Missing synced Shopify JSON files. Run: `python run_qos_analytics.py --sync-only`"
        )
        st.stop()

    orders = json.loads(ORDERS_FILE.read_text())
    products = json.loads(PRODUCTS_FILE.read_text())
    return orders, products


orders_data, products_data = load_data()

sales_rows = []
for order in orders_data:
    order_date = pd.to_datetime(order.get("created_at"))
    customer_email = order.get("customer", {}).get("email", "Guest")
    financial_status = order.get("financial_status", "unknown")

    for item in order.get("line_items", []):
        quantity = item.get("quantity", 0) or 0
        unit_price = float(item.get("price", 0) or 0)
        sales_rows.append(
            {
                "date": order_date,
                "order_id": order.get("id"),
                "product": item.get("name", "Unknown"),
                "variant_id": item.get("variant_id"),
                "quantity": quantity,
                "unit_price": unit_price,
                "line_revenue": quantity * unit_price,
                "customer": customer_email,
                "financial_status": financial_status,
            }
        )

sales_df = pd.DataFrame(sales_rows)
if sales_df.empty:
    st.warning("No sales data found in the current Shopify export.")
    st.stop()

inventory_rows = []
for product in products_data:
    for variant in product.get("variants", []):
        inventory_rows.append(
            {
                "variant_id": variant.get("id"),
                "product": f"{product.get('title', 'Unknown')} — {variant.get('title', 'Default')}",
                "stock": variant.get("inventory_quantity", 0) or 0,
            }
        )

inventory_df = pd.DataFrame(inventory_rows)

min_date = sales_df["date"].min().date()
max_date = sales_df["date"].max().date()

st.sidebar.header("Filters")
start_date, end_date = st.sidebar.date_input(
    "Date range",
    value=(max_date - timedelta(days=30), max_date),
    min_value=min_date,
    max_value=max_date,
)

filtered = sales_df[(sales_df["date"].dt.date >= start_date) & (sales_df["date"].dt.date <= end_date)]

if filtered.empty:
    st.warning("No data available for selected date range.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue", f"${filtered['line_revenue'].sum():,.0f}")
col2.metric("Units Sold", f"{int(filtered['quantity'].sum()):,}")
col3.metric("Orders", f"{filtered['order_id'].nunique():,}")
col4.metric("Active Customers", f"{filtered['customer'].nunique():,}")

st.header("Revenue Trend")
daily_revenue = filtered.groupby(filtered["date"].dt.date)["line_revenue"].sum().reset_index()
st.plotly_chart(px.line(daily_revenue, x="date", y="line_revenue"), use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Top 15 Products by Revenue")
    top_products = (
        filtered.groupby("product")["line_revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(15)
        .reset_index()
    )
    st.plotly_chart(
        px.bar(top_products, x="line_revenue", y="product", orientation="h"),
        use_container_width=True,
    )

with right:
    st.subheader("Financial Status Mix")
    status_df = filtered.groupby("financial_status")["order_id"].nunique().reset_index()
    st.plotly_chart(px.pie(status_df, names="financial_status", values="order_id"), use_container_width=True)

st.header("Inventory Risk Monitor")
recent_cutoff = datetime.now() - timedelta(days=30)
recent_sales = sales_df[sales_df["date"] >= recent_cutoff]
recent_variants = set(recent_sales["variant_id"].dropna().tolist())

risk_items = inventory_df[
    (inventory_df["variant_id"].isin(recent_variants)) & (inventory_df["stock"] <= 0)
]

dead_cutoff = datetime.now() - timedelta(days=60)
active_variants_60 = set(sales_df[sales_df["date"] >= dead_cutoff]["variant_id"].dropna().tolist())
dead_inventory = inventory_df[
    (~inventory_df["variant_id"].isin(active_variants_60)) & (inventory_df["stock"] > 0)
]

inv_col1, inv_col2 = st.columns(2)
with inv_col1:
    st.subheader("Out of Stock + Sold in 30 Days")
    st.dataframe(risk_items, use_container_width=True)

with inv_col2:
    st.subheader("Dead Inventory (No Sales in 60 Days)")
    st.dataframe(dead_inventory, use_container_width=True)

st.header("Top Customers")
top_customers = (
    filtered.groupby("customer")["line_revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
    .reset_index()
)
st.plotly_chart(
    px.bar(top_customers, x="line_revenue", y="customer", orientation="h"),
    use_container_width=True,
)
