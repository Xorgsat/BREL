# ============================================================
# Browser Reliability Engineering Lab — Makefile
# ============================================================
# Usage:
#   make help          Show this help
#   make install       Install all Python and Node.js dependencies
#   make test          Run full Selenium experiment suite (parallel, 2 workers)
#   make test-seq      Run Selenium suite sequentially (useful for debugging)
#   make playwright    Run Playwright comparative suite
#   make benchmark     Run parallelism benchmark script
#   make report        Generate consolidated reliability reports
#   make compare       Run cross-framework comparison engine
#   make lint          Run ruff linter over Python source
#   make all           Install → test → playwright → report → compare
#   make clean         Remove generated artifacts and cache dirs
#   make tag           Create annotated git tag v$(VERSION)

SHELL := /bin/bash
.DEFAULT_GOAL := help

# ── Configuration ──────────────────────────────────────────
VERSION         := 1.0.0
PYTHON          := python
UV              := uv
NPX             := npx
PYTEST_FLAGS    := --headless -v
PYTEST_PARALLEL := -n 2
EXPERIMENTS_DIR := experiments
REPORTS_DIR     := reports

# ── Phony targets ──────────────────────────────────────────
.PHONY: help install install-python install-node test test-seq playwright \
        benchmark report compare lint clean tag all smoke

# ── Help ───────────────────────────────────────────────────
help: ## Show available targets
	@printf "\n\033[1mBrowser Reliability Engineering Lab — v$(VERSION)\033[0m\n\n"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@printf "\n"

# ── Installation ───────────────────────────────────────────
install: install-python install-node ## Install all dependencies (Python + Node.js)

install-python: ## Install Python dependencies via uv
	$(UV) venv --python 3.12 || true
	$(UV) pip install -e ".[dev]"
	@echo "✓  Python dependencies installed"

install-node: ## Install Node.js / Playwright dependencies
	npm ci
	$(NPX) playwright install --with-deps chromium
	@echo "✓  Node.js / Playwright dependencies installed"

# ── Testing ────────────────────────────────────────────────
smoke: ## Run smoke suite only (fast health check)
	$(UV) run pytest selenium-lab/tests/test_smoke_foundation.py $(PYTEST_FLAGS)

test: ## Run full Selenium experiment suite in parallel (2 workers), then network-sensitive tests sequentially
	$(UV) run pytest $(EXPERIMENTS_DIR)/ $(PYTEST_FLAGS) $(PYTEST_PARALLEL) \
	  --continue-on-collection-errors \
	  -m "not network_sensitive"
	$(UV) run pytest $(EXPERIMENTS_DIR)/ $(PYTEST_FLAGS) \
	  --continue-on-collection-errors \
	  -m "network_sensitive"

test-seq: ## Run Selenium suite sequentially (debugging mode)
	$(UV) run pytest $(EXPERIMENTS_DIR)/ $(PYTEST_FLAGS) \
	  --continue-on-collection-errors

test-exp-%: ## Run a specific experiment by number  e.g. make test-exp-09
	$(UV) run pytest $(EXPERIMENTS_DIR)/ -k "exp$*" $(PYTEST_FLAGS) \
	  --continue-on-collection-errors

# ── Playwright ─────────────────────────────────────────────
playwright: ## Run Playwright comparative suite (TypeScript)
	$(NPX) playwright test

playwright-report: ## Open last Playwright HTML report
	$(NPX) playwright show-report $(REPORTS_DIR)/playwright-report

# ── Analysis ───────────────────────────────────────────────
benchmark: ## Run parallelism benchmark (1-/2-/3-worker comparison)
	$(UV) run python scripts/benchmark_parallelism.py
	@echo "✓  Benchmark complete — see reports/reliability/"

report: ## Generate consolidated reliability + flaky-test reports
	$(UV) run python scripts/generate_report.py
	@echo "✓  Reports written to $(REPORTS_DIR)/"

compare: ## Run cross-framework Selenium vs Playwright comparison engine
	$(UV) run python scripts/compare_frameworks.py
	@echo "✓  Comparison report written to $(REPORTS_DIR)/framework_comparison.md"

# ── Code Quality ───────────────────────────────────────────
lint: ## Run ruff linter over Python sources
	$(UV) run ruff check selenium-lab/ experiments/ scripts/ controlled-app/ conftest.py

lint-fix: ## Run ruff with --fix to auto-correct safe issues
	$(UV) run ruff check --fix selenium-lab/ experiments/ scripts/ controlled-app/ conftest.py

# ── All-in-one ─────────────────────────────────────────────
all: install test playwright report compare ## Full pipeline: install → test → playwright → report → compare
	@echo ""
	@printf "\033[32m✓  BREL full pipeline complete — v$(VERSION)\033[0m\n"

# ── Versioning ─────────────────────────────────────────────
tag: ## Create annotated git tag vVERSION (default: v1.0.0)
	git tag -a "v$(VERSION)" -m "BREL v$(VERSION) — Production-quality Browser Reliability Engineering Lab"
	@echo "✓  Tag v$(VERSION) created. Push with: git push origin v$(VERSION)"

# ── Cleanup ────────────────────────────────────────────────
clean: ## Remove generated artifacts, caches, and temporary files
	find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -not -path "./.venv/*" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage test-results/
	rm -f artifacts/failures/**/* 2>/dev/null || true
	@echo "✓  Workspace cleaned"
