# AGENTS.md

## Repository Purpose

This repository contains eufyMake affiliate marketing analysis workflows, Codex
skills, report-generation scripts, schemas, and reusable run manifests.

## Operating Rules

- Treat `affiliate_reports/` outputs as local generated artifacts unless a file under
  `affiliate_reports/templates/` is intentionally tracked.
- Do not commit raw platform exports, GA4 exports, order-level evidence, credentials,
  tokens, cookies, or `.env` files.
- Keep reusable report logic under `scripts/lib/affiliate_report/` and reusable entry
  points under the tracked scripts allowed by `.gitignore`.
- Prefer manifest-driven runs over one-off hardcoded production scripts.
- Preserve market/date scope and target-source assumptions in run manifests and report
  bundles so reports are auditable.

## Verification

Run `make check` before reporting the repo as healthy. If validation cannot run,
state the exact command, reason, and residual risk.
