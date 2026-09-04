@echo off
REM Quick Start Script for AI Employee File System Watcher
REM Bronze Tier - FTE-Hackathon-0

echo.
echo ========================================
echo   AI Employee - File System Watcher
echo ========================================
echo.

cd /d "%~dp0"

echo Starting watcher...
echo   Vault: %CD%
echo   Monitoring: DropFolder
echo   Interval: 30 seconds
echo.
echo Drop files into the DropFolder to create action items.
echo Press Ctrl+C to stop the watcher.
echo.

python watchers\filesystem_watcher.py . DropFolder 30

pause
