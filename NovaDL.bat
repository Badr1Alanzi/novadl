@echo off
title NovaDL
python "%~dp0run.py"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] NovaDL failed to start. Make sure Python 3.8+ is installed.
    pause
)
