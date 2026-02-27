#!/bin/bash
# Democracy at Work Episodes Database - Deploy Script
# Runs scrapers, commits changes, and pushes to GitHub

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================="
echo "D@W Episodes - Deploy Script"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Run scraper
echo -e "${BLUE}[1/3] Running episode scraper...${NC}"
python3 scraper_multi.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Scraper completed${NC}"
else
    echo -e "${YELLOW}⚠ Scraper encountered issues (continuing)${NC}"
fi
echo ""

# 2. Run YouTube matcher
echo -e "${BLUE}[2/3] Running YouTube matcher...${NC}"
python3 youtube_matcher_multi.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ YouTube matcher completed${NC}"
else
    echo -e "${YELLOW}⚠ YouTube matcher encountered issues (continuing)${NC}"
fi
echo ""

# 3. Commit and push to GitHub
echo -e "${BLUE}[3/3] Deploying to GitHub...${NC}"

# Check if there are changes
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}No changes detected${NC}"
    echo ""
else
    # Stage episode data files
    git add -f shows/*/data/episodes.json
    
    # Commit with timestamp
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    git commit -m "chore: auto-update episodes [$TIMESTAMP]" || echo "No changes to commit"
    
    # Push to GitHub
    if git push; then
        echo -e "${GREEN}✓ Successfully pushed to GitHub${NC}"
    else
        echo -e "${YELLOW}⚠ Push failed - check your git configuration${NC}"
    fi
fi

echo ""
echo -e "${GREEN}========================================="
echo "Deployment complete!"
echo "=========================================${NC}"
echo ""
echo "Latest episodes available at:"
echo "https://umasshia.github.io/daw-shows"
echo ""
