# Queen of Sparkles — Shopify Analytics App

A professional, one-command analytics workflow for:
- syncing **orders / products / customers** from Shopify,
- launching a polished Streamlit dashboard,
- surfacing sales + inventory insights your leadership team can act on.

## What this dashboard shows
- Revenue, order, customer, and units-sold KPI cards.
- Revenue trend over time.
- Top products by revenue.
- Financial status mix.
- Inventory risk monitor:
  - sold recently but now out of stock,
  - dead inventory (stock with no sales in 60 days).
- Top customer leaderboard.

## Setup (one-time)
From this folder:

```bash
python -m pip install -r requirements.txt
```

Create `.env` from `.env.example` and fill in your values.

## Run
Primary command (sync + dashboard):

```bash
python run_qos_analytics.py
```

Optional modes:

```bash
python run_qos_analytics.py --sync-only
python run_qos_analytics.py --dashboard-only
```

## Shopify API access needed from your team
You will need these values from your Shopify admin/private app setup:
- `SHOP_DOMAIN` (example: `queenofsparkles.myshopify.com`)
- `SHOPIFY_ACCESS_TOKEN` (Admin API access token)
- optional `API_VERSION` (default in code is `2024-10`)

Recommended Admin API scopes:
- `read_orders`
- `read_products`
- `read_customers`

## Data output
Synced JSON files are stored in `data/`:
- `orders_full.json`
- `products_full.json`
- `customers_full.json`
