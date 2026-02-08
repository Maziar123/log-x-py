#!/bin/bash
# Quick viewer for LogXPy color test logs
#
# Usage: ./view_color_log.sh [option]
# Options:
#   --ascii    View with ASCII characters only
#   --no-color View without color codes
#   --stats    Show statistics
#   --tail     Live tail the log file

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOGXPY_VIEW="$PROJECT_ROOT/.venv/bin/logxpy-cli-view"
LOG_FILE="$SCRIPT_DIR/xx_Color_Methods1.log"

# Parse arguments
VIEW_ARGS=()
for arg in "$@"; do
    case "$arg" in
        --ascii)
            VIEW_ARGS+=(--ascii)
            ;;
        --no-color)
            VIEW_ARGS+=(--no-colors)
            ;;
        --stats)
            exec "$LOGXPY_VIEW" stats "$LOG_FILE"
            ;;
        --tail)
            exec "$LOGXPY_VIEW" tail "$LOG_FILE"
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Usage: $0 [--ascii|--no-color|--stats|--tail]"
            exit 1
            ;;
    esac
done

# View the log file
"$LOGXPY_VIEW" render "$LOG_FILE" "${VIEW_ARGS[@]}" --color=always
