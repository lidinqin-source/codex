# Affiliate Data Analyst Maintenance Guide

## Purpose

This repository tracks the reusable affiliate reporting skill package, not every local report run. Keep the skill small, auditable, and safe to reuse across market, cadence, and platform variants.

## Commit Policy

Commit these by default:

- `.agents/skills/affiliate-data-analyst/SKILL.md`
- `.agents/skills/affiliate-data-analyst/agents/`
- `.agents/skills/affiliate-data-analyst/assets/`
- `.agents/skills/affiliate-data-analyst/references/`
- `requirements.txt`
- `.gitignore`
- `docs/`

Do not commit these by default:

- `affiliate_reports/`
- `reports/`
- `output/`
- top-level `scripts/`
- top-level scratch reference files such as `goal-pacing.md`
- credentials, tokens, browser sessions, raw platform exports, or local caches

If a generated artifact must be preserved for audit, add it intentionally with `git add -f <path>` and explain why in the commit message.

## Safe Git Workflow

Use targeted staging. Do not use `git add .` in this repo.

```bash
git status --short --untracked-files=all
git add .agents/skills/affiliate-data-analyst requirements.txt .gitignore docs/affiliate-data-analyst-maintenance.md
git status --short
git commit -m "Maintain affiliate data analyst skill"
```

Push only after reviewing the staged diff:

```bash
git diff --cached --stat
git diff --cached
git push origin main
```

## Skill Change Checklist

Before editing, classify the request:

- L0: quick explanation or read-only orientation.
- L1: lightweight local file update.
- L2: report logic, source rules, or validation behavior.
- L3: production report generation or final report QA.

For L2/L3 changes, verify that the skill still preserves these rules:

- Tool Availability Preflight happens before production work.
- Required tools are repaired up to 3 times; if still unavailable, stop and tell the user.
- No unsupported workaround replaces a required source tool.
- `requirement-checker` is used for L2/L3 requirement coverage.
- `browser:browser` is the production HTML QA tool.
- Playwright may support debugging, but it is not the L3 production QA fallback.
- Report bundle schema uses `report_title`, `report`, and `report.source_files`.

## Platform Context

Keep platform-specific context in references, not scattered through the main workflow:

- `references/platform-context.md`: launch timing, zero-row interpretation, platform caveats.
- `references/impact-actions-standard.md`: Impact Actions pull and reconciliation rules.
- `references/measurement-contract.md`: metric definitions and reconciliation contract.
- `references/reconciliation-and-artifacts.md`: artifact requirements and evidence packaging.
- `references/weekly-report-standard.md`: cadence-specific output expectations.
- `references/goal-pacing.md`: target and pacing logic.

When CJ, Impact, TradeDoubler, GA4, or Google Sheets behavior changes, update the relevant reference first, then add only the minimum main `SKILL.md` rule needed to enforce it.

## Runtime Maintenance

Keep Python dependencies in `requirements.txt`. Do not assume a preinstalled Python environment has GA4 or Google API packages.

For local verification:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

If this repo is used by an automated Codex environment, create a dedicated local environment setup step that installs `requirements.txt` before production runs.

## Audit Commands

Run these before reporting a skill maintenance pass as complete:

```bash
git status --short --untracked-files=all
rg -n "coupon|orderCoupon|KOL|Codex bundled Python|lookup/|docs/weekly-report-standard|must not directly connect|analyze data by yourself|Playwright fallback|single US monthly|canonical status|one-off script" .agents/skills/affiliate-data-analyst --glob '!**/run-log.md'
find .agents/skills/affiliate-data-analyst -name '.DS_Store' -print
python3 -m py_compile scripts/*.py 2>/dev/null || true
```

The `rg` command should return no active-rule matches. Historical `run-log.md` may contain old incident language and should not be rewritten unless the history itself is wrong.

## Report Artifact Promotion

Generated reports are ignored by default because they can contain order-level commercial data and run-specific evidence.

Promote an artifact only when all are true:

- The user explicitly wants it versioned.
- Raw rows and sensitive fields have been reviewed.
- The artifact is useful beyond one local run.
- The commit message names the market, period, cadence, and reason.

Prefer promoting reusable rules into the skill references instead of committing one-off report outputs.
