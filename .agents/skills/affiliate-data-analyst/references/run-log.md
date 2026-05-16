# Report Run Log

Use this file to record how each report was generated. Keep the notes short but specific enough that another analyst can reproduce the scope and caveats.

## 2026-04-01 to 2026-04-30 | eufyMake US Monthly Production

- Status: generated.
- Active report: `affiliate_reports/eufymake-US-2026-04-01_to_2026-04-30-monthly-production/report.html`
- Detailed process retrospective: `affiliate_reports/eufymake-US-2026-04-01_to_2026-04-30-monthly-production/skill_process_retrospective.md`
- Script: `scripts/generate_us_monthly_report.py`
- Scope:
  - GA4 property `302635205` / `P01 EufyMake All Sites | GA4`.
  - Market `US`, property timezone `Europe/London`, currency `USD`.
  - Current month `2026-04-01` to `2026-04-30`; comparison `2026-03-01` to `2026-03-31`; YTD `2026-01-01` to `2026-04-30`.
- Inputs refreshed:
  - GA4 US market baseline, daily market trend, manual UTM session facts, and transactionId-level order facts.
  - Google Sheets coupon lookup from `折扣券放到第一栏`.
  - Impact raw `Actions` for campaign `18025`, filtered locally by `EventDate` April and primary US customer-country scope.
  - CJ Commission Detail API by April event-date and posting-date lenses.
- Output facts:
  - US total market revenue: `$1,825,046.26`.
  - GA4 affiliate revenue: `$282,759.05`; MoM `-34.3%`.
  - GA4 affiliate distinct transactionId orders: `706`.
  - Impact EventDate-April rows: `345`; US-scope rows: `207`; US-scope sale amount: `$99,379.63`; payout: `$7,572.03`.
  - CJ rows: `0`.
  - Current-month reconciliation: `108` matched, `598` GA4-only, `99` platform-only.
- Known caveats:
  - US affiliate target source was not found, so goal pacing is `data_incomplete`.
  - Impact `StartDate` / `EndDate` is not used as final business-month truth; rows are locally filtered by `EventDate`.
  - CJ zero rows should be verified with wider posting-lag checks or CJ UI if GA4 shows material CJ revenue.
  - Raw input files remain under ignored `raw_inputs/`.

## 2026-05-09 to 2026-05-15 | eufyMake EU1 War-Zone Production

- Status: generated.
- Active report: `affiliate_reports/eufymake-EU1-2026-05-09_to_2026-05-15-production/report.html`
- Markdown mirror: `reports/affiliate-weekly/eufymake-eu1-affiliate-weekly-report-2026-05-09.md`
- Script: `scripts/generate_eu1_production.py`
- Scope:
  - EU1 mapping: `DE`, `FR`, `BNX` (`NL`, `BE`, `LU`).
  - GA4 property `302635205`, property timezone `Europe/London`, currency `USD`.
  - Current period `2026-05-09` to `2026-05-15`; comparison `2026-05-02` to `2026-05-08`; YTD `2026-01-01` to `2026-05-15`.
- Inputs refreshed:
  - GA4 session fact, market fact, and market-level transaction fact before affiliate filtering.
  - Coupon lookup from `折扣券放到第一栏`.
  - Impact raw `Actions` for campaign `18025`.
  - TradeDoubler raw transactions.
  - GA4 Awin residual landing-page evidence with extracted `siteid` / `sv_campaign_id`.
  - Impact country-scope QA using broad `Actions` pull plus local `CustomerCountry` classification.
- Output facts:
  - GA4 session fact rows: `30092`.
  - GA4 order fact rows: `2679`.
  - Coupon lookup rows: `179`.
  - Current-week unified affiliate orders: `33`; current-week unified affiliate revenue: `$27,824.79`.
  - YTD unified affiliate orders: `617`.
  - Impact action rows: `96`.
  - TradeDoubler transaction rows: `1`.
  - Current-week EU1-scope reconciliation: `4` matched, `29` GA4-only, `1` platform-only.
  - Primary platform-only row: Impact order `13232336372093`, publisher `CBXL` (`226873`), customer country `NL`, sale amount `$2,843.57`, commission `$142.18`; GA4 raw order fact did not contain the transactionId.
  - Platform rows excluded from primary EU1 reconciliation: `92`, preserved in `platform_orders_out_of_eu1_scope.csv`.
  - Impact country-scope audit rows: `96`, preserved in `impact_country_scope_audit.csv`.
  - Awin residual landing evidence rows: `974`.
- Known caveats:
  - Coupon lookup was applied, but EU1 had no exact `orderCoupon` lookup matches in this run; unified affiliate orders are all `manual_utm`.
  - TradeDoubler returned one transaction and it is a test source, so TD is evidence of route availability, not current scalable performance.
  - Impact `Actions` includes all eufyMake campaign trackers and customer countries; primary EU1 reconciliation now filters platform rows to `customer_country in DE/FR/NL/BE/LU`.
  - Order revenue consolidation uses max `purchaseRevenue` row per `transactionId`.
  - Primary `affiliate_order_reconciliation.csv` is current-week GA4 EU1 unified orders versus current-week EU1-scope Impact / TradeDoubler rows; non-EU1 platform rows are preserved separately for routing QA, and the former YTD-scope reconciliation is preserved as `affiliate_order_reconciliation_ytd_scope.csv`.
  - `platform-only=1` is the current-week primary EU1 customer-country count, not the broad platform-only count; broad current platform pull has `97` rows, with `5` in primary EU1 scope and `92` out of primary EU1 scope.

## 2026-05-09 to 2026-05-15 | eufyMake EU1 War-Zone Test

- Status: archived structure test, not final reconciliation.
- Archived report: `affiliate_reports/archive/eufymake-EU1-2026-05-09_to_2026-05-15-test/report.html`
- Archived Markdown: `reports/archive/affiliate-weekly/eufymake-eu1-war-zone-test-2026-05-09.md`
- Scope:
  - EU1 test mapping: `DE`, `FR`, `BNX` (`NL`, `BE`, `LU`).
  - GA4 property `302635205`, property timezone `Europe/London`, currency `USD`.
  - Current period `2026-05-09` to `2026-05-15`; comparison `2026-05-02` to `2026-05-08`; YTD `2026-01-01` to `2026-05-15`.
- Inputs refreshed:
  - GA4 EU1 market and affiliate revenue by country.
  - GA4 affiliate source / campaign facts.
  - GA4 distinct `transactionId` counts for current, previous, and YTD.
  - Awin residual QA from GA4 source evidence.
  - Impact publisher-name mapping for material EU1 campaign IDs.
  - Awin residual landing URL evidence with `siteid` / `sv_campaign_id` extraction where available.
  - EU1 country goal split: DE 62.0%, FR 20.0%, BNX 18.0%.
  - EU1 DTC net sales seasonality input, used as the non-linear affiliate target pacing proxy.
  - Data reproduction guide added to the appendix so GA4 Explore checks can match the report scope.
  - Section 3 rebuilt as Country Diagnostic Cards with platform + publisher pivot and selected traffic/funnel cases.
  - Added audit files: `country_platform_publisher_pivot.csv`, `case_selection.csv`, `case_traffic_detail.csv`, `case_funnel_summary.csv`.
- Known caveats:
  - Impact and TradeDoubler raw platform rows were not refreshed in this test run.
  - Coupon lookup classification was not fully applied; the report is intended to test the war-zone structure.
  - Awin is counted as affiliate evidence but reported separately as residual migration work; unresolved Awin publishers are shown as `Awin residual pending (siteid: unknown)` or `Awin residual pending (siteid: raw_siteid)`.

## 2026-05-09 to 2026-05-15 | eufyMake US

- Status: generated.
- Active report: `affiliate_reports/eufymake-US-2026-05-09_to_2026-05-15/report.html`
- Markdown mirror: `reports/affiliate-weekly/eufymake-us-affiliate-weekly-report-2026-05-09.md`
- Scope:
  - GA4 property `302635205` / `P01 EufyMake All Sites | GA4`.
  - Market `US`, currency `USD`, property timezone `Europe/London`.
  - Current period `2026-05-09` to `2026-05-15`; comparison `2026-05-02` to `2026-05-08`.
- Inputs refreshed:
  - GA4 total US market daily performance.
  - GA4 `manualMedium=affiliate` source, campaign, daily trend, and distinct `transactionId` counts.
  - GA4 top US `orderCoupon` QA.
  - Impact CampaignId `18025`, ActionTrackerId `34610` / `Online Sale - US`.
- Known caveats:
  - CJ means Commission Junction. GA4 `manualSource=cj` is included in affiliate totals, but the raw Commission Junction commission/order tool was not exposed in this session.
  - Coupon lookup did not show visible exact-match KOL hits in the top US coupon summary; Impact promo-code evidence is preserved separately.
  - Impact platform actions are platform evidence and are not the same attribution model as GA4 revenue.

## 2026-05-09 to 2026-05-15 | EufyMake DE

- Status: trial output, not production.
- Active report: `affiliate_reports/eufymake-DE-2026-05-09_to_2026-05-15/report.html`
- Known caveats:
  - Coupon lookup was not applied, so coupon-only affiliate orders are missing.
  - Awin residual traffic was not included.
  - Raw GA4 and platform inputs were not persisted in this run folder.
  - Impact rows are pending and require validation before payout decisions.
- Required before production:
  - Re-pull GA4 market-level order detail.
  - Apply coupon lookup.
  - Include Awin residual QA and migration list.
  - Export `ga4_transaction_classification.csv`, `ga4_excluded_transaction_orders.csv`, `unified_affiliate_orders.csv`, and `affiliate_order_reconciliation.csv`.
  - Persist refresh status and raw source references in `report_bundle.json`.

## 2026-05-08 to 2026-05-14 | EufyMake DE

- Status: archived due to conflicting affiliate scope.
- Archived Markdown:
  - `reports/archive/affiliate-weekly/eufymake-de-affiliate-weekly-report-2026-05-08.md`
  - `reports/archive/affiliate-weekly/eufymake-de-affiliate-weekly-report-2026-05-08-clean.md`
- Archived HTML/data folder:
  - `affiliate_reports/archive/eufymake-de-2026-05-08-2026-05-14/`
- Reason:
  - Markdown included Awin in manual affiliate totals.
  - HTML run used active Europe platform scope only: Impact + TradeDoubler.
  - The updated project rule counts Awin residual traffic as affiliate but reports it separately for migration to TradeDoubler.
