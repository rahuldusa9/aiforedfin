#!/bin/bash
echo "Stopping AI For Education servers..."
echo ""

# Kill backend on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null
echo "[OK] Backend stopped (port 8000)"

# Kill frontend on port 5173
lsof -ti:5173 | xargs kill -9 2>/dev/null
echo "[OK] Frontend stopped (port 5173)"

echo ""
echo "All servers stopped."
