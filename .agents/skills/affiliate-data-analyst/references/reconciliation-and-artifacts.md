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
- `report.html` when HTML output is requested

If existing scripts emit a legacy filename, preserve it but also explain the canonical artifact expected by the report contract.

## SSOT Files

- `run_manifest.json`: single source of truth for task scope, date lenses, input paths, tool pulls, run status, and requested outputs.
- `report_bundle.json`: single source of truth for computed metrics, evidence summaries, caveats, and report-facing data.
- `report.source_files` inside `report_bundle.json`: authoritative report artifact paths after report generation.
- `report_meta.json` or the `report_bundle.scope` block: source of truth for report date language. Do not hard-code date text in HTML or JavaScript when a data file can supply it.

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
- raw exports and credentials are not exposed in the final answer

When validation cannot run, state the exact blocker and residual risk.
