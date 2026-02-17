from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from shopify_sync import sync_shopify_data

BASE_DIR = Path(__file__).parent


def launch_dashboard() -> None:
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "qos_dashboard.py"],
        cwd=BASE_DIR,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="One-command workflow: sync Shopify data and launch analytics dashboard."
    )
    parser.add_argument("--sync-only", action="store_true", help="Only sync data from Shopify")
    parser.add_argument(
        "--dashboard-only", action="store_true", help="Launch dashboard without syncing first"
    )
    args = parser.parse_args()

    if args.sync_only and args.dashboard_only:
        raise SystemExit("Choose one mode: --sync-only OR --dashboard-only")

    data_dir = BASE_DIR / "data"

    if not args.dashboard_only:
        sync_shopify_data(data_dir)

    if not args.sync_only:
        launch_dashboard()


if __name__ == "__main__":
    main()
