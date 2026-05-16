# Affiliate Report Pipeline

This project now treats L3 affiliate production reports as a manifest-driven
pipeline. The agent scopes the run, writes or selects a manifest, then runs the
pipeline instead of reading raw rows in the chat loop.

## Entry Points

```sh
make setup-reporting
make affiliate-report MANIFEST=affiliate_reports/templates/run_manifest.us_monthly_mtd.json
```

Equivalent direct command:

```sh
python scripts/run_affiliate_report.py --manifest affiliate_reports/templates/run_manifest.us_monthly_mtd.json --quiet
```

The runner validates `schemas/run_manifest.schema.json`, prepares Python/Node
runtime when needed, runs the configured production generator, runs validation,
runs browser QA, and writes `run_summary.json`.

## Model-Facing Files

Normal completion should read only:

- `run_summary.json`
- `validation_summary.json`
- `browser_qa_summary.json`
- `error_summary.json` when status is failed

Do not read full raw CSVs, raw JSON exports, large `report_bundle.json`, or long
logs unless the compact summaries point to a specific debug need.

## Output Contract

The final stdout is compact:

```json
{
  "status": "passed",
  "output_dir": "affiliate_reports/...",
  "revenue": 525694.22,
  "orders": 481,
  "target_pacing": 1.022384,
  "validation": "passed",
  "browser_qa": "passed"
}
```

Long command output is captured under `run_logs/*.log`. Source response metadata
belongs in small CSVs such as `platform_refresh_status.csv`,
`impact_pull_log.csv`, and `cj_pull_log.csv`.

## Browser QA

The browser QA script starts a local static server on a free port, opens the
report at desktop `1280x720` and mobile `390x844`, captures screenshots, checks
console errors, horizontal overflow, mobile table internal scrolling, and verifies
H1/current range/key KPI text against `report_bundle.json`. It writes
`browser_qa_summary.json` and then closes the server.

Direct command:

```sh
node scripts/browser_qa_report.mjs \
  --html affiliate_reports/.../report.html \
  --out affiliate_reports/.../browser_qa_summary.json \
  --screenshots affiliate_reports/...
```

or:

```sh
node scripts/browser_qa_report.mjs --manifest affiliate_reports/.../run_manifest.json
```

## Validation

`scripts/validate_affiliate_report.py` checks required files, bundle schema,
bundle-vs-CSV metrics, distinct current `transactionId` order counts, target
math, GA4 date-range separation, Impact/CJ pull-log completeness, zero-row
language, reconciliation counts, and `report.source_files` completeness.

Direct command:

```sh
python scripts/validate_affiliate_report.py --manifest affiliate_reports/.../run_manifest.json --quiet
```

## Debug Policy

Production manifests must set `run.fresh_pull=true` and
`run.debug_cache_allowed=false`. Cache/debug reuse is allowed only in an explicit
debug manifest, and summaries must disclose it. Old report outputs are not source
inputs for production runs.
