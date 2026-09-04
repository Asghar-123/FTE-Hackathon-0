@echo off
REM AI Employee - Gold Tier Automation Starter
REM Starts all watchers including Odoo, Facebook, and Twitter

echo.
echo =============================================
echo    AI Employee - GOLD TIER Automation
echo =============================================
echo.

cd /d "%~dp0"

REM 1. Odoo Integration
echo Starting Odoo Integration...
echo Ensure 'docker-compose up -d' is run in odoo-setup/

REM 2. Social Media Watchers
echo Starting Facebook Watcher...
start /b python watchers\facebook_watcher.py .

echo Starting Twitter (X) Watcher...
start /b python watchers\twitter_watcher.py .

REM 3. Business Audit (Run once at startup)
echo Generating Weekly Business Audit...
python watchers\ceo_audit.py .

REM 4. Comms Watchers (WhatsApp disabled by user)
echo Starting Comms Watchers...
start /b python watchers\gmail_watcher.py .
start /b python watchers\linkedin_watcher.py .
start /b python watchers\filesystem_watcher.py . DropFolder 30

echo Starting Orchestrator...
python watchers\orchestrator.py . 15

pause
