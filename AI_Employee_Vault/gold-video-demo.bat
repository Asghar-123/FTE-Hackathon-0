@echo off
REM AI Employee - Gold Tier Video Demo Script
REM Focuses ONLY on Odoo, Facebook, and Twitter

echo.
echo ===================================================
echo    AI Employee - GOLD TIER VIDEO DEMO
echo ===================================================
echo.

cd /d "%~dp0"

REM 1. Show Odoo Business Audit
echo [1/3] INTEGRATION: Odoo Accounting
echo Generating real-time business audit from Odoo...
python watchers\ceo_audit.py .
echo.

REM 2. Start Facebook
echo [2/3] SOCIAL MEDIA: Facebook
echo Starting Facebook Playwright Watcher...
start "Facebook Watcher" python watchers\facebook_watcher.py .
echo.

REM 3. Start Twitter
echo [3/3] SOCIAL MEDIA: Twitter (X)
echo Starting Twitter Playwright Watcher...
start "Twitter Watcher" python watchers\twitter_watcher.py .
echo.

echo ===================================================
echo   Gold Tier Features are now RUNNING
echo   - Odoo ERP Integrated
echo   - Facebook Automation Active
echo   - Twitter (X) Automation Active
echo ===================================================
echo Press any key to stop the watchers...
pause > nul

taskkill /F /IM python.exe /T
echo Watchers stopped.
pause
