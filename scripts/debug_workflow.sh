#!/bin/bash
# Script to debug GitHub Actions workflow locally
# This reproduces the exact steps from test_and_release.yml

set -e  # Exit on error

echo "=========================================="
echo "Debugging GitHub Actions workflow locally"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo ""
echo -e "${YELLOW}Step 1: Checking Python version...${NC}"
python3 --version || { echo -e "${RED}Python 3.14 required${NC}"; exit 1; }

# Step 2: Install uv (if not already installed)
echo ""
echo -e "${YELLOW}Step 2: Checking uv...${NC}"
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi
uv --version

# Step 3: Create virtual environment with uv
echo ""
echo -e "${YELLOW}Step 3: Creating virtual environment with uv...${NC}"
rm -rf .venv
uv venv

# Step 4: Install dependencies
echo ""
echo -e "${YELLOW}Step 4: Installing dependencies...${NC}"
uv pip install -e ".[dev]"

# Step 5: Run linting
echo ""
echo -e "${YELLOW}Step 5: Running linting...${NC}"
uv pip install ruff
if uv run ruff check custom_components/regiedeseauxmpl/; then
    echo -e "${GREEN}✅ Linting passed!${NC}"
else
    echo -e "${RED}❌ Linting failed!${NC}"
    exit 1
fi

# Step 6: Run tests (without credentials, same as workflow)
echo ""
echo -e "${YELLOW}Step 6: Running tests...${NC}"
export REGIE_USERNAME="test@example.com"
export REGIE_PASSWORD="test_password"

if uv run pytest tests/ -v --tb=short -k "not test_authentication and not test_meter_index"; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Tests failed!${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Workflow completed successfully!${NC}"
echo "=========================================="
