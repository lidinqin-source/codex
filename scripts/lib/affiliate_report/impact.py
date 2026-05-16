from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def pull_metadata(output_dir: Path) -> dict[str, Any]:
    path = output_dir / "impact_pull_log.csv"
    rows = 0
    pages = 0
    statuses: set[str] = set()
    if not path.exists():
        return {"status": "missing", "rows": 0, "pages": 0, "source": "impact_pull_log.csv"}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            rows += int(float(row.get("rows_returned") or row.get("rows") or 0))
            pages += int(float(row.get("pages") or 0))
            if row.get("status"):
                statuses.add(str(row["status"]))
    status = "fresh" if statuses == {"fresh"} else "partial" if statuses else "unknown"
    return {"status": status, "rows": rows, "pages": pages, "source": "impact_pull_log.csv"}
