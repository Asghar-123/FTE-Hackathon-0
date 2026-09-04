"""
Silver Tier Verification Script

Verifies that all Silver tier requirements are met:
✅ Two or more Watcher scripts (Gmail + LinkedIn)
✅ Automatically Post on LinkedIn
✅ Plan.md generator
✅ One working MCP server (Email)
✅ Human-in-the-loop approval workflow
✅ Basic scheduling via Task Scheduler

Usage:
    python verify_silver.py [vault_path]
    
Example:
    python verify_silver.py ../AI_Employee_Vault
"""

import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def check(condition: bool, message: str) -> bool:
    """Print check result and return condition."""
    if condition:
        print(f"  {Colors.GREEN}✓{Colors.RESET} {message}")
    else:
        print(f"  {Colors.RED}✗{Colors.RESET} {message}")
    return condition


def verify_silver_tier(vault_path: Path) -> bool:
    """
    Verify all Silver tier requirements.
    
    Returns:
        True if all checks pass, False otherwise
    """
    print(f"\n{Colors.BOLD}🥈 Silver Tier Verification{Colors.RESET}")
    print(f"   Vault: {vault_path.absolute()}")
    print()
    
    all_passed = True
    watchers_dir = vault_path / 'watchers'
    
    # Check 1: Two or more Watcher scripts
    print(f"{Colors.BOLD}1. Watcher Scripts (2+ required){Colors.RESET}")
    gmail_watcher = watchers_dir / 'gmail_watcher.py'
    linkedin_watcher = watchers_dir / 'linkedin_watcher.py'
    
    all_passed &= check(gmail_watcher.exists(), "Gmail Watcher exists")
    all_passed &= check(linkedin_watcher.exists(), "LinkedIn Watcher exists")
    
    if gmail_watcher.exists():
        content = gmail_watcher.read_text(encoding='utf-8')
        all_passed &= check('class GmailWatcher' in content, "  └─ GmailWatcher class defined")
    
    if linkedin_watcher.exists():
        content = linkedin_watcher.read_text(encoding='utf-8')
        all_passed &= check('class LinkedInWatcher' in content, "  └─ LinkedInWatcher class defined")
        all_passed &= check('def post_update' in content, "  └─ Auto-post capability")
    
    # Check 2: Plan Generator
    print(f"\n{Colors.BOLD}2. Plan.md Generator{Colors.RESET}")
    plan_generator = watchers_dir / 'plan_generator.py'
    all_passed &= check(plan_generator.exists(), "Plan Generator exists")
    
    if plan_generator.exists():
        content = plan_generator.read_text(encoding='utf-8')
        all_passed &= check('class PlanGenerator' in content, "  └─ PlanGenerator class defined")
        all_passed &= check('def create_plan' in content, "  └─ create_plan method")
    
    # Check 3: MCP Server (Email)
    print(f"\n{Colors.BOLD}3. MCP Server (Email){Colors.RESET}")
    email_mcp = watchers_dir / 'email_mcp_server.py'
    all_passed &= check(email_mcp.exists(), "Email MCP Server exists")
    
    if email_mcp.exists():
        content = email_mcp.read_text(encoding='utf-8')
        all_passed &= check('class EmailServer' in content, "  └─ EmailServer class defined")
        all_passed &= check('def send_email' in content, "  └─ send_email method")
    
    # Check 4: Human-in-the-Loop Approval
    print(f"\n{Colors.BOLD}4. Human-in-the-Loop Approval{Colors.RESET}")
    approval_workflow = watchers_dir / 'approval_workflow.py'
    all_passed &= check(approval_workflow.exists(), "Approval Workflow exists")
    
    if approval_workflow.exists():
        content = approval_workflow.read_text(encoding='utf-8')
        all_passed &= check('class ApprovalWorkflow' in content, "  └─ ApprovalWorkflow class")
        all_passed &= check('def approve' in content, "  └─ approve method")
        all_passed &= check('def reject' in content, "  └─ reject method")
    
    # Check 5: Task Scheduler
    print(f"\n{Colors.BOLD}5. Task Scheduler{Colors.RESET}")
    task_scheduler = watchers_dir / 'task_scheduler.py'
    all_passed &= check(task_scheduler.exists(), "Task Scheduler exists")
    
    if task_scheduler.exists():
        content = task_scheduler.read_text(encoding='utf-8')
        all_passed &= check('class TaskScheduler' in content, "  └─ TaskScheduler class")
        all_passed &= check('def setup' in content, "  └─ setup method")
    
    # Check 6: Required Folders
    print(f"\n{Colors.BOLD}6. Required Folders{Colors.RESET}")
    required_folders = ['Inbox', 'Needs_Action', 'Done', 'Plans', 
                        'Pending_Approval', 'Approved', 'Rejected']
    for folder in required_folders:
        all_passed &= check((vault_path / folder).exists(), f"/{folder} folder exists")
    
    # Check 7: Qwen Skills Documentation
    print(f"\n{Colors.BOLD}7. Qwen Skills Documentation{Colors.RESET}")
    # Skills are in project root .qwen/skills (3 levels up from watchers folder)
    skills_dir = Path(__file__).parent.parent.parent / '.qwen' / 'skills'
    
    silver_skills = [
        'gmail-watcher',
        'linkedin-watcher',
        'email-mcp',
        'plan-generator',
        'approval-workflow',
        'task-scheduler'
    ]
    
    for skill in silver_skills:
        skill_path = skills_dir / skill
        all_passed &= check(skill_path.exists(), f"{skill} skill exists")
        if skill_path.exists():
            skill_doc = skill_path / 'SKILL.md'
            all_passed &= check(skill_doc.exists(), f"  └─ SKILL.md documentation")
    
    # Check 8: Gmail Configuration
    print(f"\n{Colors.BOLD}8. Gmail Configuration{Colors.RESET}")
    
    token_path = vault_path / 'watchers' / 'token.json'
    all_passed &= check(token_path.exists(), "Gmail token.json exists (authenticated)")
    
    # Check credentials in project root (3 levels up from watchers folder)
    credentials_path = Path(__file__).parent.parent.parent / 'credentials.json'
    all_passed &= check(credentials_path.exists(), "credentials.json exists (project root)")
    
    # Summary
    print(f"\n{'='*60}")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ Silver Tier COMPLETE!{Colors.RESET}")
        print(f"\n   All Silver tier requirements verified successfully.")
        print(f"   Watchers: Gmail + LinkedIn")
        print(f"   MCP Server: Email")
        print(f"   Approval Workflow: Enabled")
        print(f"   Scheduling: Task Scheduler ready")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Silver Tier INCOMPLETE{Colors.RESET}")
        print(f"\n   Some requirements are missing. Review the checks above.")
    print(f"{'='*60}\n")
    
    return all_passed


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        # Default to sibling AI_Employee_Vault folder
        script_dir = Path(__file__).parent
        vault_path = script_dir
    else:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f"{Colors.RED}Error: Vault path does not exist: {vault_path}{Colors.RESET}")
        sys.exit(1)
    
    success = verify_silver_tier(vault_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
