from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="QOS Operations Dashboard", layout="wide")
st.title("Queen of Sparkles — Revenue & Inventory Command Center")
st.caption("Operational analytics from local Shopify exports (no live API sync required).")

BASE_DIR = Path(__file__).parent
MARTS_DIR = BASE_DIR / "data" / "marts"


@st.cache_data
def load_marts() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    required_files = {
        "fact_order_lines": MARTS_DIR / "fact_order_lines.csv",
        "dim_products": MARTS_DIR / "dim_products.csv",
        "dim_customers": MARTS_DIR / "dim_customers.csv",
        "daily_sales": MARTS_DIR / "daily_sales.csv",
    }

    missing = [name for name, path in required_files.items() if not path.exists()]
    if missing:
        st.error(
            "Missing marts. Run `python run_local_analytics.py` from the Analytics App folder first. "
            f"Missing: {', '.join(missing)}"
        )
        st.stop()

    fact_order_lines = pd.read_csv(required_files["fact_order_lines"])
    dim_products = pd.read_csv(required_files["dim_products"])
    dim_customers = pd.read_csv(required_files["dim_customers"])
    daily_sales = pd.read_csv(required_files["daily_sales"])

    fact_order_lines["created_at"] = pd.to_datetime(fact_order_lines["created_at"], errors="coerce")
    return fact_order_lines, dim_products, dim_customers, daily_sales


fact_order_lines, dim_products, dim_customers, daily_sales = load_marts()
if fact_order_lines.empty:
    st.warning("No order-line records available in marts.")
    st.stop()

min_date = fact_order_lines["created_at"].min().date()
max_date = fact_order_lines["created_at"].max().date()

st.sidebar.header("Filters")
default_start = max(max_date - timedelta(days=30), min_date)
start_date, end_date = st.sidebar.date_input(
    "Date range",
    value=(default_start, max_date),
    min_value=min_date,
    max_value=max_date,
)

vendor_options = sorted([v for v in dim_products["vendor"].dropna().unique().tolist() if v])
selected_vendors = st.sidebar.multiselect("Vendors", options=vendor_options, default=vendor_options)

filtered = fact_order_lines[
    (fact_order_lines["created_at"].dt.date >= start_date)
    & (fact_order_lines["created_at"].dt.date <= end_date)
].copy()

if selected_vendors and not dim_products.empty:
    allowed_variants = set(
        dim_products[dim_products["vendor"].isin(selected_vendors)]["variant_id"].dropna().tolist()
    )
    filtered = filtered[filtered["variant_id"].isin(allowed_variants)]

if filtered.empty:
    st.warning("No data for selected filter combination.")
    st.stop()

# KPI section
revenue = filtered["line_revenue"].sum()
orders = filtered["order_id"].nunique()
units = filtered["quantity"].sum()
active_customers = filtered["customer_email"].nunique()
aov = revenue / orders if orders else 0

customer_orders = filtered.groupby("customer_email")["order_id"].nunique()
repeat_customer_rate = (
    (customer_orders >= 2).sum() / len(customer_orders) if len(customer_orders) > 0 else 0
)

status_mix = filtered.groupby("financial_status")["order_id"].nunique().sort_values(ascending=False)
paid_ratio = (
    status_mix.get("paid", 0) / status_mix.sum() if status_mix.sum() else 0
)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Revenue", f"${revenue:,.0f}")
k2.metric("Orders", f"{orders:,}")
k3.metric("Units Sold", f"{int(units):,}")
k4.metric("AOV", f"${aov:,.2f}")
k5.metric("Repeat Customer Rate", f"{repeat_customer_rate:.1%}")
k6.metric("Paid Order Ratio", f"{paid_ratio:.1%}")

tab_exec, tab_products, tab_inventory, tab_customers = st.tabs(
    ["Executive", "Product Intelligence", "Inventory Risk", "Customer Intelligence"]
)

with tab_exec:
    st.subheader("Daily Revenue")
    daily = (
        filtered.assign(order_date=filtered["created_at"].dt.date)
        .groupby("order_date", as_index=False)["line_revenue"]
        .sum()
    )
    st.plotly_chart(
        px.line(daily, x="order_date", y="line_revenue", markers=True, title="Revenue Trend"),
        use_container_width=True,
    )

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            px.pie(
                filtered.groupby("financial_status", as_index=False)["order_id"].nunique(),
                names="financial_status",
                values="order_id",
                title="Order Financial Status Mix",
            ),
            use_container_width=True,
        )
    with right:
        weekday = filtered.assign(weekday=filtered["created_at"].dt.day_name())
        weekday_agg = weekday.groupby("weekday", as_index=False)["line_revenue"].sum()
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_agg["weekday"] = pd.Categorical(weekday_agg["weekday"], categories=weekday_order, ordered=True)
        weekday_agg = weekday_agg.sort_values("weekday")
        st.plotly_chart(
            px.bar(weekday_agg, x="weekday", y="line_revenue", title="Revenue by Day of Week"),
            use_container_width=True,
        )

with tab_products:
    merged = filtered.merge(
        dim_products[["variant_id", "vendor", "product_type"]], on="variant_id", how="left"
    )

    top_products = (
        merged.groupby("product_name", as_index=False)
        .agg(revenue=("line_revenue", "sum"), units=("quantity", "sum"), orders=("order_id", "nunique"))
        .sort_values("revenue", ascending=False)
        .head(20)
    )
    st.plotly_chart(
        px.bar(top_products, x="revenue", y="product_name", orientation="h", title="Top 20 Products by Revenue"),
        use_container_width=True,
    )

    vendor_perf = (
        merged.groupby("vendor", as_index=False)
        .agg(revenue=("line_revenue", "sum"), units=("quantity", "sum"), orders=("order_id", "nunique"))
        .sort_values("revenue", ascending=False)
    )
    st.dataframe(vendor_perf, use_container_width=True)

with tab_inventory:
    recent_cutoff = pd.Timestamp(datetime.now() - timedelta(days=30))
    recent = fact_order_lines[fact_order_lines["created_at"] >= recent_cutoff]

    velocity = (
        recent.groupby("variant_id", as_index=False)
        .agg(units_30d=("quantity", "sum"), revenue_30d=("line_revenue", "sum"))
    )
    inv = dim_products[["variant_id", "product_title", "variant_title", "sku", "inventory_quantity"]].copy()
    risk = inv.merge(velocity, on="variant_id", how="left").fillna({"units_30d": 0, "revenue_30d": 0})
    risk["days_of_cover"] = risk.apply(
        lambda row: (row["inventory_quantity"] / (row["units_30d"] / 30)) if row["units_30d"] > 0 else 999,
        axis=1,
    )
    risk["risk_score"] = risk.apply(
        lambda row: row["units_30d"] * 2 - max(row["inventory_quantity"], 0), axis=1
    )

    at_risk = (
        risk[(risk["units_30d"] > 0) & (risk["inventory_quantity"] <= (risk["units_30d"] * 0.6))]
        .sort_values(["risk_score", "units_30d"], ascending=False)
        .head(20)
    )

    st.subheader("Top 20 At-Risk SKUs (30-day velocity vs current stock)")
    st.dataframe(
        at_risk[
            [
                "sku",
                "product_title",
                "variant_title",
                "inventory_quantity",
                "units_30d",
                "revenue_30d",
                "days_of_cover",
                "risk_score",
            ]
        ],
        use_container_width=True,
    )

    st.plotly_chart(
        px.scatter(
            risk,
            x="units_30d",
            y="inventory_quantity",
            hover_data=["sku", "product_title", "variant_title"],
            title="Inventory Positioning: 30-Day Velocity vs On-Hand Stock",
        ),
        use_container_width=True,
    )

with tab_customers:
    customer_perf = (
        filtered.groupby("customer_email", as_index=False)
        .agg(revenue=("line_revenue", "sum"), orders=("order_id", "nunique"), units=("quantity", "sum"))
        .sort_values("revenue", ascending=False)
    )

    customer_perf["segment"] = pd.cut(
        customer_perf["orders"],
        bins=[0, 1, 3, 999],
        labels=["One-time", "Repeat", "Loyal"],
    )

    left, right = st.columns(2)
    with left:
        st.plotly_chart(
            px.bar(
                customer_perf.head(20),
                x="revenue",
                y="customer_email",
                orientation="h",
                title="Top 20 Customers by Revenue",
            ),
            use_container_width=True,
        )
    with right:
        seg = customer_perf.groupby("segment", as_index=False)["customer_email"].count()
        seg.rename(columns={"customer_email": "customers"}, inplace=True)
        st.plotly_chart(
            px.pie(seg, names="segment", values="customers", title="Customer Mix by Frequency Segment"),
            use_container_width=True,
        )

    st.dataframe(customer_perf.head(50), use_container_width=True)
