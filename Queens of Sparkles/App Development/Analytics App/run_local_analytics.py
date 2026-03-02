from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from data_quality_check import run_quality_checks

BASE_DIR = Path(__file__).parent


def launch_dashboard() -> None:
    print("Launching dashboard at http://localhost:8501 ...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "qos_dashboard.py",
            "--server.address=127.0.0.1",
            "--server.port=8501",
        ],
        cwd=BASE_DIR,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local analytics workflow using existing JSON exports (no Shopify sync)."
    )
    parser.add_argument("--data-dir", default="data", help="Directory with orders/products/customers JSON")
    parser.add_argument("--checks-only", action="store_true", help="Only run data quality checks")
    parser.add_argument(
        "--no-checks",
        action="store_true",
        help="Skip all data quality checks and use already-downloaded data as-is.",
    )
    parser.add_argument("--build-only", action="store_true", help="Only run mart build")
    parser.add_argument(
        "--dashboard-only",
        action="store_true",
        help="Launch dashboard only (skip checks and mart build)",
    )
    args = parser.parse_args()

    if args.checks_only and args.build_only:
        raise SystemExit("Choose only one: --checks-only or --build-only")
    if args.checks_only and args.no_checks:
        raise SystemExit("Choose only one: --checks-only or --no-checks")

    data_dir = BASE_DIR / args.data_dir

    if not args.no_checks and not args.dashboard_only and not args.build_only:
        results, all_passed = run_quality_checks(data_dir, check_freshness=False)
        for result in results:
            icon = "PASS" if result.passed else "FAIL"
            print(f"[{icon}] {result.name}: {result.details}")
        if not all_passed:
            raise SystemExit("Data quality checks failed.")

    if args.checks_only:
        return

    if not args.dashboard_only:
        from build_analytics_marts import build_marts

        stats = build_marts(data_dir)
        print(f"Built marts: {stats}")

    if not args.build_only:
        launch_dashboard()


if __name__ == "__main__":
    main()
