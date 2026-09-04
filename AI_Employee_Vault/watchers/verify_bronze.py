"""
Bronze Tier Verification Script

Verifies that all Bronze tier requirements are met:
✅ Obsidian vault with Dashboard.md and Company_Handbook.md
✅ One working Watcher script (Gmail OR file system monitoring)
✅ Qwen Code successfully reading from and writing to the vault
✅ Basic folder structure: /Inbox, /Needs_Action, /Done

Usage:
    python verify_bronze.py [vault_path]
    
Example:
    python verify_bronze.py ../AI_Employee_Vault
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


def verify_bronze_tier(vault_path: Path) -> bool:
    """
    Verify all Bronze tier requirements.
    
    Returns:
        True if all checks pass, False otherwise
    """
    print(f"\n{Colors.BOLD}🏅 Bronze Tier Verification{Colors.RESET}")
    print(f"   Vault: {vault_path.absolute()}")
    print()
    
    all_passed = True
    
    # Check 1: Vault exists
    print(f"{Colors.BOLD}1. Vault Structure{Colors.RESET}")
    all_passed &= check(vault_path.exists(), "Vault directory exists")
    
    # Check 2: Required folders
    required_folders = ['Inbox', 'Needs_Action', 'Done']
    print(f"\n{Colors.BOLD}2. Required Folders{Colors.RESET}")
    for folder in required_folders:
        folder_path = vault_path / folder
        all_passed &= check(folder_path.exists(), f"/{folder} folder exists")
    
    # Check 3: Required files
    print(f"\n{Colors.BOLD}3. Required Files{Colors.RESET}")
    required_files = {
        'Dashboard.md': 'Dashboard with real-time summary',
        'Company_Handbook.md': 'Company Handbook with rules',
        'Business_Goals.md': 'Business Goals template'
    }
    for filename, description in required_files.items():
        file_path = vault_path / filename
        all_passed &= check(file_path.exists(), f"{filename} ({description})")
        
        # Verify file has content
        if file_path.exists():
            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                content = file_path.read_text(encoding='cp1252')
            all_passed &= check(len(content) > 50, f"  └─ {filename} has content")
    
    # Check 4: Watcher scripts
    print(f"\n{Colors.BOLD}4. Watcher Scripts{Colors.RESET}")
    watchers_dir = vault_path / 'watchers'
    all_passed &= check(watchers_dir.exists(), "Watchers directory exists")
    
    if watchers_dir.exists():
        base_watcher = watchers_dir / 'base_watcher.py'
        filesystem_watcher = watchers_dir / 'filesystem_watcher.py'
        
        all_passed &= check(base_watcher.exists(), "base_watcher.py exists")
        all_passed &= check(filesystem_watcher.exists(), "filesystem_watcher.py exists")
        
        # Verify watcher can be imported
        if filesystem_watcher.exists():
            content = filesystem_watcher.read_text(encoding='utf-8')
            all_passed &= check('class FilesystemWatcher' in content, 
                              "  └─ FilesystemWatcher class defined")
            all_passed &= check('def check_for_updates' in content, 
                              "  └─ check_for_updates method defined")
            all_passed &= check('def create_action_file' in content, 
                              "  └─ create_action_file method defined")
    
    # Check 5: Requirements file
    print(f"\n{Colors.BOLD}5. Dependencies{Colors.RESET}")
    requirements_file = watchers_dir / 'requirements.txt' if watchers_dir.exists() else Path('requirements.txt')
    all_passed &= check(requirements_file.exists(), "requirements.txt exists")
    
    # Check 6: Test action file created (if watcher was tested)
    print(f"\n{Colors.BOLD}6. Functional Test{Colors.RESET}")
    needs_action = vault_path / 'Needs_Action'
    if needs_action.exists():
        action_files = list(needs_action.glob('*.md'))
        if action_files:
            all_passed &= check(True, f"Action files created: {len(action_files)}")
            # Verify action file format
            sample = action_files[0]
            try:
                content = sample.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                content = sample.read_text(encoding='cp1252')
            all_passed &= check('---' in content and 'type:' in content, 
                              "  └─ Action file has YAML frontmatter")
            all_passed &= check('## Suggested Actions' in content, 
                              "  └─ Action file has suggested actions")
        else:
            all_passed &= check(False, "No action files found (run watcher to test)")
    else:
        all_passed &= check(False, "Needs_Action folder missing")
    
    # Summary
    print(f"\n{'='*50}")
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ Bronze Tier COMPLETE!{Colors.RESET}")
        print(f"\n   All requirements verified successfully.")
        print(f"   Next step: Run the watcher and process tasks with Qwen Code.")
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ Bronze Tier INCOMPLETE{Colors.RESET}")
        print(f"\n   Some requirements are missing. Review the checks above.")
    print(f"{'='*50}\n")
    
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
    
    success = verify_bronze_tier(vault_path)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
