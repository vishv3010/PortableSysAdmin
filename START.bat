@echo off
setlocal
echo ====================================================
echo         PORTABLE SYSADMIN TOOLKIT LAUNCHER
echo ====================================================

:: Determine the directory where START.bat is located
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"
set "PYTHONPATH=%PROJECT_ROOT%;%PROJECT_ROOT%app;%PYTHONPATH%"

:: Ensure bundled Portable Python ._pth file includes app directory if present
if exist "%PROJECT_ROOT%python_portable\python311._pth" (
    findstr /x /c:"..\app" "%PROJECT_ROOT%python_portable\python311._pth" >nul 2>&1
    if errorlevel 1 (
        echo ..>> "%PROJECT_ROOT%python_portable\python311._pth"
        echo ..\app>> "%PROJECT_ROOT%python_portable\python311._pth"
    )
)

:: Offline AI Server will run on-demand only when requested (0% CPU at startup)
echo [INFO] Offline AI ready on-demand (0% CPU background footprint at startup).

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
