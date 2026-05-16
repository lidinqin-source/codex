# Goal Pacing

## Purpose

Use goal pacing as operating control data. It is not GA4 evidence and not platform evidence. Preserve target source files, formulas, seasonality basis, country splits, and caveats separately from performance data.

## Required Inputs

Use any available target source, except where a market-specific default source is defined below:

- target workbook
- exported target CSV
- `report_bundle.json` goal fields
- user-provided annual/monthly/weekly target values

Minimum fields:

- region or country
- annual affiliate goal
- current period target
- current period actual
- YTD target
- YTD actual
- currency
- target method

If country-level goals are missing, mark country pacing as `Data incomplete` and add a configuration action. Do not fabricate a split.

## eufyMake US Default Target Source

For future eufyMake US target and pacing work, use this Google Sheet as the default and official target source:

- Spreadsheet title: `Goal`
- Spreadsheet ID: `19urEQUXab48QzYnj_rFe438sL7ax0ZB5trhcK_bF1rQ`
- Source URL: `https://docs.google.com/spreadsheets/d/19urEQUXab48QzYnj_rFe438sL7ax0ZB5trhcK_bF1rQ/edit?gid=993040432#gid=993040432`
- Tab: `US`
- Sheet ID / gid: `993040432`
- Spreadsheet timezone: `America/Los_Angeles`
- Canonical range for source verification: `US!A1:Z30`

Required field mapping:

- `region`: market or region
- `time`: month, quarter, or total label
- `session`: DTC session target basis
- `net_sales`: DTC net sales basis
- `orders`: DTC orders basis
- `affiliate_session_target`: affiliate session target
- `affiliate_revenue_target`: affiliate revenue target

For US monthly or MTD reports, use `affiliate_revenue_target` as the monthly affiliate revenue target. Prorate by elapsed days for MTD ranges. Preserve the Sheet URL, spreadsheet ID, tab, gid, pull timestamp, and row count in `run_manifest.json`, `goal_pacing_summary.json`, and report caveats.

Do not use previous report outputs, screenshot transcription, cached report bundles, or old `report_bundle.json` target fields as eufyMake US production target inputs unless the user explicitly asks for debug comparison. If the Google Sheet is unavailable, mark pacing as `Data incomplete` and add a configuration action instead of falling back to prior report artifacts.

## Calculations

- `current_gap = current_actual - current_target`
- `current_pacing = current_actual / current_target` when target is nonzero
- `ytd_gap = ytd_actual - ytd_target`
- `ytd_pacing = ytd_actual / ytd_target` when target is nonzero
- `recovery_needed = max(0, ytd_target - ytd_actual)` when the period is behind

Prefer non-linear DTC or affiliate seasonality curves when provided. Use annual/52 or day-count linear pacing only when no seasonality basis exists, and disclose that method.

## Status Labels

- `Ahead`: actual is above target by a meaningful margin.
- `On track`: actual is close enough to target for the operating cadence.
- `Behind`: actual is materially below target.
- `Data incomplete`: target or actual is missing.
- `Evidence conflict`: target files disagree or actual source is inconsistent.

## Report Rules

- Region pacing comes before country pacing.
- Country pacing explains concentration of the gap; it does not replace publisher or platform diagnosis.
- Separate YTD health from current-period health.
- If the program is behind, include the recovery amount and the operator lever most likely to close it.

## Expected Outputs

When production reporting is requested, emit or verify:

- `goal_pacing_summary.csv`
- `goal_pacing_summary.json`
- `goal_pacing_actions.csv` when actions are derived
- `goal_pacing_monthly_targets.csv` when monthly targets exist

Store these under the active report directory, not inside the skill folder.
