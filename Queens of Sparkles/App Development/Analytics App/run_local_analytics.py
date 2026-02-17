from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from build_analytics_marts import build_marts
from data_quality_check import run_quality_checks

BASE_DIR = Path(__file__).parent


def launch_dashboard() -> None:
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "qos_dashboard.py"],
        cwd=BASE_DIR,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local analytics workflow using existing JSON exports (no Shopify sync)."
    )
    parser.add_argument("--data-dir", default="data", help="Directory with orders/products/customers JSON")
    parser.add_argument("--max-stale-days", type=int, default=3, help="Data freshness threshold in days")
    parser.add_argument("--checks-only", action="store_true", help="Only run data quality checks")
    parser.add_argument("--build-only", action="store_true", help="Only run mart build")
    parser.add_argument(
        "--dashboard-only",
        action="store_true",
        help="Launch dashboard only (skip checks and mart build)",
    )
    args = parser.parse_args()

    if args.checks_only and args.build_only:
        raise SystemExit("Choose only one: --checks-only or --build-only")

    data_dir = BASE_DIR / args.data_dir

    if not args.dashboard_only and not args.build_only:
        results, all_passed = run_quality_checks(data_dir, max_stale_days=args.max_stale_days)
        for result in results:
            icon = "PASS" if result.passed else "FAIL"
            print(f"[{icon}] {result.name}: {result.details}")
        if not all_passed:
            raise SystemExit("Data quality checks failed.")

    if args.checks_only:
        return

    if not args.dashboard_only:
        stats = build_marts(data_dir)
        print(f"Built marts: {stats}")

    if not args.build_only:
        launch_dashboard()


if __name__ == "__main__":
    main()
