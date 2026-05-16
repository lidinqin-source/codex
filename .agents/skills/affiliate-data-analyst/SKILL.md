---
name: affiliate-data-analyst
description: Use for ANYTHING related to Brandon's eufyMake DTC affiliate data / business / performance analytics, including affiliate reports, GA4-led affiliate analysis, target pacing, publisher performance, Impact/CJ/TradeDoubler order reconciliation, GA4-vs-platform gaps, commission risk, audit CSVs, and branded HTML reports. Route generic GA4-only tasks to $google-analytics when there is no affiliate, publisher, target, or platform-reconciliation context.
---

# affiliate-data-analyst

This Skill equips you with the core / essential knowledge of a top-notch Affiliate Data Analyst, allowing you to assist your user Brandon, who currently works as an affiliate marketing manager at the eufyMake DTC team.


## INSTRUCTION: 

Use the lowest task tier that preserves correctness. Upgrade tiers when ambiguity, data risk, or output blast radius increases; do not run a heavy production workflow for a small file lookup.

Task tiers:

- L0 quick answer / file lookup: answer from a named artifact, simple command, or existing report. `update_plan`, `$requirement-checker`, subagents, and manifests are usually unnecessary.
- L1 single-source query / small edit: confirm the minimum scope, source lens, and output. Use tools required for the evidence source; usually skip `$requirement-checker` and subagents unless risk is high.
- L2 multi-source analysis / reconciliation / attribution: use `update_plan`, `$requirement-checker` preflight, blocking-scope gate, source exploration, and structured evidence notes. Use source-specific subagents when the runtime/user allows them; otherwise do the same exploration locally and record the execution path.
- L3 production report / recurring report / leadership output: use the full workflow in this order: `update_plan`, `$requirement-checker` preflight, blocking-scope gate, source exploration, final requirement gate, production pulls, `run_manifest.json`, `report_bundle.json` or `report_meta.json`, audit files, report generation, and rendered QA.

Tools are evidence requirements; subagents are execution helpers. Required evidence must still be gathered through ready source tools even if subagents are unavailable. If a user or runtime policy makes a subagent mandatory for a run, include it in the Tool Capability Inventory as a required capability. If a tier rule is skipped, record a concise `skipped_reason` in the final answer for L0/L1 or in `run_manifest.json` for L2/L3.


### 01. Requirement clarification

- TASK: turn either clear or unclear user's natural language affiliate data / business questions into scoped data pulls and artifact requirements.

- Subagents:
  - Use a requirement / source-exploration subagent after the blocking-scope gate when the run is production-grade, multi-source, ambiguous, or asks for a new data source, and the runtime/user allows subagents.
  - Assign one bounded exploration question per independent source surface, such as GA4 property/date scope, Impact Actions, CJ commission detail, TradeDoubler transactions, Google Sheets targets/publisher mappings, or existing workspace artifacts.
  - Do not ask a source-exploration subagent to infer or choose a missing production period, market, cadence, or output target. Those are blocking scope questions for the main agent to confirm with the user.
  - If subagents are unavailable or not allowed in the current runtime, the main agent must perform the same read-only exploration steps locally and record that execution path in `run_manifest.json`. This does not relax any source-tool requirement.
- Tools Use:
  - Codex App Server `tool/requestUserInput`, surfaced in some runtimes as `request_user_input`, for L2/L3 user-facing blocking-scope gates and required clarification choices
  - `$requirement-checker` as a conditional gate: optional for L0/L1, mandatory preflight for L2, and mandatory preflight plus final acceptance gate for L3
  - `references/tool-capability-standard.md`, `references/codex-question-tool.md`, `references/measurement-contract.md`, `references/reconciliation-and-artifacts.md`, `references/operating-review.md`, `references/platform-context.md`, and the report-standard reference that matches the requested cadence
  - `references/impact-actions-standard.md` before Impact production pulls or Impact gap analysis
  - Built-in web search for data plan research when current public context is needed
- INPUT: Various user's natural language affiliate data / business questions or existing report.
- OUTPUT: a scoped requirement snapshot that can drive data pulls, analysis, validation, and final artifacts.

Requirement clarification is a gate, not a casual preface. Use these rules before production data pulls:

0. Apply the task tier first. Run `$requirement-checker` before asking the user for L2/L3 work, or for any L1 task whose scope is risky or ambiguous. Use it to identify explicit requirements, hidden requirements, missing scope, acceptance criteria, and likely blocking questions. For L2/L3, if `$requirement-checker` is unavailable, include it in the batch Tool Capability Inventory as a missing required capability and stop before production work; do not replace it with a manual checklist. For L0/L1 only, a manual checklist is acceptable when the task is not production-blocking.

0a. For L2/L3, the first user-facing todo after reading the skill must be a blocking-scope gate, not source exploration. Do not create a plan where "explore existing report artifacts/data sources" appears before "confirm missing production scope" when the request lacks a required scope field. The blocking-scope gate checks only the user's request, current Asia/Shanghai date, and already named artifacts.

0b. For L2/L3, Codex App Server `tool/requestUserInput` is a required capability whenever the blocking-scope gate needs a user choice. In model-facing tools this may appear as `request_user_input`; read `references/codex-question-tool.md` and `references/tool-capability-standard.md` before applying the gate. Verify that the capability is exposed and callable before presenting the choice. If it is not exposed, do not invent an `openai.yaml` dependency, emulate the tool with Markdown, or accept a user-approved workaround. Run the batch Tool Capability Inventory in 0c, then stop and tell the user that the runtime did not expose the required Question Tool. Do not continue with source exploration, production pulls, or report generation until the required Question Tool is actually available.

0c. Tool Capability Inventory is a read-only capability check, not source exploration and not production work. For L2/L3, read `references/tool-capability-standard.md` and use its canonical registry, statuses, repair policy, and matrix schema. Run the inventory as a batch whenever any required capability may be missing, including when `request_user_input` is missing before scope confirmation. Do not fail fast on the first missing tool. Check every tool that is required or conditionally required by the apparent request and report one matrix with:
   - capability name
   - required / conditional / optional
   - why it is needed
   - how availability was checked
   - status: `available`, `not_exposed`, `unauthorized`, `setup_error`, `not_applicable`, or `unknown`
   - repair attempts, when the runtime provides an official repair path
   - blocking impact and next step

   For a production affiliate report, the default inventory includes the canonical capabilities in `references/tool-capability-standard.md`: `tool/requestUserInput` / `request_user_input`, `$requirement-checker`, `$google-analytics`, `$mcp-impact-affiliate-orders`, `$mcp-commission-junction-affiliate-orders`, `$mcp-tradedoubler-affiliate-orders`, Google Sheets / `google-drive:google-sheets`, `Spreadsheets`, `$anker-brand-html-generation`, `browser:browser`, and any publish/deployment tool only if the user asks to publish. All required capabilities must be ready before the run can proceed. If one or more required capabilities remain unavailable, stop after reporting the full matrix instead of reporting only the first failure. Do not downgrade a required capability to optional, substitute another tool, use manual estimates, use Markdown as a tool replacement, or proceed based on user approval of a workaround.

1. Capture current time in Asia/Shanghai before resolving relative dates:

   `TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S'`

2. Convert all relative dates into absolute date ranges and record the base date used. Do not output only "last month", "yesterday", "MTD", or similar relative labels.

3. Time range is mandatory for recurring reports. If the user asks for a monthly, weekly, daily, MTD, QTD, YTD, pacing, or comparison report without an explicit range, ask a clarification question before source exploration, production pulls, or report generation unless the user explicitly says to use defaults or to proceed without confirmation. A read-only Tool Capability Inventory may still run before this clarification so all missing tools can be reported together.

4. For "monthly report" with no month:
   - Recommended option A is the most recent complete natural month based on the Asia/Shanghai run date.
   - Also offer current month-to-date and custom month options when useful.
   - Warn that fresh GA4 and platform rows may be incomplete, especially for cross-timezone markets, and that monthly production reports should prefer completed periods.
   - If the user tells Codex to proceed by default, use the most recent complete natural month, mark the scope as an assumption, and write the assumption into `run_manifest.json`, `report_bundle.json` or `report_meta.json`, and the final report caveats.

5. Confirm or infer each required scope field:
   - `brand`
   - `market`
   - `current_start` and `current_end`
   - comparison range, when the request implies trend, MoM, YoY, pacing, or performance change
   - primary source of truth, usually GA4 for market-facing revenue/order metrics
   - platform evidence lenses, such as Impact `EventDate`, CJ event date, CJ posting date, payout/locking status, and post-period refresh window
   - output artifacts, such as HTML report, Markdown, CSV audits, reconciliation files, or action list
   - whether target pacing is required and where the target source lives

6. Ask for missing context only when it blocks correctness. Otherwise infer from workspace artifacts, naming conventions, existing report caveats, and project references, then record every important inference. Blocking examples include missing time range for a production recurring report, unclear market boundary, missing target source for target-pacing claims, or ambiguous platform date lens. Existing report directories, old scripts, and prior manifests may suggest options, but they must not become default authorization for a new L3 production run.

7. Ask in business language and keep the interaction small. When a user-facing choice is needed for L2/L3, use Codex App Server `tool/requestUserInput` / `request_user_input`; do not emulate it with a Markdown question card. Present up to three short questions when using the tool, because the official app-server API is designed for 1-3 short questions. Explain the reason/impact for each, and make the recommended option `A` or clearly labeled `(Recommended)`. For L0/L1 only, a compact Markdown question card is acceptable when the formal Question Tool is unavailable and the answer is not production-blocking.

8. After the blocking-scope gate passes, do source exploration before asking about non-blocking fields, filters, or metrics. For L1, do only the source checks needed for the requested answer. The exploration worker, either subagent or main-agent execution path, should verify the relevant source contract or existing artifact first:
   - GA4: property, timezone, currency, market boundary, dimensions, metrics, transaction fields, and filters.
   - Impact: read `references/impact-actions-standard.md`; verify advertiser account, `Actions` date semantics, action ID, `EventDate`, country field, amount, payout, status, and pagination behavior.
   - CJ / TradeDoubler: read `references/platform-context.md`; verify advertiser/account configuration, launch or active-program context, date lenses, status fields, order ID, amount, commission, and zero-row caveats.
   - Google Sheets / local files: target, publisher, CRM, and mapping source availability.
   - Existing workspace: prior report caveats, run manifests, report bundles, and reusable scripts.

9. Tool Availability Preflight is required for L2/L3 before production pulls or report generation. It must use the canonical registry in `references/tool-capability-standard.md`, and it must be batch-oriented, not fail-fast. Declare the required tools for the scoped run, then verify each one is callable and authorized:
   - Codex App Server `tool/requestUserInput` / `request_user_input` when user clarification or approval is required
   - GA4 / `$google-analytics`
   - Impact / `$mcp-impact-affiliate-orders`
   - CJ / `$mcp-commission-junction-affiliate-orders`
   - TradeDoubler / `$mcp-tradedoubler-affiliate-orders`
   - Google Sheets / `google-drive:google-sheets` or `Spreadsheets`
   - branded HTML generation and `browser:browser` for rendered HTML QA; the Browser skill is called through `node_repl` `js` and the Browser `browser-client.mjs` bootstrap, not through an invented direct browser tool

   If one or more required tools are missing, unavailable, unauthorized, or return setup errors, do not use a workaround, substitute data source, manual estimate, Markdown replacement, or weakened evidence path. Check every required or conditional capability before stopping. Try to repair exact required capabilities up to three times when an official repair path exists, such as tool discovery/loading, account/property verification, auth/scope check, or retry through the official tool path. If any required capability still fails, stop before production work and tell the user all failed required capabilities, what was tried, and what residual work is blocked. User approval cannot override missing required tools for L2/L3 production work; the actual required capabilities must be ready.

10. Create or update the requirement snapshot in `run_manifest.json` for L2/L3 production-grade runs. At minimum it should contain:
   - `request_original`
   - `base_date`
   - `operator_timezone`
   - `brand`
   - `market`
   - `current_range`
   - `comparison_range`
   - `date_lenses`
   - `market_boundary`
   - `currency`
   - `requested_outputs`
   - `assumptions`
   - `clarifications`
   - `requirement_checker`
   - `source_exploration`
   - `tool_availability`
   - `input_sources`
   - `skipped_reasons`

   `tool_availability` should follow `references/tool-capability-standard.md`: record each required or conditional capability, canonical name, status, account/property checked, discovery/loading method, repair attempts, final state, `proceed_allowed`, and whether the run is blocked.

11. For L3, after user clarification and before production pulls, run `$requirement-checker` again as an acceptance gate. For L2, run the final gate when the analysis will drive business decisions or when ambiguity remains. Confirm that the scoped requirement has enough detail for data collection, analysis, validation, and report generation. Record unresolved items as assumptions or blockers.

12. Preserve the requirement snapshot as the single source for downstream steps. Data collection, analysis, report copy, file naming, and QA should read from it instead of restating hardcoded period text.

### 02. Data collection

- TASK: Collect affiliate-related data from GA4 and affiliate platforms like IMPACT, CJ, and TradeDoubler, based on the scoped data pulls and artifact requirements. Parse data into the expected format and store data at the specific place.
- Subagents: prefer one source-specific data collection worker per independent MCP/data task when subagents are allowed. Each worker must return file paths, query parameters, date lenses, row counts, caveats, and whether the pull is production evidence or exploratory. If workers are not allowed, the main agent performs the pulls and records the reason.
- INPUT: Scoped data pulls and artifact requirements.
- OUTPUT: Required data for analysis.
- Tools Use:
  - `$google-analytics`
  - `$mcp-impact-affiliate-orders`
  - `$mcp-tradedoubler-affiliate-orders`
  - `$mcp-commission-junction-affiliate-orders`
  - `Spreadsheets`

### 03. Deep data analysis and insight discovery

- TASK: Based on the collected data plus any other additional context or data, follow the different analysis routines and predefined areas to watch defined in `references/operating-review.md`.
- INPUT: Required data for analysis plus other context data.
- OUTPUT: Business and action insights.
- Tools Use:
  - `google-drive:google-sheets` when CRM, target, publisher, or mapping data lives in Google Sheets
  - `Spreadsheets` for local CSV / XLSX analysis
  - Target pacing, annual goal, YTD health, country splits, or seasonality curves: read `references/goal-pacing.md`

### 04. Report generation

- TASK: Combine all the data into a visually good report.
- INPUT: All the data plus playbook-defined template.
- OUTPUT: Visually appealing report or presentation in HTML, and hosting on cloud on demand after asking the user.
- Tools Use:
  - `$anker-brand-html-generation`
  - `browser:browser` as the required L3 production HTML QA tool
  - `build-web-apps:frontend-testing-debugging` for debugging report UI before final L3 Browser QA; it does not replace `browser:browser` for production acceptance
  - `cloudflare:wrangler` or `cloudflare:cloudflare` only when the user asks to publish the report
- Standalone eufyMake HTML reports should include the local favicon asset `assets/eufymake-favicon.png`; embed or copy it intentionally so browser QA does not request an implicit `/favicon.ico`.

## TOOL list

Use these capabilities as tools under this skill:

- Use `references/tool-capability-standard.md` as the canonical tool registry for L2/L3 plans, inventories, manifests, and QA. Do not invent ad hoc aliases or treat a tool as ready just because a related skill name appears in metadata.
- `$requirement-checker` for requirement completeness checks, hidden requirement inference, and acceptance review.
- Codex App Server `tool/requestUserInput`, surfaced as `request_user_input` in supported runtimes, for structured user choices, blocking-scope gates, and L2/L3 production approvals.
- `$google-analytics` for GA4 property discovery, property context, dimensions, metrics, filters, transaction detail, `transactionId`, source / medium / campaign, and report pulls.
- `$mcp-impact-affiliate-orders` for Impact raw action / order evidence.
- `$mcp-tradedoubler-affiliate-orders` for TradeDoubler raw transaction evidence.
- `$mcp-commission-junction-affiliate-orders` for Commission Junction raw commission / order evidence.
- `Spreadsheets` for target workbooks, publisher mappings, CSV / XLSX inspection, formulas, charts, and spreadsheet artifacts.
- `google-drive:google-sheets` for connected Google Sheets lookup or edits when source data lives in Google Sheets.
- `$anker-brand-html-generation` for ANKER / eufyMake branded self-contained HTML report output.
- `browser:browser` for opening, previewing, screenshotting, and verifying local HTML reports through the official Browser skill bootstrap with `node_repl` `js`.
- `build-web-apps:frontend-testing-debugging` for debugging local report UI, layout, console errors, and responsive rendering.
- `cloudflare:wrangler` or `cloudflare:cloudflare` for cloud hosting / deployment only when the user asks to publish the report.
- Built-in web search for external data plan research when current public context is needed.


## Critical Constraints you should follow

1. Time handling

Use Asia/Shanghai for run metadata, operator-facing timestamps, and report generation time.

For GA4 reporting, follow `$google-analytics`: confirm the GA4 `property_id`, exact date range, property timezone, market boundary, and currency before production pulls. Use complete property-local days for completed-period analysis.

`TZ='Asia/Shanghai' date '+%Y-%m-%d %H:%M:%S'`

When confirming time ranges with the user, include a data freshness warning when the range touches recent days: data warehouses and partner platforms may update overnight or later, and the latest cross-timezone market day may not be complete from an Asia/Shanghai operator perspective. Prefer completed periods for production monthly/weekly reports.

Date parsing defaults:

- "last month" / "上月": previous natural month, rendered as absolute start and end dates.
- "this month to date" / "本月至今": first day of the current month through the current base date, unless the data source requires complete days only.
- "last week" / "上周": previous natural week; state the week convention if it matters.
- "YTD": current calendar year start through the chosen complete end date.
- Never use model knowledge cutoff dates or unstated assumptions as the current date.

2. File storage and naming rules

When creating report artifacts, follow the `codex-affliate-mkt` project folder design. All paths below are relative to the project root, not the skill folder.

Project root:

- `codex-affliate-mkt/`

Use one report root per production run:

- `affiliate_reports/{brand}-{market}-{current_start}_to_{current_end}-{run_label}/`

Recommended artifact locations:

- Run manifest: `run_manifest.json`
- Raw inputs: `raw_inputs/`
- Target files: `targets/`
- GA4 transaction classification: `ga4_transaction_classification.csv`
- Unified affiliate orders: `unified_affiliate_orders.csv`
- Order reconciliation: `affiliate_order_reconciliation.csv`
- Platform-only orders: `platform_only_orders.csv` when relevant
- GA4-only orders: `ga4_only_orders.csv` when relevant
- Goal pacing summary: `goal_pacing_summary.csv` and `goal_pacing_summary.json`
- Report bundle: `report_bundle.json`
- Final insight file: `insights.json`
- Action plan: `actions.csv` or `actions.json`
- Report files: `report.md` and / or `report.html`

Rules:

- Keep `run_manifest.json` as the source of truth for task scope, date lenses, input paths, tool pulls, run status, and requested outputs.
- Keep `report_bundle.json` as the source of truth for computed metrics, evidence summaries, caveats, and report-facing data.
- In `report_bundle.json`, use `report_title` only for the human-readable title, use `report` only for the report object, and keep the report file registry under `report.source_files`.
- Keep `report.source_files` inside `report_bundle.json` as the authoritative registry of files used by the report.
- Keep `report_meta.json` or the `report_bundle.scope` block as the source of truth for time semantics.
- Do not hardcode period text in HTML or JS; load time labels from data when available.
- Do not write generated report artifacts into the skill folder.
- Do not create dependency directories, caches, or credentials in the skill folder. Temporary runtime folders may be used only when needed and should be removed or ignored before delivery.

Report production script architecture:

- Design production report scripts around cadence and market extensibility. Daily, weekly, monthly, and region-specific reports may need different data lenses, comparison windows, platform mixes, target rules, and report sections.
- Prefer a shared production runner plus small cadence/market configuration layers when recurring scripts are added. Keep reusable logic in shared helpers and keep market/cadence differences explicit in configuration or thin wrappers.
- A production script should accept or derive these fields from `run_manifest.json`: `brand`, `market`, `cadence`, `current_range`, `comparison_range`, `date_lenses`, `requested_outputs`, `required_tools`, and `run_label`.
- Naming should remain predictable without locking the architecture: scripts may use patterns like `generate_{brand}_{market}_{cadence}_report.py` for thin wrappers, while shared implementation should live in reusable modules when repeated.
- Before standardizing a production script, check whether it generalizes across cadence and market. If it does not, record the script scope and limitations in the run manifest.

Runtime dependency standard:

- Do not assume system Python or preinstalled Python/runtimes in Codex environments contain report-specific packages such as GA4 or Google Sheets SDKs.
- Production scripts should use the project-standard Python environment and dependency manifest, such as `pyproject.toml`, `requirements*.txt`, or another explicit package manager file.
- Project setup should document how to install dependencies and run production scripts. Prefer a checked-in setup note or Codex local-environment setup script generated through the Codex app settings when the workflow becomes recurring.
- Temporary virtual environments are acceptable for one-off repair, but remove large runtime folders before delivery and record the remaining reproducibility gap.

3. Scope constraints:

- For L2/L3 production work, do not replace required source tools, validation contracts, analysis references, deterministic scripts, or report-generation skills with ad hoc manual work.
- Delegate validation, analysis, and report generation to available Codex skills, project references, or deterministic project scripts when the task tier requires them.
- Use `$google-analytics` and platform MCP skills for source data, `references/measurement-contract.md` and `references/reconciliation-and-artifacts.md` for validation rules, and `$anker-brand-html-generation` plus `browser:browser` for branded HTML report generation and preview checks.
- Check whether GA4, Impact, CJ, TradeDoubler, Google Sheets, `browser:browser`, and HTML-generation capabilities required by the scoped run are callable before relying on them. If a tool is lazy-loaded, record that in `run_manifest.json`. If a required capability is unavailable, attempt to repair the exact capability up to three times; if it still fails, stop and tell the user instead of using a workaround or weakening the evidence standard.


4. Data security constraint

- Follow the approved platform data handling and digital security policy for platform rows and exports.
- Do not hardcode tokens, API keys, OAuth material, local session files, or private connector details in scripts, manifests, reports, or skill files.
- Do not add extra redaction, aggregation-only, or sharing restrictions for platform rows unless the user, repository policy, connector policy, or approved security workflow requires it.



5. Truth constraints

- Do not fabricate country goals, publisher identities, or platform refresh status.
- Do not claim `ahead`, `behind`, `on track`, publisher ownership, or platform parity unless the required source exists and the reconciliation checks passed.
- If a source is missing, unavailable, stale, or returns zero rows, distinguish those states clearly. Read `references/platform-context.md` before interpreting platform zero-row results. "Zero rows returned by this query" is not the same as "the platform had no activity."

6. Clarification and output validation

Before reporting a production run as complete, verify and record:

- `run_manifest.json` contains the scoped requirement snapshot and assumptions.
- `report_bundle.json` or `report_meta.json` contains the final scope, date labels, source files, metric definitions, caveats, and evidence summaries.
- Required audit files exist for the requested analysis, especially transaction classification, unified orders, reconciliation outputs, platform refresh status, target pacing summary, and action items when applicable.
- L3 HTML reports have been rendered with `browser:browser`, with desktop and mobile checks, console error review, and horizontal overflow check.
- The final user-facing response does not expose credentials, auth material, or secrets.

7. Failure handling

- Missing date range for a production recurring report: ask the user with recommended defaults; do not silently choose unless the user asked to proceed by default.
- Missing target source: mark target pacing as `data_incomplete`; do not invent targets.
- Required GA4/platform/Google Sheets/local-source/`browser:browser` capability unavailable: try to repair the exact required capability up to three times. If it still fails, stop before production work and report the failed capability, attempts, and blocked outputs.
- Platform query returns unexpected date lenses or pagination behavior: pull a broad evidence window, filter locally by the business date lens, deduplicate by platform order/action ID, and log the method.
- Local dependency missing: use the project-standard Python environment and dependency manifest when present. If absent, create or request a reproducible setup before treating temporary installs as production-ready; remove large temporary folders after one-off use and document remaining rerun requirements.
- `browser:browser` unavailable: do not use Playwright or another renderer as a production-report workaround. Try to repair `browser:browser` up to three times; if it still fails, stop before delivering a production HTML report.
