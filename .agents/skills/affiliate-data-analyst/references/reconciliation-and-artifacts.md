# Reconciliation And Artifacts

## Reconciliation Groups

Use these groups for order-level reconciliation:

- `matched`: transaction appears in both GA4 affiliate evidence and platform evidence.
- `ga4_only`: transaction appears in GA4 affiliate evidence but not platform evidence.
- `platform_only`: transaction appears in platform evidence but not GA4 affiliate evidence for the named scope.
- `out_of_scope`: platform row is outside the primary market/date/country scope.
- `missing_transaction_id`: platform or GA4 evidence lacks a usable transaction ID.
- `duplicate_or_adjustment`: duplicate, reversal, adjustment, or non-order row requiring review.

Always name the reconciliation scope next to `platform_only` or `ga4_only` counts.

## Canonical Production Artifacts

For production reports, prefer:

- `run_manifest.json`
- `report_bundle.json`
- `insights.json`
- `actions.csv` or `actions.json`
- `goal_pacing_summary.csv`
- `goal_pacing_summary.json`
- `ga4_transaction_classification.csv`
- `unified_affiliate_orders.csv`
- `ga4_excluded_transaction_orders.csv`
- `affiliate_order_reconciliation.csv`
- `platform_only_orders.csv` when platform-only rows exist
- `ga4_only_orders.csv` when GA4-only rows exist
- `publisher_mapping_candidates.csv` when unmapped publishers exist
- `validation_summary.json`
- `browser_qa_summary.json`
- `run_summary.json`
- `error_summary.json` when a run fails
- `report.html` when HTML output is requested

If existing scripts emit a legacy filename, preserve it but also explain the canonical artifact expected by the report contract.

## SSOT Files

- `run_manifest.json`: single source of truth for task scope, date lenses, input paths, tool pulls, run status, and requested outputs.
- `report_bundle.json`: single source of truth for computed metrics, evidence summaries, caveats, and report-facing data.
- `run_summary.json`: small model-facing handoff for final status, headline metrics, reconciliation counts, validation status, browser QA status, and key output file names.
- `validation_summary.json` and `browser_qa_summary.json`: compact QA handoffs. Read these before opening any large artifact.
- `error_summary.json`: first file to read after runner failure; open long logs only if the compact error is insufficient.
- `report.source_files` inside `report_bundle.json`: authoritative report artifact paths after report generation.
- `report_meta.json` or the `report_bundle.scope` block: source of truth for report date language. Do not hard-code date text in HTML or JavaScript when a data file can supply it.

## Manifest-Driven Pipeline

For L3 production reports, prefer the unified runner:

```sh
make affiliate-report MANIFEST=affiliate_reports/.../run_manifest.json
```

or:

```sh
python scripts/run_affiliate_report.py --manifest affiliate_reports/.../run_manifest.json --quiet
```

The runner validates `schemas/run_manifest.schema.json`, prepares Python/Node runtime, runs source pulls/generation, runs validation and browser QA, then writes `run_summary.json`. The chat model should not read raw rows, large JSON, large CSV, or long logs during normal completion.

`run_summary.json` must keep this compact shape:

```json
{
  "status": "passed",
  "scope": {
    "brand": "eufyMake",
    "market": "US",
    "current_range": "2026-05-01 to 2026-05-15",
    "comparison_range": "2026-04-01 to 2026-04-15"
  },
  "headline_metrics": {
    "affiliate_revenue": 525694.22,
    "affiliate_orders": 481,
    "mtd_target": 514184.54,
    "mtd_pacing": 1.022384,
    "ytd_target": 978113.32,
    "ytd_pacing": 1.949502
  },
  "reconciliation": {
    "matched": 97,
    "ga4_only": 384,
    "platform_only": 21
  },
  "validation": {
    "status": "passed",
    "failed_checks": []
  },
  "browser_qa": {
    "status": "passed",
    "desktop_console_errors": 0,
    "mobile_console_errors": 0,
    "horizontal_overflow": false
  },
  "files": {
    "report_html": "report.html",
    "report_bundle": "report_bundle.json",
    "validation_summary": "validation_summary.json"
  }
}
```

## Bundle Requirements

`report_bundle.json` should preserve:

- scope: brand, market, date ranges, currency, country rules
- data sources: MCP tools or file paths, filters, row counts, pagination coverage, refresh status
- targets: source path, method, annual/YTD/current targets, caveats
- GA4 evidence: property, dimensions, metrics, filters, row counts
- platform evidence: route, account/advertiser, date range, row counts, validation status
- reconciliation summary: matched, GA4-only, platform-only, missing-ID, out-of-scope
- publisher mapping: mapped, unmapped, confidence, review queue
- caveats and action plan

## Validation Checks

Before final delivery, check:

- required artifacts exist for the requested report type
- current-week, previous-period, YTD, and broad-platform scopes are not blended
- order counts are distinct by `transactionId` when transaction detail exists
- row-level reconciliation files contain enough source fields for audit
- final report numbers match the bundle or explain why not
- `validation_summary.json` records its own final non-zero size and does not contain a misleading `bytes: 0` self-record
- automated browser QA passed for desktop 1280x720 and mobile 390x844, with console errors at zero and horizontal overflow false
- raw exports and credentials are not exposed in the final answer

When validation cannot run, state the exact blocker and residual risk.
