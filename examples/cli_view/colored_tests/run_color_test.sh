#!/bin/bash
# Run Color Methods Example and View with logxpy-cli-view
#
# This script runs the LogXPy color methods example to generate a log file,
# then displays it using logxpy-cli-view with various options.

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Paths
PYTHON="$PROJECT_ROOT/.venv/bin/python"
LOGXPY_VIEW="$PROJECT_ROOT/.venv/bin/logxpy-cli-view"
EXAMPLE_PY="$SCRIPT_DIR/xx_Color_Methods1.py"
EXAMPLE_LOG="$SCRIPT_DIR/xx_Color_Methods1.log"

echo "=========================================="
echo "LogXPy Color Methods Test Runner"
echo "=========================================="
echo ""

# Step 1: Generate the log file
echo "[1/3] Generating log file from Python script..."
cd "$SCRIPT_DIR"
"$PYTHON" "$EXAMPLE_PY"
echo "✓ Log file generated: $EXAMPLE_LOG"
echo ""

# Step 2: Show with colors
echo "[2/3] Viewing log file with COLORS enabled..."
echo "----------------------------------------"
"$LOGXPY_VIEW" render "$EXAMPLE_LOG" --color=always
echo ""
echo "----------------------------------------"
echo ""

# Step 3: Show available options
echo "[3/3] Other viewing options:"
echo ""
echo "  View with ASCII:"
echo "    $LOGXPY_VIEW render $EXAMPLE_LOG --ascii"
echo ""
echo "  View without colors:"
echo "    $LOGXPY_VIEW render $EXAMPLE_LOG --no-colors"
echo ""
echo "  View with human-readable timestamps:"
echo "    $LOGXPY_VIEW render $EXAMPLE_LOG --human-readable"
echo ""
echo "  Live tail (follow) the log:"
echo "    $LOGXPY_VIEW tail $EXAMPLE_LOG"
echo ""
echo "  Show statistics:"
echo "    $LOGXPY_VIEW stats $EXAMPLE_LOG"
echo ""
echo "=========================================="
echo "Done!"
echo "=========================================="
