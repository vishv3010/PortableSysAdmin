@echo off
setlocal EnableDelayedExpansion

title Portable SysAdmin Toolkit

echo ====================================================
echo         PORTABLE SYSADMIN TOOLKIT LAUNCHER
echo ====================================================

:: Determine the directory where START.bat is located
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"
set "PYTHONPATH=%PROJECT_ROOT%;%PROJECT_ROOT%app;%PYTHONPATH%"

:: Check for Administrator privileges
set "IS_ADMIN=0"
>nul 2>&1 fltmc.exe && set "IS_ADMIN=1"
if !IS_ADMIN! neq 1 (
    >nul 2>&1 net session && set "IS_ADMIN=1"
)

if !IS_ADMIN! neq 1 (
    echo [INFO] Administrator privileges not detected.
    echo [INFO] Requesting elevated Administrator privileges via Windows UAC...
    
    :: Elevate via cmd.exe through PowerShell RunAs with explicit path handling and error capture
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$p='%~f0'; $d='%~dp0.'; try { Start-Process -FilePath 'cmd.exe' -ArgumentList ('/c cd /d ""' + $d + '"" && ""' + $p + '""') -Verb RunAs -ErrorAction Stop; exit 0 } catch { exit 1 }" >nul 2>&1
    if !errorlevel! equ 0 (
        exit /b 0
    )
    
    echo [WARNING] Administrator elevation was declined or unavailable.
    echo [WARNING] Running with standard user privileges.
    echo [WARNING] Note: Hardware repairs and system remediation will require Administrator rights.
    echo.
)

:: Ensure bundled Portable Python ._pth file includes project root and app directory if present
if exist "%PROJECT_ROOT%python_portable\python311._pth" (
    findstr /x /c:"..\app" "%PROJECT_ROOT%python_portable\python311._pth" >nul 2>&1
    if errorlevel 1 (
        echo ..>> "%PROJECT_ROOT%python_portable\python311._pth" 2>nul
        echo ..\app>> "%PROJECT_ROOT%python_portable\python311._pth" 2>nul
    )
)

:: Offline AI Server ready on demand
echo [INFO] Offline AI ready on-demand (0%% CPU background footprint at startup).

:: Detect Python executable
set "PYTHON_EXE="

:: 1. Bundled portable python in project root
if exist "%PROJECT_ROOT%python_portable\python.exe" (
    set PYTHON_EXE="%PROJECT_ROOT%python_portable\python.exe"
    echo [INFO] Using bundled Portable Python.
)

:: 2. Bundled portable python in release directory
if not defined PYTHON_EXE (
    if exist "%PROJECT_ROOT%release\PortableSysAdmin\python_portable\python.exe" (
        set PYTHON_EXE="%PROJECT_ROOT%release\PortableSysAdmin\python_portable\python.exe"
        echo [INFO] Using bundled Portable Python from release folder.
    )
)

:: 3. Test system python (avoiding Windows Store 0-byte execution alias)
if not defined PYTHON_EXE (
    python -c "import sys; sys.exit(0)" >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_EXE=python
        echo [INFO] Using system Python.
    )
)

:: 4. Test Windows Python Launcher (py -3)
if not defined PYTHON_EXE (
    py -3 -c "import sys; sys.exit(0)" >nul 2>&1
    if !errorlevel! equ 0 (
        set PYTHON_EXE=py -3
        echo [INFO] Using Windows Python Launcher (py -3).
    )
)

:: 5. If Python is still missing, attempt automatic bootstrap
if not defined PYTHON_EXE (
    echo [INFO] Python runtime not detected.
    echo [INFO] Attempting to auto-download Portable Python for USB (21MB)...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $zip = Join-Path $env:TEMP 'python311.zip'; $dest = Join-Path '%PROJECT_ROOT%' 'python_portable'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-embed-amd64.zip' -OutFile $zip; Expand-Archive -Path $zip -DestinationPath $dest -Force; Remove-Item $zip -Force; Set-Content -Path (Join-Path $dest 'python311._pth') -Value ('python311.zip' + [Environment]::NewLine + '.' + [Environment]::NewLine + '..' + [Environment]::NewLine + '..\app' + [Environment]::NewLine + 'import site')" >nul 2>&1
    if exist "%PROJECT_ROOT%python_portable\python.exe" (
        set PYTHON_EXE="%PROJECT_ROOT%python_portable\python.exe"
        echo [INFO] Portable Python bootstrapped successfully!
    )
)

:: Check if Python was found
if not defined PYTHON_EXE (
    echo.
    echo ====================================================
    echo [ERROR] Python is not installed or not in PATH, and portable python is missing.
    echo.
    echo To fix this:
    echo 1. Ensure the 'python_portable' folder is present on the pendrive alongside START.bat
    echo 2. Or connect to the internet once to permit automatic bootstrapping
    echo 3. Or install Python 3.8+ on Windows and check 'Add python.exe to PATH'
    echo ====================================================
    echo.
    pause
    exit /b 1
)

:: Launch the main application
echo [INFO] Starting Toolkit UI...
%PYTHON_EXE% "%PROJECT_ROOT%app\main.py"
set "APP_EXIT_CODE=%errorlevel%"

if %APP_EXIT_CODE% neq 0 (
    echo.
    echo [WARNING] Toolkit exited with return code %APP_EXIT_CODE%.
    echo If this was unexpected, please review logs in:
    echo   %PROJECT_ROOT%logs
    echo.
)

:: Cleanup AI Server when UI closes
echo [INFO] Shutting down AI Server...
taskkill /F /IM llama-server.exe >nul 2>&1
echo [INFO] Goodbye!
pause
