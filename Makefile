SHELL := /bin/sh

PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
PIP := $(if $(wildcard .venv/bin/pip),.venv/bin/pip,python3 -m pip)

.PHONY: setup-reporting affiliate-report validate-report browser-qa check

setup-reporting:
	@python3 -m venv .venv
	@.venv/bin/pip install -r requirements.txt
	@npm install --package-lock=false

affiliate-report:
	@test -n "$(MANIFEST)" || (echo "MANIFEST=affiliate_reports/.../run_manifest.json is required" >&2; exit 2)
	@$(PYTHON) scripts/run_affiliate_report.py --manifest "$(MANIFEST)" --quiet

validate-report:
	@test -n "$(MANIFEST)" || (echo "MANIFEST=affiliate_reports/.../run_manifest.json is required" >&2; exit 2)
	@$(PYTHON) scripts/validate_affiliate_report.py --manifest "$(MANIFEST)" --quiet

browser-qa:
	@test -n "$(MANIFEST)" || (echo "MANIFEST=affiliate_reports/.../run_manifest.json is required" >&2; exit 2)
	@node scripts/browser_qa_report.mjs --manifest "$(MANIFEST)" --quiet

check:
	@$(PYTHON) scripts/run_affiliate_report.py --manifest affiliate_reports/templates/run_manifest.us_monthly_mtd.json --validate-only --quiet
	@$(PYTHON) scripts/validate_affiliate_report.py --manifest affiliate_reports/templates/run_manifest.us_monthly_mtd.json --schema-only --quiet
