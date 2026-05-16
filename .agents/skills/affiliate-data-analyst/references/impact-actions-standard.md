# Impact Actions Standard

Use this reference before Impact pulls for eufyMake affiliate reporting. It complements `$mcp-impact-affiliate-orders`; use that skill for the raw tool contract and this reference for project-specific operating guardrails.

## Required Pull Shape

- Use direct campaign-scoped `Actions` as the raw order/action evidence source when available.
- Pull a broad evidence window first, then filter locally by the business date lens, usually `EventDate`.
- Preserve raw rows before normalization.
- Deduplicate by stable Impact action/conversion ID when combining windows.
- Preserve out-of-market, unknown-country, and tracker-market mismatch rows as audit evidence instead of silently dropping them.

## Date Lenses

- Treat Impact API `StartDate` / `EndDate` as query-window parameters, not automatically as the report business period.
- For monthly, weekly, and daily reports, classify report scope locally from `EventDate` after the broad pull.
- Use post-period refresh windows when late updates, reversals, locking, or posting lag could affect payout/status.

## Pagination And Preview

- Do not trust a tiny `PageSize` request as proof that the response will be tiny. The API or connector may return a larger default page size.
- Avoid dumping preview rows into chat. Write raw responses to files, then summarize row counts, fields, page metadata, and caveats.
- Production pulls must paginate until exhausted or explicitly record partial pagination coverage.
- Record requested page size, returned page size, page count, row count, and whether the pull is complete.

## Gap Checks

If GA4 shows Impact-attributed orders but Impact broad `Actions` has no matching rows:

- Recheck advertiser/account and campaign ID.
- Recheck `EventDate` versus posting/update lenses.
- Query representative or all material GA4-only order IDs directly when feasible.
- Record whether the result is `fresh`, `partial_refresh`, `query_filter_error`, or `unavailable`.

## User-Facing Language

Use Impact-specific caveats only where they affect interpretation:

- Good: `Impact rows were pulled broadly and filtered locally by EventDate for the report period.`
- Good: `Returned page size differed from the requested preview size, so raw rows were written to files and summarized rather than pasted into chat.`
- Avoid: `Impact has zero orders` before checking account, campaign, date lens, pagination, and direct order lookup where applicable.
