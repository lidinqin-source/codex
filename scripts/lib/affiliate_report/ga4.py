from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def refresh_metadata(output_dir: Path) -> dict[str, Any]:
    path = output_dir / "platform_refresh_status.csv"
    if not path.exists():
        return {"status": "missing", "rows": 0, "source": "platform_refresh_status.csv"}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if (row.get("platform") or "").strip().lower() == "ga4":
                return {
                    "status": row.get("status", ""),
                    "rows": int(float(row.get("rows") or 0)),
                    "note": row.get("note", ""),
                    "source": "platform_refresh_status.csv",
                }
    return {"status": "missing", "rows": 0, "source": "platform_refresh_status.csv"}
