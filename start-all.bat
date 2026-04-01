@echo off
title AI For Education - Launcher
echo Starting AI For Education...
echo.
echo Starting Backend...
start "Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && python main.py"
timeout /t 5 /nobreak >nul
echo Starting Frontend...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
echo.
echo Both servers launched!
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo.
pause
