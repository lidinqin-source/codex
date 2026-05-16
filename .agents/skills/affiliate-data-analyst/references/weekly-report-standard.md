# Affiliate Weekly Report Standard

The report is both a retrospective and a strategy guide. It should be concise enough for leadership, but auditable enough for channel owners to act without asking where a number came from.

## Required War-Zone Report Structure

Use this structure for single war-zone reports such as EU1, EU2, NEU, US, CA, or ANZ. Do not replace the country drill-down with a flat source / publisher table; publisher and traffic evidence belongs inside each country drill-down.

1. `Overview by Region`
   - YTD pacing, current-week pacing, gap, status, and core judgment.
   - Annual affiliate goal, YTD target, current-week target, current actuals, and required run-rate.
2. `Overview by Country & Goal Health`
- Country or sub-region rows with YTD pacing, current-week pacing, gap, status, and core judgment.
- If country-level goals are not configured, mark pacing and gap as `Data incomplete` instead of fabricating a split, and add a required config action.
- If DTC or affiliate seasonality is configured, calculate YTD and current-week targets from the non-linear target curve instead of using annual / 52 or day-count linear pacing. If only DTC seasonality is available, document that it is being used as the affiliate target pacing proxy.
- Include `Cross-country Patterns` immediately under this section.
3. `Drill-down by Country (supporting evidences)`
   - Use a `Country Diagnostic Card` for each country or sub-region.
   - Each card must use the same substructure:
     - `Goal & Pacing`
     - `Platform + Publisher Pivot`
     - `Selected Case: Traffic & Funnel Analysis`
     - `Next Action`
   - For EU1, use `3.1 DE`, `3.2 FR`, and `3.3 BNX`.
4. `New Week Action Plan`
   - Owner, deadline, expected outcome, needed evidence, and decision request.
5. `Appendix / Audit Evidence`
   - GA4 source/campaign rows, platform raw rows, publisher mapping, Awin residual evidence, reproduction guide, and caveats.

## 1. Overview by Region

Purpose: show the channel health at a glance.

Include:

- War-zone sales progress, revenue, orders, sessions, users, conversion, AOV, ROAS when cost is available, contribution share, and week-over-week / target variance.
- Total market baseline versus affiliate contribution.
- Clear status language: on track, ahead, behind, or data incomplete.

Evidence:

- GA4 market baseline.
- GA4 affiliate session and order facts.
- Platform order and commission facts when refreshed.

## 2. Overview by Country & Goal Health

Purpose: identify where growth, decline, or risk is concentrated.

Include:

- Country or sub-region split under the war-zone.
- YTD pacing, current-week pacing, gap, status, and core judgment per country when country goals exist.
- `Data incomplete` pacing and gap when country goals do not exist.
- Cross-country patterns that explain whether the issue is concentrated, systemic, or low-volume noise.

## 3. Drill-down by Country

Evidence:

- GA4 manual UTM facts.
- GA4 `transactionId` detail.
- Platform raw order details.

Each country or sub-region section must use a `Country Diagnostic Card`:

- `Goal & Pacing`: annual goal, YTD pacing, weekly pacing, weekly gap, status, and a one-sentence readout. Do not explain platform or publisher causes here.
- `Platform + Publisher Pivot`: one table combining platform and publisher evidence with sessions, orders when order-level evidence exists, revenue, RPS, WoW revenue, signal, and action.
- `Selected Case: Traffic & Funnel Analysis`: one selected traffic case per country, with `Why selected`, evidence, diagnostic funnel read, interpretation, and next action. DE may use two cases when one is Awin residual migration.
- `Next Action`: one concise operating action that can be assigned for the next week.

Country card constraints:

- DE pivot has at most 5 rows; FR and BNX pivots have at most 3 rows.
-正文只放 top evidence; full publisher/source/case details belong in appendix CSVs.
- Do not fill `Orders` or `AOV` unless order-level evidence or platform raw detail exists. Use `n/a` instead of GA4 aggregate `transactions`.
- Funnel analysis is diagnostic evidence only, not revenue or payout truth.

Report-facing publisher display:

- Use the field name `Publisher` in all management-facing sections.
- The `Publisher` value should only contain the resolved publisher identity, such as `Publisher Name (id: raw_campaign)`.
- Keep platform, source, and medium in separate fields; do not embed them into the `Publisher` value.
- Do not show raw IDs such as `impact / affiliate / 1370333` as the final label.
- If a non-Awin publisher cannot be mapped, show `Unmapped Publisher (id: raw_campaign)` and include a next action to confirm identity.
- For Awin residual traffic, do not use `(referral)`, `(organic)`, or `(not set)` as IDs. Use Awin export or historical mapping first; otherwise extract `siteid` / `sv_campaign_id` from landing URLs and display `Publisher Name (siteid: raw_siteid)` if mapped, or `Awin residual pending (siteid: unknown)` if unmapped.
- Keep `raw_manual_source`, `raw_manual_medium`, `raw_manual_campaign`, `raw_siteid`, `raw_sv_campaign_id`, `publisher`, `mapping_source`, and `mapping_confidence` in audit files.

## 4. New Week Action Plan

Purpose: turn channel strategy into accountable action.

Include:

- Completed items.
- In-progress items.
- Blockers.
- Owner, deadline, expected outcome, and evidence needed for each next action.

Examples:

- Confirm publisher identity for high-traffic zero-revenue IDs.
- Migrate Awin residual links to TradeDoubler.
- Review platform-only orders before payout.

## Optional: Best Cases And Reusable Learnings

Purpose: capture what worked so it can be repeated.

Include:

- Successful publisher / campaign cases.
- Channel characteristics and operating process.
- Cost, ROI, conversion path, and durability.
- Replicable playbook or checklist.

## Optional: Long-Term Projects And Capability Building

Purpose: separate weekly firefighting from durable channel capability.

Include:

- Data warehouse and order reconciliation improvements.
- Publisher resource library.
- SOPs.
- Automation and AI tooling.
- Cross-market resource reuse.

## 5. Appendix / Audit Evidence

Purpose: preserve the evidence chain without interrupting the management narrative.

Include:

- GA4 source / medium / campaign rows.
- GA4 transaction-level affiliate classification when available.
- Platform raw rows and reconciliation status.
- Publisher mapping table and mapping confidence.
- Awin residual landing URL evidence and migration keys.
- Data reproduction guide that states the exact GA4 date range, metrics, dimensions, country mapping, affiliate filters, and known differences from common GA4 Explore views.
- Tracking gaps, platform refresh limitations, out-of-market platform orders, and other caveats.

## Data Rules

- Do not use GA4 `transactions` as the final order count when `transactionId` detail exists.
- Final affiliate orders are one consolidated row per distinct `transactionId`.
- Preserve whether evidence came from GA4 manual UTM, active platform data, or inference.
- Raw UTM campaign values are evidence IDs and must be mapped to real publisher names before appearing in the report body.
- Archive superseded reports instead of leaving conflicting active versions.
- Keep current-week reconciliation, broad platform pulls, and YTD reconciliation as separate scopes in the appendix and `report_bundle.json`.
- Preserve source references for every KPI table: tool or file, filters, row counts, pagination coverage, date lens, refresh status, and caveats.
- Do not commit raw order-level platform exports, credentials, or auth/cache artifacts by default.

## Data Reproduction Guide Standard

Every weekly report should include a short reproduction guide in the appendix. It should answer:

- Date ranges used for current week, comparison week, and YTD.
- GA4 property, property timezone, and currency.
- Target pacing method, including whether targets are linear or based on DTC / affiliate seasonality.
- Metrics used, such as `purchaseRevenue` or `totalRevenue`, and whether order count uses distinct `transactionId` or GA4 `transactions`.
- Dimensions used, such as `country`, `manualSource`, `manualMedium`, and `manualCampaignName`.
- Country or war-zone rollup rules, such as BNX = Netherlands + Belgium + Luxembourg.
- Affiliate inclusion filter, including whether the report uses `manualMedium = affiliate` only or a broader evidence rule such as source-based Awin residual inclusion.
- Known Explore mismatch notes, especially when a common GA4 Exploration filter is narrower than the report's production scope.
