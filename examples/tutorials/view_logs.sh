#!/bin/bash
#
# Convenient log viewing script
# Usage: ./view_logs.sh [tutorial_number] [options]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to display help
show_help() {
    echo "Log Viewer Helper Script"
    echo ""
    echo "Usage: $0 [tutorial_number] [viewer_options]"
    echo ""
    echo "Examples:"
    echo "  $0                    # View all logs"
    echo "  $0 1                  # View tutorial 01 logs"
    echo "  $0 5 --human-readable # View tutorial 05 with human-readable times"
    echo "  $0 all --action-status failed # View all logs, filter failed actions"
    echo ""
    echo "Available tutorials:"
    echo "  1 - Basic Logging"
    echo "  2 - Actions and Context"
    echo "  3 - Decorators"
    echo "  4 - Error Handling"
    echo "  5 - Real-World API Scenario"
    echo "  all - View all logs together"
    echo ""
    echo "Common viewer options:"
    echo "  --human-readable            Human-readable timestamps"
    echo "  --action-status failed      Filter by action status"
    echo "  --keyword WORD              Search for keyword"
    echo "  --field-limit N             Limit field display length"
    echo "  --color never               Disable colors"
    echo "  --ascii                     Use ASCII instead of Unicode"
    echo ""
}

# Check if logxpy-view is available
if ! command -v logxpy-view &> /dev/null; then
    echo -e "${YELLOW}Warning: logxpy-view not found in PATH${NC}"
    echo "Please install logxpy_cli_view:"
    echo "  cd ../logxpy_cli_view && pip install -e ."
    exit 1
fi

# No arguments - show help and list available logs
if [ $# -eq 0 ]; then
    show_help
    echo ""
    echo -e "${BLUE}Available log files:${NC}"
    ls -lh tutorial_*.log 2>/dev/null || echo "No log files found. Run tutorials first."
    exit 0
fi

# Parse arguments
TUTORIAL=$1
shift
VIEWER_OPTS="$@"

# Determine which log file(s) to view
case $TUTORIAL in
    1)
        LOG_FILE="tutorial_01_basic.log"
        DESCRIPTION="Tutorial 01: Basic Logging"
        ;;
    2)
        LOG_FILE="tutorial_02_actions.log"
        DESCRIPTION="Tutorial 02: Actions and Context"
        ;;
    3)
        LOG_FILE="tutorial_03_decorators.log"
        DESCRIPTION="Tutorial 03: Decorators"
        ;;
    4)
        LOG_FILE="tutorial_04_errors.log"
        DESCRIPTION="Tutorial 04: Error Handling"
        ;;
    5)
        LOG_FILE="tutorial_05_api.log"
        DESCRIPTION="Tutorial 05: Real-World API Scenario"
        ;;
    all|*)
        LOG_FILE="tutorial_*.log"
        DESCRIPTION="All Tutorial Logs"
        ;;
esac

# Check if log file exists
if ! ls $LOG_FILE 1> /dev/null 2>&1; then
    echo -e "${YELLOW}Log file(s) not found: $LOG_FILE${NC}"
    echo "Run the tutorial script(s) first:"
    echo "  python run_all_tutorials.py"
    echo "Or run individual tutorial:"
    echo "  python tutorial_0${TUTORIAL}_*.py"
    exit 1
fi

# Display header
echo -e "${GREEN}Viewing: $DESCRIPTION${NC}"
echo -e "${BLUE}Command: logxpy-view $VIEWER_OPTS $LOG_FILE${NC}"
echo ""

# Run the viewer
logxpy-view $VIEWER_OPTS $LOG_FILE
