@echo off
echo Stopping Portable SysAdmin Toolkit...
taskkill /F /IM llama-server.exe >nul 2>&1
echo Done.
echo.
timeout /t 3 >nul 2>&1 || pause
