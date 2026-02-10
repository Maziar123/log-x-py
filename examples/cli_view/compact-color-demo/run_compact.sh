#!/bin/bash
# Compact demo - deep nesting with 2 colored blocks

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PYTHON="$PROJECT_ROOT/.venv/bin/python"
LOGXPY_VIEW="$PROJECT_ROOT/.venv/bin/logxpy-cli-view"

cd "$SCRIPT_DIR"
echo "============================================================"
echo "  Compact Demo - Color Blocks Test"
echo "============================================================"

echo ""
echo "[1/3] Creating log..."
"$PYTHON" compact_color_demo.py

echo ""
echo "[2/3] Creating simple color test..."
"$PYTHON" simple_color_test.py

echo ""
echo "[3/4] Tree view with simple_color.log..."
echo "      (screenshot this for GitHub)"
echo ""

# Use logxpy-cli-view for tree rendering
"$LOGXPY_VIEW" render simple_color.log --color=always

echo ""
echo "[4/4] Statistics..."
"$LOGXPY_VIEW" stats simple_color.log

echo ""
echo "============================================================"
echo "  Note: compact_color_demo.py uses @logged decorator which"
echo "  creates sibling actions at the same task level - this is"
echo "  a known limitation. Use simple_color_test.py for now."
echo "============================================================"
echo ""
echo "Other viewing options:"
echo "  View with ASCII: $LOGXPY_VIEW render $PWD/simple_color.log --ascii"
echo "  Live tail: $LOGXPY_VIEW tail $PWD/simple_color.log"
echo "============================================================"
