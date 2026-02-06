#!/bin/bash
# Setup script for local-only git files
# Run: ./setup-local-git.sh

set -e

echo "🔧 Setting up local-only git configuration..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo -e "${RED}❌ Error: Not a git repository${NC}"
    echo "Run this from the project root."
    exit 1
fi

# Create local directories
echo "📁 Creating local-only directories..."
mkdir -p local/secrets
mkdir -p local/experiments
mkdir -p local/notes
mkdir -p local/scripts
echo -e "${GREEN}✓${NC} Created: local/{secrets,experiments,notes,scripts}"

# Install pre-push hook
if [ -f git-hooks/pre-push ]; then
    echo ""
    echo "🔒 Installing pre-push hook..."
    cp git-hooks/pre-push .git/hooks/pre-push
    chmod +x .git/hooks/pre-push
    echo -e "${GREEN}✓${NC} Installed: .git/hooks/pre-push"
else
    echo -e "${YELLOW}⚠ Warning: git-hooks/pre-push not found${NC}"
fi

# Create sample local config
cat > local/.gitkeep << 'EOF'
# This directory is for LOCAL-ONLY files
# Contents will NOT be pushed to GitHub (enforced by pre-push hook)
#
# Put here:
# - API keys and secrets
# - Personal notes
# - Local experiments
# - Credentials
EOF
echo -e "${GREEN}✓${NC} Created: local/.gitkeep"

# Add to .git/info/exclude (like .gitignore but local-only)
if ! grep -q "^local/$" .git/info/exclude 2>/dev/null; then
    echo "" >> .git/info/exclude
    echo "# Local-only directories (not pushed to GitHub)" >> .git/info/exclude
    echo "local/" >> .git/info/exclude
    echo -e "${GREEN}✓${NC} Added 'local/' to .git/info/exclude"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  1. Put local files in: local/"
echo "  2. Commit locally: git add local/ && git commit -m 'Local updates'"
echo "  3. Push to GitHub: git push (BLOCKED if local files are staged!)"
echo ""
echo "To test the hook:"
echo "  echo 'test' > local/test.txt"
echo "  git add local/test.txt && git commit -m 'Test'"
echo "  git push  # Should be blocked"
echo ""
echo "To bypass (DANGER): git push --no-verify"
