from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


def count_reconciliation(path: Path) -> dict[str, int]:
    counts: Counter[str] = Counter()
    if not path.exists():
        return {"matched": 0, "ga4_only": 0, "platform_only": 0}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            status = (row.get("reconciliation_status") or "").strip()
            if status:
                counts[status] += 1
    return {
        "matched": counts.get("matched", 0),
        "ga4_only": counts.get("ga4_only", 0),
        "platform_only": counts.get("platform_only", 0),
    }


def distinct_current_transactions(path: Path) -> set[str]:
    transactions: set[str] = set()
    if not path.exists():
        return transactions
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if (row.get("period") or "").strip() == "current":
                tx = (row.get("transactionId") or "").strip()
                if tx:
                    transactions.add(tx)
    return transactions


def current_revenue(path: Path) -> float:
    total = 0.0
    seen: set[str] = set()
    if not path.exists():
        return total
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if (row.get("period") or "").strip() != "current":
                continue
            tx = (row.get("transactionId") or "").strip()
            if tx and tx in seen:
                continue
            if tx:
                seen.add(tx)
            try:
                total += float(row.get("purchaseRevenue") or 0)
            except ValueError:
                continue
    return total
