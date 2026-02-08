#!/bin/bash
# Run all examples and view their logs as trees

cd "$(dirname "$0")"

echo "======================================================================"
echo "Running All Log Examples with Tree Visualization"
echo "======================================================================"

for example in example_*.py; do
    echo ""
    echo "----------------------------------------------------------------------"
    echo "Running: $example"
    echo "----------------------------------------------------------------------"
    python "$example"
    
    # Get corresponding log file
    log_file="${example%.py}.log"
    
    if [ -f "$log_file" ]; then
        echo ""
        echo "======================================================================"
        echo "Tree View: $log_file"
        echo "======================================================================"
        echo ""
        python view_tree.py "$log_file"
    fi
    
    echo ""
    read -p "Press Enter to continue to next example..."
done

echo ""
echo "======================================================================"
echo "All examples completed!"
echo "======================================================================"
