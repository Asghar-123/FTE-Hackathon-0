---
name: task-scheduler
description: |
  Schedule recurring tasks using cron (Linux/Mac) or Task Scheduler (Windows).
  Automates periodic operations like daily briefings, weekly audits, and 
  regular folder processing.
---

# Task Scheduler

Schedule recurring AI Employee tasks using system schedulers.

## Supported Schedulers

| Platform | Scheduler | Command |
|----------|-----------|---------|
| Windows | Task Scheduler | `schtasks` |
| Linux | cron | `crontab` |
| Mac | cron/launchd | `crontab` |

## Usage

### Windows - Task Scheduler

#### Create Scheduled Task

```batch
# Daily briefing at 8 AM
schtasks /create /tn "AI_Employee_Daily_Briefing" ^
  /tr "python C:\path\to\orchestrator.py C:\path\to\vault" ^
  /sc daily /st 08:00 ^
  /ru SYSTEM

# Hourly folder processing
schtasks /create /tn "AI_Employee_Process" ^
  /tr "python C:\path\to\orchestrator.py C:\path\to\vault" ^
  /sc minute /mo 60 ^
  /ru SYSTEM
```

#### View Scheduled Tasks

```batch
schtasks /query /tn "AI_Employee_*"
```

#### Delete Task

```batch
schtasks /delete /tn "AI_Employee_Daily_Briefing" /f
```

### Linux/Mac - cron

#### Edit Crontab

```bash
crontab -e
```

#### Add Scheduled Jobs

```bash
# Daily briefing at 8 AM
0 8 * * * cd /path/to/vault && python orchestrator.py .

# Hourly processing
0 * * * * cd /path/to/vault && python orchestrator.py .

# Weekly audit every Monday at 9 AM
0 9 * * 1 cd /path/to/vault && python weekly_audit.py .

# Cleanup expired approvals daily at midnight
0 0 * * * cd /path/to/vault && python approval_workflow.py . --cleanup
```

#### View Crontab

```bash
crontab -l
```

#### Remove All Jobs

```bash
crontab -r
```

## Predefined Schedules

### Daily Briefing (8 AM)

Generates morning summary with:
- Pending tasks count
- Yesterday's completions
- Today's priorities

```bash
# Windows
schtasks /create /tn "AI_Employee_Briefing" ^
  /tr "python C:\vault\watchers\daily_briefing.py C:\vault" ^
  /sc daily /st 08:00

# Linux/Mac
0 8 * * * python /vault/watchers/daily_briefing.py /vault
```

### Hourly Processing

Checks for new files and processes them:

```bash
# Windows
schtasks /create /tn "AI_Employee_Process" ^
  /tr "python C:\vault\watchers\orchestrator.py C:\vault" ^
  /sc minute /mo 60

# Linux/Mac
0 * * * * python /vault/watchers/orchestrator.py /vault
```

### Weekly Audit (Monday 9 AM)

Full weekly review with:
- Revenue summary
- Task completion rate
- Bottleneck analysis

```bash
# Windows
schtasks /create /tn "AI_Employee_Weekly" ^
  /tr "python C:\vault\watchers\weekly_audit.py C:\vault" ^
  /sc weekly /d MON /st 09:00

# Linux/Mac
0 9 * * 1 python /vault/watchers/weekly_audit.py /vault
```

## Python Scheduling (Alternative)

For simple scheduling without system scheduler:

```python
# scheduled_runner.py
import schedule
import time
from orchestrator import AIEmployeeOrchestrator
from pathlib import Path

vault = Path('../AI_Employee_Vault')
orchestrator = AIEmployeeOrchestrator(vault)

# Schedule jobs
schedule.every().hour.do(orchestrator.run_cycle)
schedule.every().day.at("08:00").do(run_daily_briefing)
schedule.every().monday.at("09:00").do(run_weekly_audit)

print("Scheduler started...")
while True:
    schedule.run_pending()
    time.sleep(60)
```

### Install Schedule Library

```bash
pip install schedule
```

### Run Scheduler

```bash
python scheduled_runner.py
```

## Environment Setup

### Windows Service

For always-on operation, run as Windows Service:

1. Install NSSM (Non-Sucking Service Manager)
2. Create service:
```batch
nssm install AI_Employee "C:\Python\python.exe" "C:\vault\watchers\auto_employee.py" "C:\vault"
nssm start AI_Employee
```

### Linux Systemd

Create systemd service:

```ini
# /etc/systemd/system/ai-employee.service
[Unit]
Description=AI Employee Automation
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/vault
ExecStart=/usr/bin/python3 /path/to/vault/watchers/auto_employee.py /path/to/vault
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable ai-employee
sudo systemctl start ai-employee
sudo systemctl status ai-employee
```

## Best Practices

1. **Log Rotation**: Configure log rotation to prevent disk fill
2. **Error Handling**: Ensure scripts handle errors gracefully
3. **Notifications**: Set up email/SMS alerts for failures
4. **Backup**: Backup vault before scheduled operations
5. **Monitoring**: Monitor scheduled task execution

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not running | Check user permissions |
| Python not found | Use full path to python.exe |
| File access denied | Run as appropriate user |
| Task runs but fails | Check script output logs |

## Example: Full Setup

### Windows Complete Setup

```batch
@echo off
REM setup_scheduled_tasks.bat

REM Navigate to vault
cd /d "C:\AI_Employee_Vault"

REM Create daily briefing task
schtasks /create /tn "AI_Employee_Daily_Briefing" ^
  /tr "python C:\AI_Employee_Vault\watchers\daily_briefing.py C:\AI_Employee_Vault" ^
  /sc daily /st 08:00 ^
  /ru SYSTEM ^
  /f

REM Create hourly processing task
schtasks /create /tn "AI_Employee_Process" ^
  /tr "python C:\AI_Employee_Vault\watchers\orchestrator.py C:\AI_Employee_Vault" ^
  /sc minute /mo 60 ^
  /ru SYSTEM ^
  /f

REM Create weekly audit task
schtasks /create /tn "AI_Employee_Weekly_Audit" ^
  /tr "python C:\AI_Employee_Vault\watchers\weekly_audit.py C:\AI_Employee_Vault" ^
  /sc weekly /d MON /st 09:00 ^
  /ru SYSTEM ^
  /f

echo Scheduled tasks created!
schtasks /query /tn "AI_Employee_*"
```

### Linux Complete Setup

```bash
#!/bin/bash
# setup_cron.sh

VAULT_PATH="/home/user/AI_Employee_Vault"
PYTHON_PATH="/usr/bin/python3"

# Create crontab entries
crontab -l > /tmp/mycron 2>/dev/null

# Add AI Employee jobs
echo "0 8 * * * $PYTHON_PATH $VAULT_PATH/watchers/daily_briefing.py $VAULT_PATH" >> /tmp/mycron
echo "0 * * * * $PYTHON_PATH $VAULT_PATH/watchers/orchestrator.py $VAULT_PATH" >> /tmp/mycron
echo "0 9 * * 1 $PYTHON_PATH $VAULT_PATH/watchers/weekly_audit.py $VAULT_PATH" >> /tmp/mycron

# Install new crontab
crontab /tmp/mycron
rm /tmp/mycron

echo "Cron jobs installed!"
crontab -l
```
