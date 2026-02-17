from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


@dataclass
class CheckResult:
    name: str
    passed: bool
    details: str


def _load_json(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text())


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def run_quality_checks(data_dir: Path, max_stale_days: int = 3) -> tuple[list[CheckResult], bool]:
    files = {
        "orders": data_dir / "orders_full.json",
        "products": data_dir / "products_full.json",
        "customers": data_dir / "customers_full.json",
    }

    results: list[CheckResult] = []
    loaded: dict[str, list[dict[str, Any]]] = {}

    for key, path in files.items():
        if not path.exists():
            results.append(CheckResult(f"{key}_file_exists", False, f"Missing file: {path}"))
            continue
        loaded[key] = _load_json(path)
        results.append(CheckResult(f"{key}_file_exists", True, f"Found {path.name}"))

    if len(loaded) != len(files):
        return results, False

    for key, rows in loaded.items():
        results.append(
            CheckResult(
                f"{key}_row_count",
                len(rows) > 0,
                f"{key} rows={len(rows)}",
            )
        )

    order_ids = [str(order.get("id")) for order in loaded["orders"] if order.get("id")]
    dup_order_count = len(order_ids) - len(set(order_ids))
    results.append(
        CheckResult(
            "orders_duplicate_ids",
            dup_order_count == 0,
            f"duplicate_order_ids={dup_order_count}",
        )
    )

    customer_ids = [str(customer.get("id")) for customer in loaded["customers"] if customer.get("id")]
    dup_customer_count = len(customer_ids) - len(set(customer_ids))
    results.append(
        CheckResult(
            "customers_duplicate_ids",
            dup_customer_count == 0,
            f"duplicate_customer_ids={dup_customer_count}",
        )
    )

    created_dates = [_parse_datetime(order.get("created_at")) for order in loaded["orders"]]
    created_dates = [date for date in created_dates if date]
    if created_dates:
        max_created_at = max(created_dates)
        stale_threshold = datetime.now(timezone.utc) - timedelta(days=max_stale_days)
        is_fresh = max_created_at >= stale_threshold
        results.append(
            CheckResult(
                "orders_data_freshness",
                is_fresh,
                f"latest_order={max_created_at.isoformat()} threshold={stale_threshold.isoformat()}",
            )
        )
    else:
        results.append(CheckResult("orders_data_freshness", False, "No parseable order created_at timestamps"))

    all_passed = all(result.passed for result in results)
    return results, all_passed


def main() -> None:
    parser = argparse.ArgumentParser(description="Data quality gate for local Shopify analytics JSON.")
    parser.add_argument("--data-dir", default="data", help="Directory containing Shopify JSON exports")
    parser.add_argument("--max-stale-days", type=int, default=3, help="Allowed staleness window for latest order")
    args = parser.parse_args()

    results, all_passed = run_quality_checks(Path(args.data_dir), max_stale_days=args.max_stale_days)

    print("\n=== DATA QUALITY REPORT ===")
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}: {result.details}")

    if not all_passed:
        raise SystemExit("\nData quality checks failed. Fix data inputs before launching dashboard.")

    print("\nAll quality checks passed.")


if __name__ == "__main__":
    main()
