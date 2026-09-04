@echo off
REM AI Employee - Full Automation Starter
REM This starts both the File Watcher and Orchestrator for fully automatic processing

echo.
echo =============================================
echo    AI Employee - Full Automation Mode
echo =============================================
echo.
echo This will:
echo   1. Monitor DropFolder for new files
echo   2. Automatically process files with Qwen Code
echo   3. Auto-approve low-risk tasks
echo   4. Flag high-risk tasks for approval
echo   5. Update Dashboard automatically
echo   6. Move completed tasks to Done/
echo.
echo Drop files into DropFolder/ to begin.
echo Press Ctrl+C to stop.
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.12+
    pause
    exit /b 1
)

REM Check if Qwen Code is available
qwen --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Qwen Code not found. Install with: pip install qwen-code
    echo Processing will be limited.
    echo.
)

REM Start the full automation
echo Starting AI Employee Orchestrator...
echo.

python watchers\orchestrator.py . 15

pause
