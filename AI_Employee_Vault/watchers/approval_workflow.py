"""
Approval Workflow - Silver Tier Skill

Human-in-the-Loop (HITL) approval system for sensitive actions.

Usage:
    python approval_workflow.py <vault_path> --approve FILE
    python approval_workflow.py <vault_path> --reject FILE --reason "reason"
    python approval_workflow.py <vault_path> --list
    python approval_workflow.py <vault_path> --cleanup

Example:
    python approval_workflow.py ../AI_Employee_Vault --list
    python approval_workflow.py ../AI_Employee_Vault --approve APPROVAL_payment.md
"""

import sys
import logging
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ApprovalWorkflow')


class ApprovalWorkflow:
    """
    Manages approval workflow for sensitive actions.
    """
    
    # Default approval thresholds
    PAYMENT_THRESHOLD = 100.00  # Auto-approve payments below this
    REQUIRE_APPROVAL_TYPES = {'payment', 'email_send', 'social_post', 'delete', 'subscription'}
    
    def __init__(self, vault_path: Path):
        """
        Initialize Approval Workflow.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = vault_path
        self.pending_approval = vault_path / 'Pending_Approval'
        self.approved = vault_path / 'Approved'
        self.rejected = vault_path / 'Rejected'
        self.done = vault_path / 'Done'
        self.accounting = vault_path / 'Accounting'
        
        # Ensure folders exist
        for folder in [self.pending_approval, self.approved, 
                       self.rejected, self.accounting]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Approval log
        self.log_path = self.accounting / 'approval_log.md'
        self._init_log()
    
    def _init_log(self):
        """Initialize approval log if not exists."""
        if not self.log_path.exists():
            content = f'''---
type: approval_log
created: {datetime.now().isoformat()}
---

# Approval History

| Date | Action | Amount | Decision | Notes |
|------|--------|--------|----------|-------|

'''
            self.log_path.write_text(content, encoding='utf-8')
    
    def requires_approval(self, action_data: Dict[str, Any]) -> bool:
        """
        Check if action requires approval.
        
        Args:
            action_data: Dict with action type, amount, etc.
            
        Returns:
            True if approval required
        """
        action_type = action_data.get('type', '')
        
        # Check type
        if action_type in self.REQUIRE_APPROVAL_TYPES:
            return True
        
        # Check payment amount
        if action_type == 'payment':
            amount = float(action_data.get('amount', 0))
            if amount > self.PAYMENT_THRESHOLD:
                return True
        
        # Check content for keywords
        content = action_data.get('content', '').lower()
        approval_keywords = ['approve', 'approval', 'permission', 'authorize']
        for keyword in approval_keywords:
            if keyword in content:
                return True
        
        return False
    
    def create_approval(
        self,
        action_type: str,
        description: str,
        source_file: Path,
        amount: float = None,
        recipient: str = None,
        reason: str = None,
        expires_hours: int = 24
    ) -> Path:
        """
        Create approval request file.
        
        Args:
            action_type: Type of action (payment, email_send, etc.)
            description: Description of the action
            source_file: Original action file path
            amount: Amount if payment
            recipient: Recipient if applicable
            reason: Reason for the action
            expires_hours: Hours until expiration
            
        Returns:
            Path to created approval file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        expires = datetime.now() + timedelta(hours=expires_hours)
        
        # Generate filename
        safe_desc = self._sanitize_filename(description)[:20]
        filename = f'APPROVAL_{action_type}_{safe_desc}_{timestamp}.md'
        approval_path = self.pending_approval / filename
        
        # Build content
        content = f'''---
type: approval_request
action: {action_type}
'''
        if amount:
            content += f'amount: {amount:.2f}\n'
        if recipient:
            content += f'recipient: {recipient}\n'
        
        content += f'''reason: {reason or description}
created: {datetime.now().isoformat()}
expires: {expires.isoformat()}
status: pending
source_file: {source_file.name}
---

# Approval Required: {action_type.title()}

## Details
- **Action**: {action_type.replace('_', ' ').title()}
'''
        if amount:
            content += f'- **Amount**: ${amount:.2f}\n'
        if recipient:
            content += f'- **Recipient**: {recipient}\n'
        
        content += f'''- **Reason**: {reason or description}
- **Created**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Expires**: {expires.strftime("%Y-%m-%d %H:%M:%S")}

## Source File
Original action: `{source_file.name}`

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.

## Notes
*Add any comments or conditions.*

---
*Created by AI Employee Approval System*
'''
        
        approval_path.write_text(content, encoding='utf-8')
        logger.info(f'Created approval request: {filename}')
        
        return approval_path
    
    def approve(self, approval_file: Path, notes: str = None) -> bool:
        """
        Approve an action.
        
        Args:
            approval_file: Path to approval file
            notes: Optional notes
            
        Returns:
            True if successful
        """
        return self._process_approval(approval_file, 'approved', notes)
    
    def reject(self, approval_file: Path, reason: str = None) -> bool:
        """
        Reject an action.
        
        Args:
            approval_file: Path to approval file
            reason: Reason for rejection
            
        Returns:
            True if successful
        """
        return self._process_approval(approval_file, 'rejected', reason)
    
    def _process_approval(self, approval_file: Path, decision: str, notes: str = None) -> bool:
        """Process approval decision."""
        if not approval_file.exists():
            logger.error(f'Approval file not found: {approval_file}')
            return False
        
        try:
            # Read approval file
            content = approval_file.read_text(encoding='utf-8')
            
            # Extract details for logging
            action_type = 'unknown'
            amount = None
            for line in content.split('\n'):
                if 'action:' in line:
                    action_type = line.split(':')[1].strip()
                if 'amount:' in line:
                    amount = line.split(':')[1].strip()
            
            # Update file with decision
            content = content.replace(
                'status: pending',
                f'status: {decision}'
            )
            content += f'\n\n## Decision\n- **Status**: {decision.title()}\n- **Decided**: {datetime.now().isoformat()}\n'
            if notes:
                content += f'- **Notes**: {notes}\n'
            
            # Move to appropriate folder
            if decision == 'approved':
                dest = self.approved / approval_file.name
            else:
                dest = self.rejected / approval_file.name
            
            approval_file.write_text(content, encoding='utf-8')
            shutil.move(str(approval_file), str(dest))
            
            # Log decision
            self._log_decision(action_type, amount, decision, notes)
            
            logger.info(f'{decision.title()}: {approval_file.name}')
            return True
            
        except Exception as e:
            logger.error(f'Error processing approval: {e}')
            return False
    
    def _log_decision(self, action_type: str, amount: str, decision: str, notes: str = None):
        """Log approval decision."""
        try:
            content = self.log_path.read_text(encoding='utf-8')
            
            # Add new entry
            amount_str = f'${amount}' if amount else '-'
            notes_str = notes or '-'
            timestamp = datetime.now().strftime('%Y-%m-%d')
            
            new_entry = f'| {timestamp} | {action_type} | {amount_str} | {decision.title()} | {notes_str} |\n'
            
            # Insert after header row
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '|------|' in line:
                    lines.insert(i + 1, new_entry)
                    break
            
            self.log_path.write_text('\n'.join(lines), encoding='utf-8')
            
        except Exception as e:
            logger.error(f'Error logging decision: {e}')
    
    def list_pending(self) -> list:
        """List all pending approvals."""
        pending = []
        for f in self.pending_approval.glob('*.md'):
            content = f.read_text(encoding='utf-8')
            info = {'path': f, 'name': f.name}
            for line in content.split('\n')[:15]:
                if 'action:' in line and 'action_' not in line:
                    info['action'] = line.split(':')[1].strip()
                if 'amount:' in line:
                    info['amount'] = line.split(':')[1].strip()
                if 'created:' in line:
                    info['created'] = line.split(':')[1].strip()
                if 'expires:' in line:
                    info['expires'] = line.split(':')[1].strip()
            pending.append(info)
        return pending
    
    def cleanup_expired(self) -> int:
        """
        Move expired approvals to Rejected.
        
        Returns:
            Number of expired approvals moved
        """
        count = 0
        now = datetime.now()
        
        for f in self.pending_approval.glob('*.md'):
            content = f.read_text(encoding='utf-8')
            for line in content.split('\n'):
                if 'expires:' in line:
                    expires_str = line.split(':')[1].strip()
                    try:
                        expires = datetime.fromisoformat(expires_str)
                        if expires < now:
                            self.reject(f, 'Expired - no response')
                            count += 1
                    except Exception:
                        pass
                    break
        
        return count
    
    def _sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filename."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            text = text.replace(char, '_')
        return text.strip()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python approval_workflow.py <vault_path> [options]")
        print("\nOptions:")
        print("  --list                   List pending approvals")
        print("  --approve FILE           Approve an action")
        print("  --reject FILE            Reject an action")
        print("  --reason TEXT            Reason for rejection")
        print("  --notes TEXT             Notes for approval")
        print("  --cleanup                Remove expired approvals")
        print("\nExamples:")
        print("  python approval_workflow.py ../AI_Employee_Vault --list")
        print("  python approval_workflow.py ../AI_Employee_Vault --approve APPROVAL_payment.md")
        print("  python approval_workflow.py ../AI_Employee_Vault --reject APPROVAL_email.md --reason \"Wrong recipient\"")
        sys.exit(1)
    
    vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        logger.error(f'Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    workflow = ApprovalWorkflow(vault_path)
    
    # Parse options
    if '--list' in sys.argv:
        pending = workflow.list_pending()
        print(f"\n⏳ Pending Approvals ({len(pending)}):")
        for item in pending:
            print(f"\n  📄 {item['name']}")
            print(f"     Action: {item.get('action', 'unknown')}")
            if item.get('amount'):
                print(f"     Amount: ${item['amount']}")
            print(f"     Created: {item.get('created', 'unknown')}")
            print(f"     Expires: {item.get('expires', 'unknown')}")
    
    elif '--approve' in sys.argv:
        idx = sys.argv.index('--approve')
        if idx + 1 < len(sys.argv):
            approval_file = workflow.pending_approval / sys.argv[idx + 1]
            notes = None
            if '--notes' in sys.argv:
                notes_idx = sys.argv.index('--notes')
                if notes_idx + 1 < len(sys.argv):
                    notes = sys.argv[notes_idx + 1]
            
            if workflow.approve(approval_file, notes):
                print(f"\n✅ Approved: {approval_file.name}")
            else:
                print(f"\n❌ Failed to approve")
    
    elif '--reject' in sys.argv:
        idx = sys.argv.index('--reject')
        if idx + 1 < len(sys.argv):
            approval_file = workflow.pending_approval / sys.argv[idx + 1]
            reason = None
            if '--reason' in sys.argv:
                reason_idx = sys.argv.index('--reason')
                if reason_idx + 1 < len(sys.argv):
                    reason = sys.argv[reason_idx + 1]
            
            if workflow.reject(approval_file, reason):
                print(f"\n❌ Rejected: {approval_file.name}")
            else:
                print(f"\n❌ Failed to reject")
    
    elif '--cleanup' in sys.argv:
        count = workflow.cleanup_expired()
        print(f"\n🧹 Cleaned up {count} expired approvals")


if __name__ == '__main__':
    main()
