"""
Task Scheduler - Silver Tier Skill

Helper script to set up scheduled tasks for AI Employee.

Usage:
    python task_scheduler.py <vault_path> --setup
    python task_scheduler.py <vault_path> --list
    python task_scheduler.py <vault_path> --remove

Example:
    python task_scheduler.py ../AI_Employee_Vault --setup
"""

import sys
import os
import logging
import subprocess
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TaskScheduler')


class TaskScheduler:
    """
    Manages scheduled tasks for AI Employee.
    """
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.python_exe = sys.executable
        self.is_windows = os.name == 'nt'
        
        # Task definitions
        self.tasks = [
            {
                'name': 'AI_Employee_Process',
                'script': 'watchers/orchestrator.py',
                'schedule': 'hourly',
                'description': 'Process pending tasks every hour'
            },
            {
                'name': 'AI_Employee_Briefing',
                'script': 'watchers/daily_briefing.py',
                'schedule': 'daily_8am',
                'description': 'Generate daily briefing at 8 AM'
            },
            {
                'name': 'AI_Employee_Weekly_Audit',
                'script': 'watchers/weekly_audit.py',
                'schedule': 'weekly_monday_9am',
                'description': 'Weekly business audit on Monday 9 AM'
            },
            {
                'name': 'AI_Employee_Cleanup',
                'script': 'watchers/approval_workflow.py',
                'schedule': 'daily_midnight',
                'description': 'Cleanup expired approvals at midnight'
            }
        ]
    
    def setup(self) -> bool:
        """Set up all scheduled tasks."""
        if self.is_windows:
            return self._setup_windows()
        else:
            return self._setup_linux()
    
    def _setup_windows(self) -> bool:
        """Set up tasks using Windows Task Scheduler."""
        logger.info('Setting up Windows Task Scheduler tasks...')
        
        vault_str = str(self.vault_path.absolute())
        python_str = self.python_exe
        
        for task in self.tasks:
            script_path = self.vault_path / task['script']
            if not script_path.exists():
                logger.warning(f"Script not found: {script_path}, skipping {task['name']}")
                continue
            
            cmd = self._get_windows_command(task, vault_str, python_str, script_path)
            
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    logger.info(f"✓ Created task: {task['name']}")
                else:
                    logger.error(f"Failed to create {task['name']}: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Error creating {task['name']}: {e}")
        
        return True
    
    def _get_windows_command(self, task: dict, vault: str, python: str, script: Path) -> str:
        """Get Windows schtasks command."""
        schedule_map = {
            'hourly': '/sc minute /mo 60',
            'daily_8am': '/sc daily /st 08:00',
            'weekly_monday_9am': '/sc weekly /d MON /st 09:00',
            'daily_midnight': '/sc daily /st 00:00'
        }
        
        schedule = schedule_map.get(task['schedule'], '/sc once')
        
        return (
            f'schtasks /create /tn "{task["name"]}" '
            f'/tr "{python} {script} {vault}" '
            f'{schedule} '
            f'/ru SYSTEM /f'
        )
    
    def _setup_linux(self) -> bool:
        """Set up tasks using cron."""
        logger.info('Setting up cron jobs...')
        
        vault_str = str(self.vault_path.absolute())
        python_str = self.python_exe
        
        # Get current crontab
        try:
            result = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True
            )
            current_cron = result.stdout if result.returncode == 0 else ''
        except Exception:
            current_cron = ''
        
        # Build new crontab
        cron_lines = [line for line in current_cron.split('\n') 
                      if line and not line.startswith('# AI Employee')]
        
        cron_lines.append('')
        cron_lines.append('# AI Employee - Auto-generated scheduled tasks')
        
        schedule_map = {
            'hourly': '0 * * * *',
            'daily_8am': '0 8 * * *',
            'weekly_monday_9am': '0 9 * * 1',
            'daily_midnight': '0 0 * * *'
        }
        
        for task in self.tasks:
            script_path = self.vault_path / task['script']
            if not script_path.exists():
                continue
            
            schedule = schedule_map.get(task['schedule'], '')
            if schedule:
                cron_line = f"{schedule} {python_str} {script_path} {vault_str}"
                cron_lines.append(cron_line)
        
        # Write new crontab
        new_cron = '\n'.join(cron_lines)
        
        try:
            # Write to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(new_cron)
                temp_file = f.name
            
            # Install crontab
            subprocess.run(['crontab', temp_file], check=True)
            
            # Clean up
            os.unlink(temp_file)
            
            logger.info('✓ Cron jobs installed')
            return True
            
        except Exception as e:
            logger.error(f'Error setting up cron: {e}')
            return False
    
    def list_tasks(self) -> list:
        """List all scheduled tasks."""
        if self.is_windows:
            return self._list_windows()
        else:
            return self._list_linux()
    
    def _list_windows(self) -> list:
        """List Windows scheduled tasks."""
        try:
            result = subprocess.run(
                'schtasks /query /tn "AI_Employee_*" /fo table',
                shell=True,
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception as e:
            return f'Error: {e}'
    
    def _list_linux(self) -> str:
        """List Linux cron jobs."""
        try:
            result = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True
            )
            # Filter AI Employee jobs
            lines = result.stdout.split('\n')
            ai_lines = [l for l in lines if 'AI_Employee' in l or 'orchestrator' in l]
            return '\n'.join(ai_lines) if ai_lines else 'No AI Employee cron jobs found'
        except Exception as e:
            return f'Error: {e}'
    
    def remove(self) -> bool:
        """Remove all scheduled tasks."""
        if self.is_windows:
            return self._remove_windows()
        else:
            return self._remove_linux()
    
    def _remove_windows(self) -> bool:
        """Remove Windows scheduled tasks."""
        logger.info('Removing Windows scheduled tasks...')
        
        for task in self.tasks:
            cmd = f'schtasks /delete /tn "{task["name"]}" /f'
            try:
                subprocess.run(cmd, shell=True, check=True)
                logger.info(f"✓ Removed task: {task['name']}")
            except Exception as e:
                logger.warning(f"Could not remove {task['name']}: {e}")
        
        return True
    
    def _remove_linux(self) -> bool:
        """Remove Linux cron jobs."""
        logger.info('Removing AI Employee cron jobs...')
        
        try:
            result = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True
            )
            lines = result.stdout.split('\n')
            
            # Filter out AI Employee jobs
            new_lines = [l for l in lines 
                        if 'AI_Employee' not in l 
                        and 'orchestrator' not in l
                        and 'daily_briefing' not in l
                        and 'weekly_audit' not in l
                        and 'approval_workflow' not in l]
            
            # Also remove the header comment
            new_lines = [l for l in new_lines 
                        if '# AI Employee' not in l]
            
            # Write new crontab
            if new_lines and new_lines[-1] != '':
                new_lines.append('')
            
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write('\n'.join(new_lines))
                temp_file = f.name
            
            subprocess.run(['crontab', temp_file], check=True)
            os.unlink(temp_file)
            
            logger.info('✓ Removed AI Employee cron jobs')
            return True
            
        except Exception as e:
            logger.error(f'Error removing cron jobs: {e}')
            return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python task_scheduler.py <vault_path> [options]")
        print("\nOptions:")
        print("  --setup     Set up scheduled tasks")
        print("  --list      List scheduled tasks")
        print("  --remove    Remove scheduled tasks")
        print("\nExamples:")
        print("  python task_scheduler.py ../AI_Employee_Vault --setup")
        print("  python task_scheduler.py ../AI_Employee_Vault --list")
        print("  python task_scheduler.py ../AI_Employee_Vault --remove")
        sys.exit(1)
    
    vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        logger.error(f'Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    scheduler = TaskScheduler(vault_path)
    
    if '--setup' in sys.argv:
        scheduler.setup()
        print("\n✅ Scheduled tasks set up!")
        
    elif '--list' in sys.argv:
        tasks = scheduler.list_tasks()
        print(f"\n📅 Scheduled Tasks:\n")
        print(tasks)
        
    elif '--remove' in sys.argv:
        scheduler.remove()
        print("\n✅ Scheduled tasks removed!")


if __name__ == '__main__':
    main()
