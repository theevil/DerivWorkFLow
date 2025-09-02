#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Setting up pre-commit hooks for DerivWorkFLow...${NC}"

# Check if we're in the project root
if [ ! -f "package.json" ] || [ ! -f ".pre-commit-config.yaml" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

# Install frontend dependencies
echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
cd apps/frontend
npm install
cd ../..

# Install backend dependencies
echo -e "${YELLOW}🐍 Installing backend dependencies...${NC}"
cd apps/backend
pipenv install --dev
cd ../..

# Install pre-commit
echo -e "${YELLOW}🔧 Installing pre-commit...${NC}"
cd apps/backend
pipenv install pre-commit
cd ../..

# Install pre-commit hooks
echo -e "${YELLOW}📎 Installing pre-commit hooks...${NC}"
cd apps/backend
pipenv run pre-commit install
cd ../..

# Run pre-commit on all files to set up the baseline
echo -e "${YELLOW}🔍 Running pre-commit on all files to set up baseline...${NC}"
cd apps/backend
pipenv run pre-commit run --all-files
cd ../..

# Create secrets baseline
echo -e "${YELLOW}🔐 Creating secrets baseline...${NC}"
cd apps/backend
pipenv run detect-secrets scan --baseline ../../.secrets.baseline
cd ../..

echo -e "${GREEN}✅ Pre-commit setup completed successfully!${NC}"
echo -e "${BLUE}📝 Available commands:${NC}"
echo -e "  • ${GREEN}npm run pre-commit:run${NC} - Run pre-commit on all files"
echo -e "  • ${GREEN}npm run pre-commit:run-changed${NC} - Run pre-commit on changed files"
echo -e "  • ${GREEN}npm run format:all${NC} - Format all code"
echo -e "  • ${GREEN}npm run lint:all${NC} - Lint all code"
echo -e "  • ${GREEN}npm run type-check:all${NC} - Type check all code"
echo -e ""
echo -e "${BLUE}🎯 Pre-commit hooks will now run automatically on every commit!${NC}"
