#!/bin/bash
# Run 3-level nested colored example and view it

cd "$(dirname "$0")"

# Generate log if needed
if [ ! -f "xxx_3level_nested_colored.log" ] || [ "xxx_3level_nested_colored.py" -nt "xxx_3level_nested_colored.log" ]; then
    echo "Generating log file..."
    uv run python xxx_3level_nested_colored.py
fi

# View based on argument
case "${1:-}" in
    tree|t) uv run logxpy-cli-view render xxx_3level_nested_colored.log --format tree ;;
    nocolor|nc) uv run logxpy-cli-view render xxx_3level_nested_colored.log --color never ;;
    *) uv run logxpy-cli-view render xxx_3level_nested_colored.log ;;  # default: oneline
esac
