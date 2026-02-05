#!/bin/bash
# Run a single example and view its log as a tree

if [ -z "$1" ]; then
    echo "Usage: ./run_single.sh <example_number>"
    echo ""
    echo "Available examples:"
    echo "  1 - Basic Logging"
    echo "  2 - Actions and Nested Operations"
    echo "  3 - Error Handling"
    echo "  4 - API Server Simulation"
    echo "  5 - Data Pipeline"
    echo "  6 - Deep Nesting (7 levels) ⭐ NEW!"
    echo ""
    echo "Example: ./run_single.sh 1"
    exit 1
fi

cd "$(dirname "$0")"

example_file="example_0${1}_*.py"
example_file=$(ls $example_file 2>/dev/null | head -1)

if [ -z "$example_file" ]; then
    echo "Error: Example $1 not found"
    exit 1
fi

echo "======================================================================"
echo "Running: $example_file"
echo "======================================================================"
echo ""

python "$example_file"

# Get corresponding log file
log_file="${example_file%.py}.log"

if [ -f "$log_file" ]; then
    echo ""
    echo "======================================================================"
    echo "Tree View: $log_file"
    echo "======================================================================"
    echo ""
    python view_tree.py "$log_file"
fi
