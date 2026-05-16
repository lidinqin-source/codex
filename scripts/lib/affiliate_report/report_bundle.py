from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .manifest import ManifestError, load_schema, validate_json_schema


def load_bundle(output_dir: Path) -> dict[str, Any]:
    path = output_dir / "report_bundle.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestError(f"report_bundle.json not found in {output_dir}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"report_bundle.json is invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ManifestError("report_bundle.json root must be an object")
    return data


def validate_bundle_schema(bundle: dict[str, Any], root: Path) -> list[str]:
    schema = load_schema(root, "report_bundle.schema.json")
    return [f"{issue.path}: {issue.message}" for issue in validate_json_schema(bundle, schema)]


def source_files(bundle: dict[str, Any]) -> dict[str, str]:
    files = bundle.get("report", {}).get("source_files", {})
    return files if isinstance(files, dict) else {}


def headline_metrics(bundle: dict[str, Any]) -> dict[str, Any]:
    affiliate_current = bundle.get("metrics", {}).get("affiliate_current", {})
    target_current = bundle.get("target_summary", {}).get("current", {})
    return {
        "affiliate_revenue": round(float(affiliate_current.get("revenue") or 0), 2),
        "affiliate_orders": int(affiliate_current.get("orders") or 0),
        "mtd_target": round(float(target_current.get("current_period_target") or 0), 2),
        "mtd_pacing": round(float(target_current.get("current_period_pacing") or 0), 6),
        "ytd_target": round(float(target_current.get("ytd_target") or 0), 2),
        "ytd_pacing": round(float(target_current.get("ytd_pacing") or 0), 6),
    }


def scope_summary(bundle: dict[str, Any]) -> dict[str, str]:
    scope = bundle.get("scope", {})
    current = f"{scope.get('current_start')} to {scope.get('current_end')}"
    comparison = f"{scope.get('previous_start')} to {scope.get('previous_end')}"
    return {
        "brand": str(scope.get("brand", "")),
        "market": str(scope.get("market", "")),
        "current_range": current,
        "comparison_range": comparison,
    }


def reconciliation_summary(bundle: dict[str, Any]) -> dict[str, int]:
    raw = bundle.get("reconciliation_summary", {})
    return {
        "matched": int(raw.get("matched") or 0),
        "ga4_only": int(raw.get("ga4_only") or 0),
        "platform_only": int(raw.get("platform_only") or 0),
    }
