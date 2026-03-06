@echo off
title Scoutbot UI Launcher
echo [1/3] Checking Virtual Environment...

:: Check if venv exists
if not exist "venv\" (
    echo [ERROR] Virtual environment 'venv' not found!
    echo Please run setup_scoutbot.bat first.
    pause
    exit
)

echo [2/3] Activating Environment...
call venv\Scripts\activate

echo [3/3] Starting Scoutbot UI...
:: Replace 'scoutbot_main.py' with your actual filename
python scoutbot_main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application crashed or failed to start.
    pause
)

deactivate