# Measurement Contract

## Scope Fields

Every run should preserve these fields in the narrative and bundle:

- brand
- region or war-zone
- market/country or country group
- current date range
- previous comparison range when trend is requested
- YTD range when pacing is requested
- currency
- GA4 property and timezone
- target method
- platform route and refresh status

## Evidence Roles

- GA4 proves site behavior, market boundary, traffic source/campaign, and transaction detail when pulled at row level.
- Affiliate platform raw order/action rows prove platform-side order, commission, validation, publisher, and payout evidence.
- Target workbooks and exported target artifacts prove operating goals, pacing curves, and country splits.
- Publisher mapping proves management-facing identity labels; raw IDs remain audit evidence until mapped.

## Source-Of-Truth Rules

- Use GA4 `countryId` as the market boundary for GA4-led reports unless the user names another boundary.
- Use one consolidated row per distinct `transactionId` as final affiliate order truth when transaction detail exists.
- Do not use aggregate GA4 `transactions` as final affiliate order count when transaction-level data is available.
- Treat platform rows without a GA4 `transactionId` match as reconciliation evidence, not automatic market performance.
- Preserve source-row currencies and report-currency conversion assumptions separately.

## Attribution Classes

Use stable attribution labels:

- `manual_utm`
- `platform_only`
- `ga4_only`
- `out_of_scope`
- `inferred`

Count overlap once. When attribution is inferred, say what evidence supports the inference and what evidence is missing.

## Context Checks

Before writing the final answer, verify:

- current, previous, YTD, and platform pull date lenses are not mixed
- country group rollups are explicit, for example BNX = NL + BE + LU
- publisher labels do not hide raw evidence IDs
- platform refresh status and row counts are named
- caveats are attached to the KPI they affect
