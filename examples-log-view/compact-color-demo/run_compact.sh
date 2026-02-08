#!/bin/bash
# Compact demo - deep nesting with 2 colored blocks

cd "$(dirname "$0")"
echo "============================================================"
echo "  Compact Demo - Deep Function Tree + 2 Colored Blocks"
echo "============================================================"

PY="python"
if command -v uv &> /dev/null; then
    PY="uv run python"
fi

echo ""
echo "[1/3] Creating log..."
$PY compact_color_demo.py

echo ""
echo "[2/3] Parsing tree..."
$PY compact_parser.py compact_color.log

echo ""
echo "[3/3] Tree view with colors..."
echo "      (screenshot this for GitHub)"
echo ""

# Use real tree viewer (complete-example-01) - builds proper tree with ├── └── │
if [ -f "../complete-example-01/view_tree.py" ]; then
    $PY ../complete-example-01/view_tree.py compact_color.log
# Fallback to flat list viewer (comp-with-parser) - shows line numbers with colors
elif [ -f "../comp-with-parser/view_tree_colored.py" ]; then
    $PY ../comp-with-parser/view_tree_colored.py compact_color.log 2>/dev/null
else
    cat compact_color.log | $PY -m json.tool --compact 2>/dev/null || cat compact_color.log
fi

echo ""
echo "============================================================"
echo "  Done! Entries: $(wc -l < compact_color.log) | Depth: 4 | Blocks: 2"
echo "============================================================"
