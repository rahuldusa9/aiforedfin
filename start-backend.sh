#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SCRIPT_DIR/backend"
/usr/local/bin/python3 -m uvicorn main:app --reload --port 8000
