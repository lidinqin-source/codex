# Tool Capability Standard

## Official Basis

This standard is a project-level governance layer built on top of official Codex mechanisms. It is not a claim that OpenAI ships an affiliate-specific readiness matrix.

Official Codex references used:

- Agent Skills package reusable workflows as `SKILL.md` plus optional `references/`, `scripts/`, `assets/`, and `agents/openai.yaml`: https://developers.openai.com/codex/skills
- `agents/openai.yaml` can configure UI metadata, invocation policy, and declared tool dependencies; do not invent unsupported schema: https://developers.openai.com/codex/skills
- Codex App Server exposes `tool/requestUserInput` for 1-3 short user questions when the client/runtime supports it: https://developers.openai.com/codex/app-server#toolrequestuserinput
- Codex slash commands include `/plan`, which switches the active conversation into plan mode: https://developers.openai.com/codex/cli/slash-commands
- Codex hooks can run on `UserPromptSubmit`, receive `permission_mode`, add context, or block a prompt, but they do not switch the conversation mode or expose app-server tools: https://developers.openai.com/codex/hooks
- Codex config can control MCP server startup and exposed tool allow/deny lists with fields such as `mcp_servers.<id>.required`, `enabled_tools`, and `disabled_tools`: https://developers.openai.com/codex/config-reference#configtoml

Project policy added by this skill:

- L2/L3 affiliate production work treats certain capabilities as required gates.
- Required capabilities must be checked in one batch matrix.
- Required capability failures cannot be bypassed by Markdown, stale artifacts, manual estimates, substitute tools, or user approval.
- Exact capability repair is limited to official repair paths and three attempts.

## Principle

For L2/L3 affiliate production work, every required capability must be actually ready before production work starts. Do not use a workaround, substitute tool, stale artifact, manual estimate, Markdown question, or user approval to replace a required capability.

Subagents are execution helpers. Source tools, validation skills, user-input tools, and QA tools are evidence capabilities. A missing subagent can change who executes the work; a missing required evidence capability blocks the run.

## Mode Entry Gate

For likely L2/L3 production prompts, prefer starting in Codex plan mode so `tool/requestUserInput` can be exposed by clients that gate it behind plan-oriented interaction.

Opening behavior:

- If `request_user_input` is already exposed, use it for the blocking-scope gate.
- If the current mode is not plan mode and `request_user_input` is not exposed, first tell the user to rerun the production request through `/plan <same request>` or switch the current thread with `/plan`.
- Then run the read-only Tool Capability Inventory if the task is already in progress or the user asked for a readiness audit.
- Do not continue into source exploration, production pulls, report generation, or HTML QA while `tool/requestUserInput` remains required and unavailable.

Hook policy:

- A trusted `UserPromptSubmit` hook may detect likely affiliate L2/L3 production prompts and block with a message that tells the user to use `/plan`.
- The hook is only an entry guard. It must not be described as fixing `request_user_input`, because hooks cannot switch modes or force app-server tool exposure.
- Keep hook logic in `codex-infra` templates or a trusted repo `.codex/hooks.json`, not inside this skill folder.

## Two Gates

- Tool Capability Inventory: read-only exposure, auth, and setup check. Use it whenever a required capability may be missing, including before scope confirmation when the Question Tool is missing. It never pulls production data.
- Tool Availability Preflight: scoped readiness check after the blocking-scope gate and before production pulls, analysis, report generation, or HTML QA.

Both gates are batch-oriented. Check every required or conditionally required capability before stopping so the user sees one complete readiness matrix.

## Matrix Schema

Record these fields in the user-facing matrix and in `run_manifest.json.tool_availability` for L2/L3:

- `capability`
- `canonical_name`
- `need_level`: `required`, `conditional`, `optional`, or `not_applicable`
- `why_needed`
- `check_method`
- `status`: `available`, `not_exposed`, `unauthorized`, `setup_error`, `not_applicable`, or `unknown`
- `official_repair_path`
- `repair_attempts`
- `blocking_impact`
- `next_step`

If any required capability is not `available`, set `proceed_allowed` to `false`.

## Status Rules

- `available`: the capability is exposed, callable, authorized, and can be used for the scoped run.
- `not_exposed`: the current mode, client, skill list, plugin list, app server, or MCP registry does not expose the capability.
- `unauthorized`: the capability exists but account, app, connector, property, advertiser, or sheet access is missing.
- `setup_error`: the capability exists but dependency, configuration, server startup, or runtime setup failed.
- `not_applicable`: the request does not require this capability after scope is known.
- `unknown`: the capability could not be checked through an official path.

`unknown` is blocking for a required capability in L2/L3.

## Repair Policy

Try to repair the exact required capability up to three times only when there is an official repair path. Examples:

- load or discover the named skill, plugin, app, or MCP tool;
- refresh connector/app auth through the official client path;
- verify the specific GA4 property, advertiser account, or sheet access;
- restart or reload the official MCP/app server path when the runtime supports it;
- install project dependencies through the checked-in project dependency manifest.

Do not count a substitute tool or manual process as a repair. User approval cannot override a failed required capability.

## Canonical Registry

Use these names in plans, matrices, manifests, and final reports. Do not invent ad hoc aliases.

| Capability | Canonical name | Required when | Check method | Official repair path | Stop condition |
| --- | --- | --- | --- | --- | --- |
| Structured user question | `tool/requestUserInput` / `request_user_input` | L2/L3 needs a blocking user choice, production approval, or final scope confirmation | Verify the model-facing tool is exposed in the current mode/client before asking | Switch/re-run in a Codex mode or client that exposes the official app-server capability | Not exposed, unauthorized, setup error, or unknown |
| Requirement coverage | `$requirement-checker` | All L2/L3; high-risk L1 | Verify the skill is listed, readable, and callable | Discover/load the skill through the official skill path; fix missing skill installation if available | Missing for L2/L3 |
| GA4 evidence | `$google-analytics` | GA4 metrics, ecommerce revenue/orders, channel/source analysis, transaction detail, or GA4-vs-platform reconciliation | Verify skill/tool exposure, property access, dimensions, metrics, filters, timezone, and currency | Load skill/tool; verify property/account auth; repair connector/MCP auth if supported | Required GA4 pull cannot be performed |
| Impact evidence | `$mcp-impact-affiliate-orders` | Impact advertiser/platform evidence, Impact gap analysis, Impact publisher/order reconciliation | Verify MCP/skill exposure, advertiser account, date lens, pagination, and a safe test query path | Load MCP/skill; verify advertiser/auth; repair connector/MCP auth if supported | Required Impact evidence cannot be pulled |
| CJ evidence | `$mcp-commission-junction-affiliate-orders` | CJ advertiser/platform evidence, CJ gap analysis, CJ launch/zero-row interpretation, or CJ publisher/order reconciliation | Verify MCP/skill exposure, advertiser account, date lens, status fields, and a safe test query path | Load MCP/skill; verify advertiser/auth; repair connector/MCP auth if supported | Required CJ evidence cannot be pulled |
| TradeDoubler evidence | `$mcp-tradedoubler-affiliate-orders` | TradeDoubler markets, European affiliate evidence, or TD publisher/order reconciliation | Verify MCP/skill exposure, advertiser account, date lens, validation status, and a safe test query path | Load MCP/skill; verify advertiser/auth; repair connector/MCP auth if supported | Required TD evidence cannot be pulled |
| Google Sheets source | `google-drive:google-sheets` | Connected target, publisher, CRM, mapping, or planning data lives in Google Sheets | Verify Google Drive/Sheets app or skill exposure and sheet access | Load Google Drive/Sheets app; repair connector auth through official app path | Required sheet cannot be read |
| Local spreadsheet work | `Spreadsheets` | Local CSV/XLSX analysis, target workbooks, chart/table artifacts, or spreadsheet generation | Verify skill exposure and local file readability | Load skill; install project dependencies only through checked-in dependency manifest when needed | Required spreadsheet work cannot be performed |
| Branded HTML generation | `$anker-brand-html-generation` | ANKER/eufyMake branded HTML report output | Verify skill exposure, reference/assets availability, and local output path | Load skill; restore missing checked-in references/assets | Required branded report cannot be generated |
| Production HTML QA | `scripts/browser_qa_report.mjs` / Playwright Chromium | L3 HTML report QA and acceptance | Verify Node runtime can import Playwright, auto-start a localhost server, open desktop 1280x720 and mobile 390x844, capture screenshots, and write `browser_qa_summary.json` | Run `make setup-reporting` or let `scripts/run_affiliate_report.py` prepare Node dependencies; repair the exact Node/Playwright runtime | Required L3 HTML QA cannot run |
| Interactive Browser debug | `browser:browser` via `node_repl` `js` + Browser `browser-client.mjs` | Human/debug preview after automated QA finds a visual issue or when the user asks to inspect in Browser | Verify Browser plugin is enabled, `node_repl` `js` is exposed, `scripts/browser-client.mjs` exists, and the `iab` browser can open the target local URL/file | Load Browser plugin, discover `node_repl js`, retry Browser bootstrap through the official Browser skill path | Does not replace automated production QA unless the scoped run explicitly requires interactive Browser evidence |
| UI debugging helper | `build-web-apps:frontend-testing-debugging` | Debugging report UI before final Browser QA | Verify skill exposure when UI debugging is needed | Load skill/plugin if available | Does not replace production Browser QA; only blocks if specifically required |
| Publish/deploy | `cloudflare:wrangler` / `cloudflare:cloudflare` | User asks to publish, deploy, host, or make a live URL | Verify Cloudflare skill/tool exposure, project config, and auth | Load Cloudflare plugin; repair auth/config through official path | Publishing requested but tool unavailable |
| Current public web context | Built-in web search | Current external market/public context is requested or necessary | Verify browsing/search is available before relying on web evidence | Use official available search path | External context requested but unavailable |

Conditional capabilities become required as soon as the scoped request needs them. Mark them `not_applicable` only after the scope makes them irrelevant.

## Required Stop Message

When any required capability remains unavailable after inventory and allowed repairs, stop with:

`I cannot start L2/L3 production work because one or more required capabilities are not ready. I checked all required and conditional capabilities in the matrix below, attempted only official repairs for the original capabilities, and did not use any workaround. Production pulls, report generation, and QA are blocked until the failed required capabilities are available.`
