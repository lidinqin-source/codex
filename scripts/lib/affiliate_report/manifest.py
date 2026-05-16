from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


class ManifestError(ValueError):
    """Raised when a run manifest is unsafe or invalid."""


@dataclass(frozen=True)
class SchemaIssue:
    path: str
    message: str


def project_root_from(path: Path | None = None) -> Path:
    base = (path or Path(__file__)).resolve()
    for parent in [base, *base.parents]:
        if (parent / ".agents" / "skills" / "affiliate-data-analyst").exists():
            return parent
    return Path.cwd().resolve()


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ManifestError(f"Manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ManifestError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ManifestError(f"Manifest root must be an object: {path}")
    return data


def load_manifest(path: Path) -> dict[str, Any]:
    return load_json(path)


def load_schema(root: Path, schema_name: str) -> dict[str, Any]:
    return load_json(root / "schemas" / schema_name)


def resolve_output_dir(manifest: dict[str, Any], root: Path) -> Path:
    raw = manifest.get("scope", {}).get("output_dir")
    if not isinstance(raw, str) or not raw:
        raise ManifestError("scope.output_dir is required")
    candidate = Path(raw)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ManifestError(f"scope.output_dir must stay inside the project: {raw}") from exc
    if "affiliate_reports" not in resolved.parts:
        raise ManifestError("scope.output_dir must be under affiliate_reports/")
    if any(part in {".git", ".codex", "node_modules", ".venv", "venv"} for part in resolved.parts):
        raise ManifestError(f"scope.output_dir points at a forbidden runtime directory: {raw}")
    return resolved


def _schema_type_matches(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


def _resolve_ref(schema: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ManifestError(f"Unsupported JSON Schema ref: {ref}")
    target: Any = schema
    for raw_part in ref[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        target = target[part]
    if not isinstance(target, dict):
        raise ManifestError(f"JSON Schema ref did not resolve to an object: {ref}")
    return target


def _validate_node(value: Any, node: dict[str, Any], root_schema: dict[str, Any], path: str, issues: list[SchemaIssue]) -> None:
    if "$ref" in node:
        _validate_node(value, _resolve_ref(root_schema, str(node["$ref"])), root_schema, path, issues)
        return

    expected_type = node.get("type")
    if isinstance(expected_type, list):
        if not any(_schema_type_matches(value, item) for item in expected_type):
            issues.append(SchemaIssue(path, f"expected one of {expected_type}, got {type(value).__name__}"))
            return
    elif isinstance(expected_type, str) and not _schema_type_matches(value, expected_type):
        issues.append(SchemaIssue(path, f"expected {expected_type}, got {type(value).__name__}"))
        return

    if "enum" in node and value not in node["enum"]:
        issues.append(SchemaIssue(path, f"expected one of {node['enum']}, got {value!r}"))

    if isinstance(value, str):
        min_length = node.get("minLength")
        if isinstance(min_length, int) and len(value) < min_length:
            issues.append(SchemaIssue(path, f"must be at least {min_length} characters"))
        pattern = node.get("pattern")
        if isinstance(pattern, str) and re.search(pattern, value) is None:
            issues.append(SchemaIssue(path, f"does not match pattern {pattern!r}"))

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = node.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            issues.append(SchemaIssue(path, f"must be >= {minimum}"))

    if isinstance(value, dict):
        for key in node.get("required", []):
            if key not in value:
                issues.append(SchemaIssue(f"{path}.{key}" if path else key, "is required"))
        properties = node.get("properties", {})
        if isinstance(properties, dict):
            for key, child in properties.items():
                if key in value and isinstance(child, dict):
                    _validate_node(value[key], child, root_schema, f"{path}.{key}" if path else key, issues)

    if isinstance(value, list):
        min_items = node.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            issues.append(SchemaIssue(path, f"must contain at least {min_items} items"))
        item_schema = node.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                _validate_node(item, item_schema, root_schema, f"{path}[{index}]", issues)


def validate_json_schema(data: dict[str, Any], schema: dict[str, Any]) -> list[SchemaIssue]:
    issues: list[SchemaIssue] = []
    _validate_node(data, schema, schema, "$", issues)
    return issues


def _parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ManifestError(f"{field} must be an ISO date: {value}") from exc


def validate_manifest(manifest: dict[str, Any], root: Path | None = None, schema_name: str = "run_manifest.schema.json") -> None:
    project_root = root or project_root_from()
    schema = load_schema(project_root, schema_name)
    issues = validate_json_schema(manifest, schema)
    if issues:
        joined = "; ".join(f"{issue.path}: {issue.message}" for issue in issues[:12])
        more = f"; +{len(issues) - 12} more" if len(issues) > 12 else ""
        raise ManifestError(f"Manifest schema validation failed: {joined}{more}")

    scope = manifest["scope"]
    current_start = _parse_date(scope["current_range"]["start"], "scope.current_range.start")
    current_end = _parse_date(scope["current_range"]["end"], "scope.current_range.end")
    comparison_start = _parse_date(scope["comparison_range"]["start"], "scope.comparison_range.start")
    comparison_end = _parse_date(scope["comparison_range"]["end"], "scope.comparison_range.end")
    ytd_start = _parse_date(scope["ytd_range"]["start"], "scope.ytd_range.start")
    ytd_end = _parse_date(scope["ytd_range"]["end"], "scope.ytd_range.end")
    if current_start > current_end:
        raise ManifestError("scope.current_range.start must be <= scope.current_range.end")
    if comparison_start > comparison_end:
        raise ManifestError("scope.comparison_range.start must be <= scope.comparison_range.end")
    if ytd_start > ytd_end:
        raise ManifestError("scope.ytd_range.start must be <= scope.ytd_range.end")
    if not (ytd_start <= current_start <= current_end <= ytd_end):
        raise ManifestError("scope.ytd_range must include the current range")

    boundary_values = manifest["market_boundary"]["allowed_values"]
    if scope["market"] not in boundary_values:
        raise ManifestError("scope.market must be included in market_boundary.allowed_values")

    if manifest["run"]["mode"] == "production":
        if not manifest["run"]["fresh_pull"]:
            raise ManifestError("production run manifests must set run.fresh_pull=true")
        if manifest["run"]["debug_cache_allowed"]:
            raise ManifestError("production run manifests must set run.debug_cache_allowed=false")

    required_tools = [
        row for row in manifest["tool_availability"]["matrix"]
        if row.get("need_level") == "required"
    ]
    failed_tools = [row for row in required_tools if row.get("status") != "available"]
    if manifest["tool_availability"]["proceed_allowed"] and failed_tools:
        names = ", ".join(str(row.get("canonical_name")) for row in failed_tools)
        raise ManifestError(f"tool_availability.proceed_allowed cannot be true while required tools are unavailable: {names}")
    if not manifest["tool_availability"]["proceed_allowed"]:
        raise ManifestError("tool_availability.proceed_allowed is false; production runner must stop before pulling data")

    exclusion = manifest["old_report_exclusion"]
    if exclusion.get("forbid_prior_report_inputs") is not True:
        raise ManifestError("old_report_exclusion.forbid_prior_report_inputs must be true")
    allowed_refs = exclusion.get("allowed_reference_paths", [])
    for ref in allowed_refs:
        if isinstance(ref, str) and ref.startswith("affiliate_reports/eufymake-"):
            raise ManifestError("old_report_exclusion.allowed_reference_paths must not include prior report directories")

    resolve_output_dir(manifest, project_root)
