# Makefile for Régie des Eaux Montpellier integration
# Uses uv for dependency management (recommended)

UV := uv
PYTHON := .venv/bin/python
PROJECT_DIR := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))

.PHONY: help setup clean test run lint format test-workflow debug-workflow

# Default target
help:
	@echo "Régie des Eaux Montpellier - Development Commands"
	@echo "==============================================="
	@echo ""
	@echo "Environment Setup:"
	@echo "  make setup          # Create virtual env with uv"
	@echo "  make clean          # Remove virtual env"
	@echo ""
	@echo "Testing:"
	@echo "  make test           # Run all tests with pytest"
	@echo "  make test-cov       # Run tests with coverage"
	@echo "  make test-watch     # Run tests in watch mode"
	@echo "  make test-workflow  # Run tests as in GitHub workflow (excludes auth tests)"
	@echo ""
	@echo "Development:"
	@echo "  make run            # Run standalone test (needs REGIE_USERNAME/PASSWORD)"
	@echo "  make shell          # Activate virtual env in shell"
	@echo "  make lint           # Run code linting"
	@echo "  make format         # Format code"
	@echo ""
	@echo "CI/CD Debug:"
	@echo "  make debug-workflow # Reproduce full GitHub Actions workflow locally"
	@echo ""
	@echo "Home Assistant:"
	@echo "  make ha-setup       # Setup for HA development"

# Setup virtual environment with uv
setup:
	@echo "📦 Setting up development environment with uv..."
	$(UV) venv --python-preference only-managed
	$(UV) pip install -e '.'
	$(UV) pip install ".[dev]"
	@echo "✅ Environment setup complete!"
	@echo "   Activate with: source .venv/bin/activate"

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	rm -rf .venv
	@echo "✅ Cleaned up"

# Install dependencies only (no venv)
install:
	$(UV) pip install -e '.'
	$(UV) pip install ".[dev]"

# Run tests
test:
	@echo "🧪 Running tests..."
	$(PYTHON) -m pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	$(PYTHON) -m pytest tests/ -v --tb=short --cov=custom_components --cov=standalone --cov-report=term-missing

# Run tests in watch mode (requires watchmedo)
test-watch:
	@echo "👀 Watching for changes and running tests..."
	@echo "Installing watchmedo..."
	$(UV) pip install watchmedo
	$(PYTHON) -m pytest --watch tests/

# Run standalone test
run:
	@if [ -z "$(REGIE_USERNAME)" ] || [ -z "$(REGIE_PASSWORD)" ]; then \
		echo "❌ REGIE_USERNAME and REGIE_PASSWORD environment variables required"; \
		echo ""; \
		echo "Set them first:"; \
		echo "  export REGIE_USERNAME=your@email.com"; \
		echo "  export REGIE_PASSWORD=your_password"; \
		exit 1; \
	fi
	@echo "🚀 Running standalone test..."
	$(PYTHON) test_standalone.py --full --verbose

# Run standalone test with coordinator
run-coordinator:
	@if [ -z "$(REGIE_USERNAME)" ] || [ -z "$(REGIE_PASSWORD)" ]; then \
		echo "❌ REGIE_USERNAME and REGIE_PASSWORD environment variables required"; \
		exit 1; \
	fi
	@echo "🚀 Running coordinator test..."
	$(PYTHON) test_standalone.py --coordinator --full --verbose

# Activate shell with virtual env
shell:
	@echo "🐚 Starting shell with virtual environment..."
	. .venv/bin/activate && bash

# Lint code (same directories as GitHub workflow)
lint:
	@echo "🔍 Running linting..."
	$(UV) pip install ruff
	$(PYTHON) -m ruff check custom_components/regiedeseauxmpl/

# Format code
format:
	@echo "💇 Formatting code..."
	$(UV) pip install ruff
	$(PYTHON) -m ruff format custom_components standalone tests examples scripts

# Setup for Home Assistant development
ha-setup:
	@echo "🏠 Setting up for Home Assistant development..."
	@echo "   This copies the integration to HA config directory"
	@echo "   Not implemented yet - HA uses HACS"

# Show Python version
python-version:
	@$(PYTHON) --version

# Show uv version
uv-version:
	@$(UV) --version

# Show installed packages
pkgs:
	@echo "📦 Installed packages:"
	$(UV) pip list

# Run tests as in GitHub workflow (excludes tests requiring real credentials)
test-workflow:
	@echo "🧪 Running tests as in GitHub workflow..."
	REGIE_USERNAME="test@example.com" REGIE_PASSWORD="test_password" $(UV) run pytest tests/ -v --tb=short -k "not test_authentication and not test_meter_index"

# Debug GitHub Actions workflow locally
debug-workflow:
	@echo "🔍 Debugging full GitHub Actions workflow..."
	@chmod +x scripts/debug_workflow.sh
	./scripts/debug_workflow.sh

# Sync dependencies (update lock file)
sync:
	$(UV) lock

# Update dependencies
update:
	$(UV) lock --upgrade
	$(UV) pip install -e '.'
	$(UV) pip install ".[dev]"
