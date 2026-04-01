@echo off
title AI For Education - Stop Servers
echo Stopping AI For Education servers...
echo.

:: Kill Python/Uvicorn backend
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend*" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo [OK] Backend stopped (port 8000)

:: Kill Node/Vite frontend
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo [OK] Frontend stopped (port 5173)

echo.
echo All servers stopped.
pause
