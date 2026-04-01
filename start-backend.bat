@echo off
title AI For Education - Backend
cd /d "%~dp0backend"
call venv\Scripts\activate
python main.py
pause
