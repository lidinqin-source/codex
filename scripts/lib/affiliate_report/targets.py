from __future__ import annotations

import calendar
from datetime import date
from typing import Any


def _parse(value: str) -> date:
    return date.fromisoformat(value)


def _number(value: Any) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    text = str(value or "").strip()
    if not text:
        return 0.0
    negative = text.startswith("(") and text.endswith(")")
    text = text.strip("()").replace("$", "").replace(",", "").replace("%", "").strip()
    try:
        number = float(text or 0)
        return -number if negative else number
    except ValueError:
        return 0.0


def compute_target_math(manifest: dict[str, Any], actual_revenue: float, ytd_actual: float | None = None) -> dict[str, float]:
    """Compute the manifest target math without reading generated artifacts."""
    scope = manifest["scope"]
    target = manifest["target"]
    annual_goal = _number(target.get("annual_affiliate_gmv_goal"))
    denominator = _number(target.get("denominator_net_sales"))
    current_start = _parse(scope["current_range"]["start"])
    current_end = _parse(scope["current_range"]["end"])
    monthly_rows = [row for row in target.get("monthly_rows", []) if row.get("period_type") == "month"]

    month_targets: dict[int, float] = {}
    for row in monthly_rows:
        month_number = int(row["month_number"])
        if target.get("source_type") == "google_sheet" and row.get("affiliate_revenue_target") not in {None, ""}:
            month_targets[month_number] = _number(row.get("affiliate_revenue_target"))
        else:
            net_sales = _number(row.get("net_sales"))
            month_targets[month_number] = annual_goal * (net_sales / denominator) if annual_goal and denominator else 0.0

    month_target = month_targets.get(current_start.month, 0.0)
    elapsed_days = (current_end - current_start).days + 1
    days_in_month = calendar.monthrange(current_start.year, current_start.month)[1]
    current_target = month_target * elapsed_days / days_in_month

    ytd_target = 0.0
    for month_number, value in month_targets.items():
        if month_number < current_start.month:
            ytd_target += value
        elif month_number == current_start.month:
            ytd_target += current_target

    return {
        "current_period_target": round(current_target, 2),
        "current_period_actual": round(actual_revenue, 2),
        "current_period_pacing": round(actual_revenue / current_target, 6) if current_target else 0.0,
        "ytd_target": round(ytd_target, 2),
        "ytd_actual": round(float(ytd_actual if ytd_actual is not None else actual_revenue), 2),
        "ytd_pacing": round(float(ytd_actual if ytd_actual is not None else actual_revenue) / ytd_target, 6) if ytd_target else 0.0,
    }
