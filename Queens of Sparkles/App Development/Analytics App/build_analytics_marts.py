from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


def _read_json(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text())


def build_marts(data_dir: Path) -> dict[str, int]:
    orders = _read_json(data_dir / "orders_full.json")
    products = _read_json(data_dir / "products_full.json")
    customers = _read_json(data_dir / "customers_full.json")

    marts_dir = data_dir / "marts"
    marts_dir.mkdir(parents=True, exist_ok=True)

    order_lines_rows: list[dict[str, Any]] = []
    for order in orders:
        order_id = order.get("id")
        created_at = order.get("created_at")
        financial_status = order.get("financial_status")
        fulfillment_status = order.get("fulfillment_status")
        customer = order.get("customer") or {}
        customer_id = customer.get("id")
        customer_email = customer.get("email") or "Guest"

        for line in order.get("line_items", []):
            quantity = int(line.get("quantity") or 0)
            price = float(line.get("price") or 0)
            order_lines_rows.append(
                {
                    "order_id": order_id,
                    "created_at": created_at,
                    "financial_status": financial_status,
                    "fulfillment_status": fulfillment_status,
                    "customer_id": customer_id,
                    "customer_email": customer_email,
                    "product_id": line.get("product_id"),
                    "variant_id": line.get("variant_id"),
                    "sku": line.get("sku"),
                    "product_name": line.get("name"),
                    "variant_name": line.get("variant_title"),
                    "quantity": quantity,
                    "unit_price": price,
                    "line_revenue": quantity * price,
                }
            )

    fact_order_lines = pd.DataFrame(order_lines_rows)
    if not fact_order_lines.empty:
        fact_order_lines["created_at"] = pd.to_datetime(fact_order_lines["created_at"], errors="coerce")

    products_rows: list[dict[str, Any]] = []
    for product in products:
        for variant in product.get("variants", []):
            products_rows.append(
                {
                    "product_id": product.get("id"),
                    "product_title": product.get("title"),
                    "product_type": product.get("product_type"),
                    "vendor": product.get("vendor"),
                    "variant_id": variant.get("id"),
                    "variant_title": variant.get("title"),
                    "sku": variant.get("sku"),
                    "price": float(variant.get("price") or 0),
                    "inventory_quantity": int(variant.get("inventory_quantity") or 0),
                }
            )

    dim_products = pd.DataFrame(products_rows)

    customer_rows = []
    for customer in customers:
        customer_rows.append(
            {
                "customer_id": customer.get("id"),
                "email": customer.get("email"),
                "first_name": customer.get("first_name"),
                "last_name": customer.get("last_name"),
                "orders_count": customer.get("orders_count"),
                "total_spent": float(customer.get("total_spent") or 0),
                "state": customer.get("state"),
                "created_at": customer.get("created_at"),
            }
        )

    dim_customers = pd.DataFrame(customer_rows)
    if not dim_customers.empty:
        dim_customers["created_at"] = pd.to_datetime(dim_customers["created_at"], errors="coerce")

    if not fact_order_lines.empty:
        daily_sales = (
            fact_order_lines.assign(order_date=fact_order_lines["created_at"].dt.date)
            .groupby("order_date", as_index=False)
            .agg(
                revenue=("line_revenue", "sum"),
                units_sold=("quantity", "sum"),
                orders=("order_id", "nunique"),
                active_customers=("customer_email", "nunique"),
            )
        )
    else:
        daily_sales = pd.DataFrame(columns=["order_date", "revenue", "units_sold", "orders", "active_customers"])

    fact_order_lines.to_csv(marts_dir / "fact_order_lines.csv", index=False)
    dim_products.to_csv(marts_dir / "dim_products.csv", index=False)
    dim_customers.to_csv(marts_dir / "dim_customers.csv", index=False)
    daily_sales.to_csv(marts_dir / "daily_sales.csv", index=False)

    return {
        "fact_order_lines": len(fact_order_lines),
        "dim_products": len(dim_products),
        "dim_customers": len(dim_customers),
        "daily_sales": len(daily_sales),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build analysis-ready marts from Shopify JSON.")
    parser.add_argument("--data-dir", default="data", help="Directory containing Shopify JSON exports")
    args = parser.parse_args()

    stats = build_marts(Path(args.data_dir))
    print("Built analytics marts:")
    for name, row_count in stats.items():
        print(f"- {name}: {row_count} rows")


if __name__ == "__main__":
    main()
