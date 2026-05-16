#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from affiliate_report.manifest import ManifestError, load_manifest, resolve_output_dir, validate_manifest
from affiliate_report.reconciliation import count_reconciliation, distinct_current_transactions
from affiliate_report.report_bundle import (
    load_bundle,
    source_files,
    validate_bundle_schema,
)
from affiliate_report.targets import compute_target_math


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a manifest-driven affiliate report run.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--quiet", action="store_true", default=False)
    parser.add_argument("--schema-only", action="store_true", help="Only validate manifest/schema readiness.")
    return parser.parse_args()


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def parse_row_date(value: str) -> date | None:
    value = (value or "").strip()
    try:
        if len(value) == 8 and value.isdigit():
            return date(int(value[:4]), int(value[4:6]), int(value[6:]))
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def row_float(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key) or 0)
    except ValueError:
        return 0.0


def current_csv_revenue(rows: list[dict[str, str]]) -> float:
    seen: set[str] = set()
    total = 0.0
    for row in rows:
        if (row.get("period") or "").strip() != "current":
            continue
        tx = (row.get("transactionId") or "").strip()
        if tx and tx in seen:
            continue
        if tx:
            seen.add(tx)
        total += row_float(row, "purchaseRevenue")
    return total


def ytd_csv_revenue(rows: list[dict[str, str]]) -> float:
    seen: set[str] = set()
    total = 0.0
    for row in rows:
        period = (row.get("period") or "").strip()
        if period not in {"current", "previous", "ytd_other"}:
            continue
        tx = (row.get("transactionId") or "").strip()
        if tx and tx in seen:
            continue
        if tx:
            seen.add(tx)
        total += row_float(row, "purchaseRevenue")
    return total


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, **metadata: Any) -> None:
    checks.append({"name": name, "status": "passed" if passed else "failed", **metadata})


def file_status(output_dir: Path, rel: str) -> dict[str, Any]:
    path = output_dir / rel
    return {
        "file": rel,
        "exists": path.exists(),
        "bytes": path.stat().st_size if path.exists() else 0,
    }


def validate_date_ranges(rows: list[dict[str, str]], manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    scope = manifest["scope"]
    current_start = date.fromisoformat(scope["current_range"]["start"])
    current_end = date.fromisoformat(scope["current_range"]["end"])
    previous_start = date.fromisoformat(scope["comparison_range"]["start"])
    previous_end = date.fromisoformat(scope["comparison_range"]["end"])
    ytd_start = date.fromisoformat(scope["ytd_range"]["start"])
    ytd_end = date.fromisoformat(scope["ytd_range"]["end"])
    failures: list[str] = []
    for index, row in enumerate(rows, start=2):
        period = (row.get("period") or "").strip()
        row_date = parse_row_date(row.get("date", ""))
        if row_date is None:
            failures.append(f"row {index}: invalid date {row.get('date')!r}")
            continue
        if period == "current" and not (current_start <= row_date <= current_end):
            failures.append(f"row {index}: current row outside current_range")
        elif period == "previous" and not (previous_start <= row_date <= previous_end):
            failures.append(f"row {index}: previous row outside comparison_range")
        elif period == "ytd_other" and not (ytd_start <= row_date <= ytd_end):
            failures.append(f"row {index}: ytd_other row outside ytd_range")
    return not failures, failures[:10]


def validate_logs(output_dir: Path, manifest: dict[str, Any]) -> tuple[bool, list[str]]:
    failures: list[str] = []
    refresh_end = manifest["platforms"]["post_period_refresh_end"]

    impact_rows = read_csv_rows(output_dir / "impact_pull_log.csv")
    if not impact_rows:
        failures.append("impact_pull_log.csv missing or empty")
    for index, row in enumerate(impact_rows, start=2):
        for field in ["status", "rows_returned", "pages", "start_date", "end_date"]:
            if row.get(field) in {None, ""}:
                failures.append(f"impact_pull_log.csv row {index}: missing {field}")
        if row.get("end_date", "") < refresh_end:
            failures.append(f"impact_pull_log.csv row {index}: end_date before post_period_refresh_end")
        if "pagination" not in " ".join(row.keys()).lower() and not row.get("pages"):
            failures.append(f"impact_pull_log.csv row {index}: pagination/pages not recorded")

    cj_rows = read_csv_rows(output_dir / "cj_pull_log.csv")
    lenses = {row.get("lens") for row in cj_rows}
    if not {"event_date", "posting_date"}.issubset(lenses):
        failures.append("cj_pull_log.csv must include event_date and posting_date lenses")
    for index, row in enumerate(cj_rows, start=2):
        for field in ["status", "rows", "lens", "pages"]:
            if row.get(field) in {None, ""}:
                failures.append(f"cj_pull_log.csv row {index}: missing {field}")
        note = (row.get("note") or "").lower()
        if int(float(row.get("rows") or 0)) == 0 and "no activity" in note:
            failures.append(f"cj_pull_log.csv row {index}: zero-row result is described as no activity")

    for rel in ["platform_refresh_status.csv", "impact_pull_log.csv", "cj_pull_log.csv"]:
        for index, row in enumerate(read_csv_rows(output_dir / rel), start=2):
            joined = " ".join(str(value).lower() for value in row.values())
            row_count = row.get("rows") or row.get("rows_returned") or "1"
            try:
                count = int(float(row_count or 0))
            except ValueError:
                count = 1
            if count == 0 and "no activity" in joined:
                failures.append(f"{rel} row {index}: zero-row result must not be called no activity")

    return not failures, failures[:12]


def stable_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload.setdefault("self_check", {})["file"] = path.name
    payload["self_check"]["exists"] = True
    payload["self_check"]["bytes"] = 0
    for _ in range(8):
        text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        size = len(text.encode("utf-8"))
        if payload["self_check"]["bytes"] == size:
            path.write_text(text, encoding="utf-8")
            return
        payload["self_check"]["bytes"] = size
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest.resolve()
    checks: list[dict[str, Any]] = []
    failed_checks: list[str] = []

    try:
        manifest = load_manifest(manifest_path)
        validate_manifest(manifest, ROOT)
    except ManifestError as exc:
        summary = {
            "status": "failed",
            "failed_checks": ["manifest_schema"],
            "error": str(exc),
        }
        if not args.quiet:
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(summary, ensure_ascii=False))
        return 2

    output_dir = resolve_output_dir(manifest, ROOT)
    if args.schema_only:
        summary = {"status": "passed", "failed_checks": [], "output_dir": str(output_dir)}
        print(json.dumps(summary, ensure_ascii=False))
        return 0

    try:
        bundle = load_bundle(output_dir)
    except ManifestError as exc:
        summary = {
            "status": "failed",
            "failed_checks": ["report_bundle_exists"],
            "error": str(exc),
            "output_dir": str(output_dir),
        }
        stable_write_json(output_dir / "validation_summary.json", summary)
        print(json.dumps(summary, ensure_ascii=False))
        return 2

    bundle_schema_failures = validate_bundle_schema(bundle, ROOT)
    add_check(checks, "report_bundle_schema", not bundle_schema_failures, failures=bundle_schema_failures)

    source_registry = source_files(bundle)
    required_source_keys = {
        "run_manifest",
        "bundle",
        "insights",
        "actions",
        "html",
        "markdown",
        "ga4_transaction_classification",
        "unified_affiliate_orders",
        "reconciliation",
        "platform_refresh",
        "validation",
        "goal_pacing",
        "target_source",
    }
    missing_source_keys = sorted(required_source_keys - set(source_registry))
    add_check(checks, "report_source_files_complete", not missing_source_keys, missing=missing_source_keys)

    required_files = sorted(set(source_registry.values()) | {
        "report_bundle.json",
        "insights.json",
        "actions.csv",
        "goal_pacing_summary.csv",
        "goal_pacing_summary.json",
        "ga4_transaction_classification.csv",
        "unified_affiliate_orders.csv",
        "affiliate_order_reconciliation.csv",
        "platform_refresh_status.csv",
        "impact_pull_log.csv",
        "cj_pull_log.csv",
        "report.html",
        "report.md",
    })
    file_checks = [file_status(output_dir, rel) for rel in required_files]
    missing_or_empty = [item["file"] for item in file_checks if not item["exists"] or item["bytes"] <= 0]
    add_check(checks, "required_files_exist_nonempty", not missing_or_empty, missing_or_empty=missing_or_empty, files=file_checks)

    unified_path = output_dir / "unified_affiliate_orders.csv"
    unified_rows = read_csv_rows(unified_path)
    distinct_current = distinct_current_transactions(unified_path)
    csv_revenue = current_csv_revenue(unified_rows)
    bundle_affiliate = bundle.get("metrics", {}).get("affiliate_current", {})
    bundle_orders = int(bundle_affiliate.get("orders") or 0)
    bundle_revenue = float(bundle_affiliate.get("revenue") or 0)
    add_check(
        checks,
        "current_affiliate_orders_distinct_transaction_id",
        bundle_orders == len(distinct_current),
        bundle_orders=bundle_orders,
        csv_distinct_current_orders=len(distinct_current),
    )
    add_check(
        checks,
        "report_bundle_metrics_match_csv",
        abs(bundle_revenue - csv_revenue) <= 0.02,
        bundle_revenue=round(bundle_revenue, 6),
        csv_revenue=round(csv_revenue, 6),
    )

    computed_target = compute_target_math(manifest, bundle_revenue, ytd_csv_revenue(unified_rows))
    target_current = bundle.get("target_summary", {}).get("current", {})
    target_failures: list[str] = []
    for key in ["current_period_target", "current_period_pacing", "ytd_target", "ytd_pacing"]:
        expected = float(computed_target[key])
        observed = float(target_current.get(key) or 0)
        tolerance = 0.02 if "target" in key else 0.0005
        if abs(expected - observed) > tolerance:
            target_failures.append(f"{key}: expected {expected}, observed {observed}")
    add_check(checks, "target_math_full_month_mtd_ytd", not target_failures, failures=target_failures, computed=computed_target)

    date_ok, date_failures = validate_date_ranges(unified_rows, manifest)
    add_check(checks, "ga4_date_ranges_not_mixed", date_ok, failures=date_failures)

    log_ok, log_failures = validate_logs(output_dir, manifest)
    add_check(checks, "impact_cj_logs_complete", log_ok, failures=log_failures)

    recon_counts = count_reconciliation(output_dir / "affiliate_order_reconciliation.csv")
    bundle_recon = bundle.get("reconciliation_summary", {})
    recon_failures = [
        key for key in ["matched", "ga4_only", "platform_only"]
        if int(bundle_recon.get(key) or 0) != int(recon_counts.get(key) or 0)
    ]
    add_check(checks, "reconciliation_counts_match_csv", not recon_failures, failures=recon_failures, csv_counts=recon_counts)

    failed_checks = [check["name"] for check in checks if check["status"] != "passed"]
    status = "passed" if not failed_checks else "failed"
    summary = {
        "status": status,
        "failed_checks": failed_checks,
        "output_dir": str(output_dir),
        "checks": checks,
        "compact_metrics": {
            "affiliate_revenue": round(bundle_revenue, 2),
            "affiliate_orders": bundle_orders,
            "reconciliation": recon_counts,
        },
    }
    stable_write_json(output_dir / "validation_summary.json", summary)

    compact = {
        "status": status,
        "failed_checks": failed_checks,
        "output_dir": str(output_dir),
        "validation_summary": str(output_dir / "validation_summary.json"),
    }
    if args.quiet:
        print(json.dumps(compact, ensure_ascii=False))
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
