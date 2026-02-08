#!/bin/bash
# View 3-level nested colored log
cd "$(dirname "$0")"
case "${1:-}" in
    tree|t) uv run logxpy-cli-view render xxx_3level_nested_colored.log --format tree ;;
    nocolor|nc) uv run logxpy-cli-view render xxx_3level_nested_colored.log --color never ;;
    *) uv run logxpy-cli-view render xxx_3level_nested_colored.log ;;
esac
