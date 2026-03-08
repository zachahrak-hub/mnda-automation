#!/bin/bash
# ============================================================
# MNDA Automation — one-command installer
# Usage: bash install.sh
# ============================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "=================================================="
echo "   MNDA Automation — Setup"
echo "=================================================="
echo ""

# ----------------------------------------------------------
# 1. Check Python version
# ----------------------------------------------------------
echo "Checking Python version..."
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}Error: python3 not found. Install Python 3.9+ from https://python.org${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED="3.9"

if python3 -c "import sys; exit(0 if sys.version_info >= (3,9) else 1)"; then
    echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"
else
    echo -e "${RED}Error: Python $REQUIRED or higher required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

# ----------------------------------------------------------
# 2. Create virtual environment
# ----------------------------------------------------------
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created (.venv)${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate
source .venv/bin/activate

# ----------------------------------------------------------
# 3. Install dependencies
# ----------------------------------------------------------
echo ""
echo "Installing dependencies..."
pip install --upgrade pip --quiet
pip install -e . --quiet
echo -e "${GREEN}✓ Dependencies installed${NC}"

# ----------------------------------------------------------
# 4. Set up .env file
# ----------------------------------------------------------
echo ""
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}! .env file created from template.${NC}"
    echo -e "${YELLOW}  Open .env and fill in your API keys before running.${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# ----------------------------------------------------------
# 5. Create local storage folder
# ----------------------------------------------------------
mkdir -p reviews
mkdir -p credentials
echo -e "${GREEN}✓ Storage folders ready (reviews/, credentials/)${NC}"

# ----------------------------------------------------------
# Done
# ----------------------------------------------------------
echo ""
echo "=================================================="
echo -e "${GREEN}   Setup complete!${NC}"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "  1. Edit .env with your settings:"
echo "       nano .env   (or open in your editor)"
echo ""
echo "  2. Activate the environment (each new terminal session):"
echo "       source .venv/bin/activate"
echo ""
echo "  3. Review your first MNDA:"
echo "       mnda review --file path/to/nda.pdf"
echo ""
echo "  4. Start the email watcher:"
echo "       mnda watch-email"
echo ""
echo "  5. Start the Slack bot:"
echo "       mnda watch-slack"
echo ""
echo "  Full setup guide: README.md"
echo ""
