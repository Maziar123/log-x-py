#!/bin/bash
# Capture logxpy-view output as HTML and PNG screenshot
# Usage: ./capture.sh [oneline|tree]

cd "$(dirname "$0")"
uv run python capture.py "$@"
