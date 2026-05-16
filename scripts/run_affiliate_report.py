#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from affiliate_report.logging import StepLogger
from affiliate_report.manifest import (
    ManifestError,
    load_manifest,
    load_schema,
    resolve_output_dir,
    validate_json_schema,
    validate_manifest,
)
from affiliate_report.report_bundle import headline_metrics, load_bundle, reconciliation_summary, scope_summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a manifest-driven affiliate production report.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--quiet", action="store_true", default=False)
    parser.add_argument("--validate-only", action="store_true", help="Validate the manifest and exit before pulling/generating data.")
    return parser.parse_args()


def now(timezone: str) -> str:
    return datetime.now(ZoneInfo(timezone)).isoformat(timespec="seconds")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_command(command: list[str], cwd: Path, log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as handle:
        handle.write("$ " + " ".join(command) + "\n\n")
        process = subprocess.run(
            command,
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        handle.write(process.stdout or "")
        if process.returncode:
            handle.write(f"\n[exit_code] {process.returncode}\n")
        return process.returncode


def can_import(module: str) -> bool:
    code = f"import {module}"
    return subprocess.run([sys.executable, "-c", code], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False).returncode == 0


def prepare_python_runtime(manifest: dict[str, Any], log_dir: Path, logger: StepLogger) -> None:
    logger.event("prepare_python_runtime", "started")
    required_modules = ["google.analytics.data_v1beta", "googleapiclient.discovery", "requests"]
    missing = [module for module in required_modules if not can_import(module)]
    if missing:
        pip_log = log_dir / "python_runtime_setup.log"
        code = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], ROOT, pip_log)
        if code:
            raise RuntimeError(f"Python runtime setup failed; see {pip_log}")
    logger.event("prepare_python_runtime", "passed", missing_before_setup=missing)


def node_can_import_playwright() -> bool:
    code = "import('playwright').then(()=>process.exit(0)).catch(()=>process.exit(1))"
    return subprocess.run(["node", "-e", code], cwd=str(ROOT), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False).returncode == 0


def prepare_node_runtime(log_dir: Path, logger: StepLogger) -> None:
    logger.event("prepare_node_runtime", "started")
    if not node_can_import_playwright():
        npm_log = log_dir / "node_runtime_setup.log"
        code = run_command(["npm", "install", "--package-lock=false", "--silent"], ROOT, npm_log)
        if code:
            raise RuntimeError(f"Node runtime setup failed; see {npm_log}")
    logger.event("prepare_node_runtime", "passed")


def write_error_summary(output_dir: Path, manifest: dict[str, Any] | None, step: str, error: str, logs: dict[str, str]) -> dict[str, Any]:
    payload = {
        "status": "failed",
        "failed_step": step,
        "error": error,
        "generated_at": now((manifest or {}).get("operator_timezone", "Asia/Shanghai")),
        "logs": logs,
        "read_next": "Read this file first. Open long logs only when the compact error is insufficient.",
    }
    write_json(output_dir / "error_summary.json", payload)
    return payload


def copy_manifest_for_run(source_manifest: Path, manifest: dict[str, Any], output_dir: Path, timezone: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    run_manifest = output_dir / "run_manifest.json"
    manifest = dict(manifest)
    execution = dict(manifest.get("execution", {}))
    execution.update({
        "status": "running",
        "started_at": now(timezone),
        "source_manifest": str(source_manifest),
    })
    manifest["execution"] = execution
    write_json(run_manifest, manifest)
    return run_manifest


def validate_run_summary(summary: dict[str, Any]) -> list[str]:
    schema = load_schema(ROOT, "run_summary.schema.json")
    return [f"{issue.path}: {issue.message}" for issue in validate_json_schema(summary, schema)]


def build_run_summary(output_dir: Path) -> dict[str, Any]:
    bundle = load_bundle(output_dir)
    validation_path = output_dir / "validation_summary.json"
    browser_path = output_dir / "browser_qa_summary.json"
    validation = json.loads(validation_path.read_text(encoding="utf-8")) if validation_path.exists() else {"status": "failed", "failed_checks": ["missing_validation_summary"]}
    browser = json.loads(browser_path.read_text(encoding="utf-8")) if browser_path.exists() else {"status": "failed", "failed_checks": ["missing_browser_qa_summary"]}

    summary = {
        "status": "passed" if validation.get("status") == "passed" and browser.get("status") == "passed" else "failed",
        "scope": scope_summary(bundle),
        "headline_metrics": headline_metrics(bundle),
        "reconciliation": reconciliation_summary(bundle),
        "validation": {
            "status": validation.get("status", "failed"),
            "failed_checks": validation.get("failed_checks", []),
        },
        "browser_qa": {
            "status": browser.get("status", "failed"),
            "desktop_console_errors": int(browser.get("desktop_console_errors") or 0),
            "mobile_console_errors": int(browser.get("mobile_console_errors") or 0),
            "horizontal_overflow": bool(browser.get("horizontal_overflow")),
            "failed_checks": browser.get("failed_checks", []),
        },
        "files": {
            "report_html": "report.html",
            "report_bundle": "report_bundle.json",
            "validation_summary": "validation_summary.json",
            "browser_qa_summary": "browser_qa_summary.json",
            "run_summary": "run_summary.json",
        },
    }
    schema_errors = validate_run_summary(summary)
    if schema_errors:
        summary["status"] = "failed"
        summary["validation"]["status"] = "failed"
        summary["validation"]["failed_checks"] = list(summary["validation"].get("failed_checks", [])) + ["run_summary_schema"]
        summary["schema_errors"] = schema_errors
    return summary


def compact_stdout(summary: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    metrics = summary.get("headline_metrics", {})
    return {
        "status": summary.get("status"),
        "output_dir": str(output_dir),
        "revenue": metrics.get("affiliate_revenue", 0),
        "orders": metrics.get("affiliate_orders", 0),
        "target_pacing": metrics.get("mtd_pacing", 0),
        "validation": summary.get("validation", {}).get("status"),
        "browser_qa": summary.get("browser_qa", {}).get("status"),
    }


def main() -> int:
    args = parse_args()
    manifest_path = args.manifest.resolve()
    manifest: dict[str, Any] | None = None
    output_dir = ROOT / "affiliate_reports" / "_failed_manifest_validation"
    log_dir = output_dir / "run_logs"
    logs: dict[str, str] = {}

    try:
        manifest = load_manifest(manifest_path)
        validate_manifest(manifest, ROOT)
        output_dir = resolve_output_dir(manifest, ROOT)
        log_dir = output_dir / "run_logs"
        logger = StepLogger(log_dir, quiet=args.quiet, timezone=manifest.get("operator_timezone", "Asia/Shanghai"))
        logger.event("validate_manifest", "passed", manifest=str(manifest_path), output_dir=str(output_dir))

        if args.validate_only:
            payload = {"status": "passed", "output_dir": str(output_dir), "manifest": str(manifest_path)}
            print(json.dumps(payload, ensure_ascii=False))
            return 0

        stale_error = output_dir / "error_summary.json"
        if stale_error.exists():
            stale_error.unlink()
        run_manifest = copy_manifest_for_run(manifest_path, manifest, output_dir, manifest.get("operator_timezone", "Asia/Shanghai"))
        logger.event("prepare_output_dir", "passed", run_manifest=str(run_manifest))

        prepare_python_runtime(manifest, log_dir, logger)

        generator = manifest["run"]["generator"]
        generator_path = (ROOT / generator).resolve()
        if not generator_path.exists():
            raise RuntimeError(f"Configured generator does not exist: {generator}")
        generation_log = log_dir / "generate_report.log"
        logs["generation"] = str(generation_log)
        logger.event("generate_report", "started", generator=generator)
        generation_code = run_command([sys.executable, str(generator_path), "--manifest", str(run_manifest)], ROOT, generation_log)
        if generation_code:
            raise RuntimeError(f"Report generation failed with exit code {generation_code}; see {generation_log}")
        logger.event("generate_report", "passed")

        validation_log = log_dir / "validation.log"
        logs["validation"] = str(validation_log)
        logger.event("validation", "started")
        validation_code = run_command([sys.executable, "scripts/validate_affiliate_report.py", "--manifest", str(run_manifest), "--quiet"], ROOT, validation_log)
        if validation_code:
            raise RuntimeError(f"Validation failed with exit code {validation_code}; see {validation_log}")
        logger.event("validation", "passed")

        prepare_node_runtime(log_dir, logger)
        browser_log = log_dir / "browser_qa.log"
        logs["browser_qa"] = str(browser_log)
        logger.event("browser_qa", "started")
        browser_code = run_command(["node", "scripts/browser_qa_report.mjs", "--manifest", str(run_manifest), "--quiet"], ROOT, browser_log)
        if browser_code:
            raise RuntimeError(f"Browser QA failed with exit code {browser_code}; see {browser_log}")
        logger.event("browser_qa", "passed")

        summary = build_run_summary(output_dir)
        write_json(output_dir / "run_summary.json", summary)
        if summary["status"] != "passed":
            write_error_summary(output_dir, manifest, "summary", "Validation or browser QA did not pass", logs)
            print(json.dumps(compact_stdout(summary, output_dir), ensure_ascii=False))
            return 1

        print(json.dumps(compact_stdout(summary, output_dir), ensure_ascii=False))
        return 0

    except Exception as exc:
        if manifest is not None:
            try:
                output_dir = resolve_output_dir(manifest, ROOT)
            except Exception:
                pass
        error = write_error_summary(output_dir, manifest, "runner", str(exc), logs)
        payload = {
            "status": "failed",
            "output_dir": str(output_dir),
            "error_summary": str(output_dir / "error_summary.json"),
            "error": error["error"],
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
