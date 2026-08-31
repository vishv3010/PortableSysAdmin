@echo off
setlocal
echo ====================================================
echo         PORTABLE SYSADMIN TOOLKIT LAUNCHER
echo ====================================================

:: Determine the directory where START.bat is located
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please ensure Python is available or run from the portable USB build.
    pause
    exit /b 1
)

:: Launch the main application
echo [INFO] Starting Toolkit...
python app\main.py
pause
