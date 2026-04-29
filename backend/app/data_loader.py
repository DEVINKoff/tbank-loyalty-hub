from __future__ import annotations

import csv
import os
from functools import lru_cache
from pathlib import Path
from typing import Any


DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


@lru_cache(maxsize=1)
def load_data(data_dir: str | os.PathLike[str] | None = None) -> dict[str, list[dict[str, Any]]]:
    """Load hackathon CSV files.

    The cache keeps the API fast in demo mode. For production, replace this
    layer with a repository class backed by PostgreSQL or ClickHouse.
    """

    root = Path(data_dir) if data_dir else DEFAULT_DATA_DIR
    required_files = {
        "users": "Users.csv",
        "offers": "Offers.csv",
        "loyalty_history": "LoyaltyHistory.csv",
        "accounts": "Accounts.csv",
        "loyalty_programs": "LoyaltyPrograms.csv",
    }

    missing = [filename for filename in required_files.values() if not (root / filename).exists()]
    if missing:
        raise FileNotFoundError(f"Missing CSV files in {root}: {', '.join(missing)}")

    data = {key: _read_csv(root / filename) for key, filename in required_files.items()}

    for account in data["accounts"]:
        account["current_balance"] = float(account["current_balance"])

    for offer in data["offers"]:
        offer["cashback_percent"] = float(offer["cashback_percent"])

    for item in data["loyalty_history"]:
        item["cashback_amount"] = float(item["cashback_amount"])

    return data
