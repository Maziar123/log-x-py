#!/bin/bash
# Run comprehensive example and analyze with parse_comprehensive.py
# Usage: ./run_and_analyze.sh

set -e  # Exit on error

echo "=========================================="
echo "🚀 LogXPy Run & Analyze Pipeline"
echo "=========================================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Step 1: Delete all existing log files
echo "🧹 Cleaning up old log files..."
rm -f *.log
echo "   ✓ Removed all .log files"

# Get project root (two levels up from comp-with-parser)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Set up Python path - need the logxpy parent dir (not project root)
export PYTHONPATH="$PROJECT_ROOT/logxpy:$PYTHONPATH"

# Step 2: Run the example script
echo ""
echo "▶️  Running example_09_comprehensive.py..."
python example_09_comprehensive.py

# Step 3: Check if log file was created
echo ""
echo "🔍 Checking for log file..."
LOG_FILE=$(ls -t *.log 2>/dev/null | head -1)

if [ -z "$LOG_FILE" ]; then
    echo "   ❌ ERROR: No log file found!"
    exit 1
fi

echo "   ✓ Log file created: $LOG_FILE"
echo "   📄 Size: $(ls -lh "$LOG_FILE" | awk '{print $5}')"
echo "   📊 Lines: $(wc -l < "$LOG_FILE")"

# Step 4: Run the parser
echo ""
echo "🔎 Running parser on $LOG_FILE..."
python parse_comprehensive.py "$LOG_FILE"

# Step 5: View FULL log with logxpy_cli_view (rich colors)
echo ""
echo "🌲 Viewing FULL log with logxpy_cli_view (rich colors)..."
echo "----------------------------------------"

# Use logxpy_cli_view with rich color themes
export PYTHONPATH="$PROJECT_ROOT/logxpy_cli_view/src:$PROJECT_ROOT/logxpy:$PYTHONPATH"

# Try to use logxpy_cli_view, fallback to view_tree.py
if /mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py/.venv/bin/python -c "import logxpy_cli_view" 2>/dev/null; then
    echo "   📊 Rendering with DarkBackgroundTheme (rich colors)..."
    echo ""
    /mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py/.venv/bin/python -m logxpy_cli_view._cli render "$LOG_FILE"
else
    # Fallback to view_tree.py
    echo "   ⚠️  logxpy_cli_view not available, using view_tree.py"
    VIEW_TREE="$PROJECT_ROOT/examples-log-view/complete-example-01/view_tree.py"
    if [ -f "$VIEW_TREE" ]; then
        python "$VIEW_TREE" "$LOG_FILE"
    else
        echo "   ❌ No viewer available"
    fi
fi

# Step 6: View tree with line numbers and colors
echo ""
echo "🎨 Viewing tree with line numbers and full color blocks..."
echo "----------------------------------------"

PYTHON_VENV="/mnt/N1/MZ/AMZ/Projects/Prog/a_cross/log-x-py/.venv/bin/python"

# Show tree with line numbers - highlight colored entries (lines 108-125)
$PYTHON_VENV view_tree_colored.py "$LOG_FILE" 2>&1 | grep -A 5 "\[10[0-9]\|\[11[0-9]\|\[12[0-5]\]" | head -60

echo ""
echo "📚 New logxpy color methods:"
echo "   log.set_foreground('cyan')       - Set text color"
echo "   log.set_background('red')        - Set background color"
echo "   log.reset_foreground()           - Reset text color"
echo "   log.reset_background()           - Reset background color"
echo "   log.colored('msg', fg='y', bg='b')  - One-shot colored message"

echo ""
echo "=========================================="
echo "✅ Pipeline complete!"
echo "=========================================="
