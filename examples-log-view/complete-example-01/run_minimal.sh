#!/bin/bash
# Minimal color demo - 3 steps in 1 script

cd "$(dirname "$0")"
echo "=========================================="
echo "  Minimal Logging Demo"
echo "=========================================="

# Detect Python runner (uv run or python)
if command -v uv &> /dev/null; then
    PY="uv run python"
else
    PY="python"
fi

# Step 1: Create log
echo ""
echo "[1/3] Creating log..."
$PY minimal_color_demo.py

# Step 2: Parse
echo ""
echo "[2/3] Parsing log..."
$PY minimal_parser.py minimal_color.log

# Step 3: View with colors
echo ""
echo "[3/3] Tree view with colors..."
echo "      (screenshot this for GitHub)"
echo ""

# Try different viewers in order of preference
if [ -f "../comp-with-parser/view_tree_colored.py" ]; then
    $PY ../comp-with-parser/view_tree_colored.py minimal_color.log 2>/dev/null
elif command -v logxpy-view &> /dev/null; then
    logxpy-view minimal_color.log
else
    echo "⚠️  Using basic viewer (install 'colored' for full color):"
    $PY view_tree.py minimal_color.log
fi

echo ""
echo "=========================================="
echo "  Done! Log entries: $(wc -l < minimal_color.log)"
echo "=========================================="
