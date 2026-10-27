# Portable SysAdmin Windows Installer (PowerShell)
# Requires Administrator privileges
# Run: powershell -ExecutionPolicy Bypass -File install.ps1

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   PORTABLE SYSADMIN TOOLKIT - WINDOWS INSTALLER    " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# Check Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[!] Administrator privileges recommended for complete setup." -ForegroundColor Yellow
}

$InstallDir = "$env:ProgramFiles\PortableSysAdmin"
if (-not $isAdmin) {
    $InstallDir = "$env:LOCALAPPDATA\PortableSysAdmin"
}

$SourceDir = $PSScriptRoot
if (-not $SourceDir) {
    $SourceDir = Get-Location
}

Write-Host "[+] Installing to $InstallDir..." -ForegroundColor Green
if (-not (Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}

# Copy files
Copy-Item -Path "$SourceDir\app" -Destination "$InstallDir\" -Recurse -Force
Copy-Item -Path "$SourceDir\config" -Destination "$InstallDir\" -Recurse -Force
Copy-Item -Path "$SourceDir\knowledge" -Destination "$InstallDir\" -Recurse -Force
Copy-Item -Path "$SourceDir\scripts" -Destination "$InstallDir\" -Recurse -Force
if (Test-Path "$SourceDir\tools") {
    Copy-Item -Path "$SourceDir\tools" -Destination "$InstallDir\" -Recurse -Force
}
if (Test-Path "$SourceDir\python_portable") {
    Copy-Item -Path "$SourceDir\python_portable" -Destination "$InstallDir\" -Recurse -Force
}
if (Test-Path "$SourceDir\bin") {
    Copy-Item -Path "$SourceDir\bin" -Destination "$InstallDir\" -Recurse -Force
}
if (Test-Path "$SourceDir\models") {
    Copy-Item -Path "$SourceDir\models" -Destination "$InstallDir\" -Recurse -Force
}
if (Test-Path "$SourceDir\POCKET_REFERENCE.html") {
    Copy-Item -Path "$SourceDir\POCKET_REFERENCE.html" -Destination "$InstallDir\" -Force
}
if (Test-Path "$SourceDir\START.bat") {
    Copy-Item -Path "$SourceDir\START.bat" -Destination "$InstallDir\" -Force
}

# Ensure logs dir
New-Item -ItemType Directory -Path "$InstallDir\logs" -Force | Out-Null

# Create command wrapper portablesysadmin.cmd in System or User PATH
$CmdPath = "$InstallDir\portablesysadmin.cmd"
@"
@echo off
setlocal
cd /d "$InstallDir"
set "PYTHONPATH=$InstallDir;$InstallDir\app;%PYTHONPATH%"
if exist "$InstallDir\python_portable\python.exe" (
    "$InstallDir\python_portable\python.exe" "$InstallDir\app\main.py" %*
) else (
    python "$InstallDir\app\main.py" %*
)
"@ | Set-Content -Path $CmdPath -Encoding ASCII

# Add to PATH
$CurrentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
if ($isAdmin -and ($CurrentPath -notlike "*$InstallDir*")) {
    [Environment]::SetEnvironmentVariable("PATH", "$CurrentPath;$InstallDir", "Machine")
    Write-Host "[+] Added $InstallDir to System PATH." -ForegroundColor Green
} elseif (-not $isAdmin) {
    $UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($UserPath -notlike "*$InstallDir*") {
        [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$InstallDir", "User")
        Write-Host "[+] Added $InstallDir to User PATH." -ForegroundColor Green
    }
}

# Create Desktop Shortcut
$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\Portable SysAdmin.lnk")
$Shortcut.TargetPath = "$InstallDir\START.bat"
$Shortcut.WorkingDirectory = "$InstallDir"
$Shortcut.Description = "Portable SysAdmin Diagnostic & Optimization Toolkit"
$Shortcut.Save()

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   INSTALLATION SUCCESSFUL!                         " -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "You can now run the tool anywhere in CMD or PowerShell by typing:"
Write-Host "  portablesysadmin" -ForegroundColor Yellow
Write-Host "Or double-click the shortcut on your Desktop."
Write-Host "====================================================" -ForegroundColor Cyan
