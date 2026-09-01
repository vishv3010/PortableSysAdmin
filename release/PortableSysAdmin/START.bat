@echo off
setlocal
echo ====================================================
echo         PORTABLE SYSADMIN TOOLKIT LAUNCHER
echo ====================================================

:: Determine the directory where START.bat is located
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: Start the AI Server in the background if it exists
if exist "%PROJECT_ROOT%bin\llama-server.exe" (
    echo [INFO] Booting offline AI Brain in the background (Optimized for CPU)...
    start "Local AI Server" /B /MIN "%PROJECT_ROOT%bin\llama-server.exe" -m "%PROJECT_ROOT%models\model.gguf" --port 8080 -t 4 -c 2048 -b 512 >nul 2>&1
    :: Wait 3 seconds for server to spin up
    timeout /t 3 /nobreak >nul
) else (
    echo [WARNING] Local AI Server not found in bin\. AI analysis will fallback to mocked logic.
)

:: Check for bundled Portable Python first
set "PYTHON_EXE=python"
if exist "%PROJECT_ROOT%python_portable\python.exe" (
    echo [INFO] Using bundled Portable Python.
    set "PYTHON_EXE=%PROJECT_ROOT%python_portable\python.exe"
) else (
    :: Fallback to system Python
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed or not in PATH, and portable python is missing.
        echo Please ensure Python is available or run from the full portable USB build.
        pause
        exit /b 1
    )
)

:: Launch the main application
echo [INFO] Starting Toolkit UI...
"%PYTHON_EXE%" app\main.py

:: Cleanup AI Server when UI closes
echo [INFO] Shutting down AI Server...
taskkill /F /IM llama-server.exe >nul 2>&1
echo [INFO] Goodbye!
pause
