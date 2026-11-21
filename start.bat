@echo off
title PlantGuard AI Web Platform
cd /d "%~dp0"
echo Starting PlantGuard AI Platform...
call .venv\Scripts\python.exe run_app.py
pause
