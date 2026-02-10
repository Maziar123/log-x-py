#!/bin/bash
# Demo script showcasing all modern tree viewer features

cd "$(dirname "$0")"

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║   Modern Log Tree Viewer - Feature Demonstration                ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: Default mode (colors + emojis)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Test 1: Default Mode (Colors + Emojis)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: python view_tree.py example_02_actions.log"
echo ""
python view_tree.py example_02_actions.log | head -35
echo ""
read -p "Press Enter to continue..."
echo ""

# Test 2: ASCII mode
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Test 2: ASCII Mode (Plain Text)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: python view_tree.py example_02_actions.log --ascii"
echo ""
python view_tree.py example_02_actions.log --ascii | head -30
echo ""
read -p "Press Enter to continue..."
echo ""

# Test 3: No emojis
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 Test 3: Colors Only (No Emojis)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: python view_tree.py example_02_actions.log --no-emojis"
echo ""
python view_tree.py example_02_actions.log --no-emojis | head -30
echo ""
read -p "Press Enter to continue..."
echo ""

# Test 4: Deep nesting
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌲 Test 4: Deep Nesting (7 Levels)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: python view_tree.py example_06_deep_nesting.log"
echo ""
python view_tree.py example_06_deep_nesting.log | head -60
echo ""
read -p "Press Enter to continue..."
echo ""

# Test 5: Depth limit
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔢 Test 5: Depth Limit (Max 3 Levels)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: python view_tree.py example_06_deep_nesting.log --depth-limit 3"
echo ""
python view_tree.py example_06_deep_nesting.log --depth-limit 3 | head -50
echo ""
read -p "Press Enter to continue..."
echo ""

# Test 6: Error handling
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔥 Test 6: Error Visualization"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: python view_tree.py example_03_errors.log"
echo ""
python view_tree.py example_03_errors.log
echo ""
read -p "Press Enter to continue..."
echo ""

# Test 7: Complex API server
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔌 Test 7: API Server Logs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: python view_tree.py example_04_api_server.log"
echo ""
python view_tree.py example_04_api_server.log | head -50
echo ""
read -p "Press Enter to continue..."
echo ""

# Test 8: Data pipeline
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 Test 8: ETL Pipeline"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Command: python view_tree.py example_05_data_pipeline.log"
echo ""
python view_tree.py example_05_data_pipeline.log | head -40
echo ""

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║   Feature Demonstration Complete! ✨                             ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Summary of features demonstrated:"
echo "  ✅ Colors and ANSI styling"
echo "  ✅ Emoji indicators for types and statuses"
echo "  ✅ ASCII mode for compatibility"
echo "  ✅ Deep nesting support (7+ levels)"
echo "  ✅ Depth limiting for readability"
echo "  ✅ Error visualization"
echo "  ✅ Complex nested operations"
echo "  ✅ Zero external dependencies"
echo ""
