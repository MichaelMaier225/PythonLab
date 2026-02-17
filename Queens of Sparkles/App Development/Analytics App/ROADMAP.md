# Analytics App Roadmap (from raw JSON to decision platform)

You now have the hard part done: **raw Shopify data landed** (`orders`, `products`, `customers`).
The next move is to turn this into a repeatable analytics system your team can trust.

## Phase 1 — Foundation (this week)
Goal: make your current dashboard reliable and easy to run.

1. **Establish data contracts**
   - Confirm required fields per file (e.g., `order.id`, `order.created_at`, `line_items`, `variant.inventory_quantity`, customer email/id).
   - Document assumptions and null-handling rules.

2. **Add freshness + QA checks**
   - File exists checks.
   - Row count checks (orders/customers/products not unexpectedly zero).
   - Max `created_at` freshness check.
   - Duplicate ID checks.

3. **Define KPI glossary**
   - Revenue definition (gross vs net of refunds).
   - Active customer definition.
   - Inventory risk definitions.

## Phase 2 — Data Modeling (next 1–2 weeks)
Goal: stop calculating everything directly from nested JSON.

1. Build normalized, analysis-ready tables in `data/marts/`:
   - `fact_order_lines.parquet`
   - `dim_products.parquet`
   - `dim_customers.parquet`
   - `daily_sales.parquet`

2. Add a transformation script (example command):
   - `python build_analytics_marts.py`

3. Version your schema:
   - Save model version + run timestamp in a metadata file.

## Phase 3 — BI Expansion (weeks 2–4)
Goal: answer leadership questions quickly.

1. Add dashboard pages:
   - Executive overview.
   - Product performance + markdown candidates.
   - Customer cohorts (new vs repeat).
   - Inventory buy-planning signals.

2. Add drill-down filters:
   - Product type, vendor, collection, channel, date, status.

3. Add export actions:
   - “Download at-risk SKUs” CSV.
   - “Download weekly KPI snapshot” CSV.

## Phase 4 — Forecasting + Alerts (month 2)
Goal: proactive operations.

1. Demand forecasting per SKU/week.
2. Reorder point recommendations.
3. Slack/email alerts for:
   - fast sellers with low stock,
   - dead inventory over threshold,
   - sudden revenue drops.

## Phase 5 — Productionization (month 2+)
Goal: make this a real internal product.

1. Scheduled sync + transforms (cron/GitHub Actions).
2. Environment separation (dev/prod).
3. Access controls and secrets management.
4. Monitoring (job success, freshness, anomaly alerts).

---

## Immediate next sprint (start here)
If you're unsure what to do **today**, do these 5 items in order:

1. Create `data_quality_check.py` and fail on missing/stale/duplicate data.
2. Create `build_analytics_marts.py` to flatten order line items.
3. Point the dashboard to marts instead of raw nested JSON.
4. Add one new KPI: **Repeat Customer Rate**.
5. Add one new table: **Top 20 At-Risk SKUs by 30-day velocity vs current stock**.

That sequence gives you a “big project” path while still shipping value every day.
