"""
AI Employee - Full Automation with Email Reply

Single command to run everything:
- Gmail Watcher (detects new emails)
- Orchestrator (processes tasks)
- Email Reply Processor (sends approved replies)
- Dashboard Updater

Usage:
    python auto_employee.py [vault_path]
    
Example:
    python auto_employee.py .
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AutoEmployee')


class AutoEmployee:
    """Full automation with email reply support."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.needs_action = vault_path / 'Needs_Action'
        self.pending_approval = vault_path / 'Pending_Approval'
        self.approved = vault_path / 'Approved'
        self.done = vault_path / 'Done'
        
        # Ensure folders exist
        for folder in [self.needs_action, self.pending_approval, 
                       self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed email subjects
        self.processed_subjects = set()
        
        # Import and initialize Gmail Watcher
        self.gmail_watcher = None
        try:
            from gmail_watcher import GmailWatcher
            self.gmail_watcher = GmailWatcher(str(vault_path), check_interval=60)
            if self.gmail_watcher.service:
                logger.info('✓ Gmail Watcher initialized')
            else:
                logger.warning('Gmail Watcher not authenticated')
        except ImportError as e:
            logger.warning(f'Gmail Watcher not available: {e}')
        except Exception as e:
            logger.error(f'Gmail Watcher error: {e}')
        
        # Import orchestrator
        try:
            from orchestrator import AIEmployeeOrchestrator
            self.orchestrator = AIEmployeeOrchestrator(vault_path, check_interval=30)
            logger.info('✓ Orchestrator initialized')
        except ImportError as e:
            logger.error(f'Could not import orchestrator: {e}')
            self.orchestrator = None
        
        # Import email reply processor
        try:
            from email_reply_processor import EmailReplyProcessor
            self.email_processor = EmailReplyProcessor(vault_path)
            logger.info('✓ Email Reply Processor initialized')
        except ImportError as e:
            logger.warning(f'Email Reply Processor not available: {e}')
            self.email_processor = None
        
        # Import auto reply handler
        try:
            from auto_reply_handler import AutoReplyHandler
            self.auto_reply = AutoReplyHandler(vault_path)
            logger.info('✓ Auto Reply Handler initialized')
        except ImportError as e:
            logger.warning(f'Auto Reply Handler not available: {e}')
            self.auto_reply = None
    
    def run(self):
        """Run the fully automated AI Employee."""
        logger.info('='*70)
        logger.info('🤖 AI Employee - Full Automation Mode')
        logger.info('='*70)
        logger.info(f'Vault: {self.vault_path.absolute()}')
        logger.info('')
        logger.info('✅ Automated Tasks:')
        if self.gmail_watcher and self.gmail_watcher.service:
            logger.info('   • Gmail - Checking for new emails every 60 seconds')
            if self.auto_reply:
                logger.info('   • Auto Reply - Sending replies automatically')
        else:
            logger.info('   • Gmail - Not available (run gmail_watcher.py separately)')
        logger.info('   • Email Replies - Sends automatically when approved')
        logger.info('   • File Processing - Processes Needs_Action folder')
        logger.info('   • Dashboard - Updates automatically every 30 seconds')
        logger.info('   • Plans - Creates Plan.md for complex tasks')
        logger.info('   • Approvals - Processes Pending_Approval folder')
        logger.info('')
        logger.info('📧 How to Reply to Emails:')
        logger.info('   1. Edit reply draft in Needs_Action/EMAIL_*.md')
        logger.info('   2. Move file to Approved/ folder (to send)')
        logger.info('   3. System sends automatically! (within 30 seconds)')
        logger.info('')
        logger.info('   Quick command:')
        logger.info('   move Needs_Action\\EMAIL_*.md Approved\\')
        logger.info('📁 How to Process Files:')
        logger.info('   1. Drop file in DropFolder/')
        logger.info('   2. System creates action file automatically')
        logger.info('   3. System processes and moves to Done/')
        logger.info('')
        logger.info('Press Ctrl+C to stop\n')
        
        # Initial Gmail check - AUTO-REPLY FIRST, then create action files for rest
        if self.gmail_watcher and self.gmail_watcher.service:
            logger.info('Checking Gmail for new emails...')
            try:
                if self.gmail_watcher.service:
                    results = self.gmail_watcher.service.users().messages().list(
                        userId='me', q='is:unread', maxResults=5
                    ).execute()
                    messages = results.get('messages', [])
                    
                    if messages:
                        logger.info(f'✓ Found {len(messages)} new email(s)!')
                        
                        # Process each email
                        for msg in messages:
                            full_msg = self.gmail_watcher.service.users().messages().get(
                                userId='me', id=msg['id'], format='full'
                            ).execute()
                            
                            # Extract email data
                            email_data = self.gmail_watcher._extract_email_data(full_msg) if hasattr(self.gmail_watcher, '_extract_email_data') else None
                            
                            # Check if already processed
                            if email_data and self._is_email_processed(email_data['subject']):
                                continue
                            
                            # Try auto-reply first
                            if self.auto_reply and email_data and self.auto_reply._should_auto_reply(email_data):
                                logger.info(f"🚀 Auto-replying to: {email_data['from']}")
                                try:
                                    reply = self.auto_reply._draft_with_qwen(email_data)
                                    if reply:
                                        self.auto_reply._send_email(
                                            to=email_data['from'],
                                            subject=f"Re: {email_data['subject']}",
                                            body=reply
                                        )
                                        # Mark as read
                                        self.gmail_watcher.service.users().messages().modify(
                                            userId='me', id=msg['id'],
                                            body={'removeLabelIds': ['UNREAD']}
                                        ).execute()
                                        logger.info(f"✓ Auto-reply sent to {email_data['from']}")
                                        self.auto_reply._log_completed_reply(email_data, reply)
                                        continue  # Skip action file creation
                                except Exception as e:
                                    logger.error(f"Auto-reply failed: {e}")
                            
                            # Create action file for non-auto-replied emails
                            filepath = self.gmail_watcher.create_action_file(msg)
                            logger.info(f'  Created: {filepath.name}')
                    else:
                        logger.info('No new emails found.')
            except Exception as e:
                logger.error(f'Error checking Gmail: {e}')
        
        # Initial processing cycle
        logger.info('Running initial processing cycle...')
        self.run_cycle()
        
        # Main loop - check every 30 seconds
        cycle_count = 0
        gmail_check_count = 0
        try:
            while True:
                cycle_count += 1
                
                # Check Gmail every 60 seconds (every 2nd cycle)
                if self.gmail_watcher and self.gmail_watcher.service:
                    gmail_check_count += 1
                    if gmail_check_count >= 2:  # Every 60 seconds
                        logger.info(f'--- Checking Gmail (Cycle {cycle_count}) ---')
                        try:
                            items = self.gmail_watcher.check_for_updates()
                            if items:
                                logger.info(f'✓ Found {len(items)} new email(s)!')
                                for item in items:
                                    filepath = self.gmail_watcher.create_action_file(item)
                                    logger.info(f'  Created: {filepath.name}')
                            else:
                                logger.info(f'No new emails (Cycle {cycle_count})')
                            
                            # Also try auto-reply
                            if self.auto_reply:
                                reply_count = self.auto_reply.process_new_emails()
                                if reply_count > 0:
                                    logger.info(f'✓ Sent {reply_count} auto-reply/ies!')
                        except Exception as e:
                            logger.error(f'Error checking Gmail: {e}')
                        gmail_check_count = 0
                
                # Run processing cycle
                logger.info(f'--- Processing Cycle {cycle_count} ---')
                self.run_cycle()
                
                time.sleep(30)
                
        except KeyboardInterrupt:
            logger.info('\n\n⏹️  Stopping AI Employee...')
    
    def run_cycle(self):
        """Run one processing cycle."""
        # Check for files moved to Approved folder and send them
        if self.approved.exists():
            approved_emails = list(self.approved.glob('EMAIL_*.md'))
            if approved_emails and self.email_processor:
                logger.info(f'Processing {len(approved_emails)} approved email(s)...')
                for email_file in approved_emails:
                    try:
                        # Process the approved email
                        content = email_file.read_text(encoding='utf-8')
                        reply_data = self.email_processor._parse_reply(content)
                        if reply_data and self.email_processor.send_reply(reply_data):
                            # Move to Done
                            dest = self.done / email_file.name
                            email_file.rename(dest)
                            self.email_processor._add_completion_note(dest)
                            logger.info(f'✅ Sent: {email_file.name}')
                        else:
                            logger.warning(f'Failed to send: {email_file.name}')
                    except Exception as e:
                        logger.error(f'Error sending {email_file.name}: {e}')
        
        # Update dashboard
        if self.orchestrator:
            self.orchestrator.dashboard.update()
        
        # Show pending count
        if self.pending_approval.exists():
            pending = list(self.pending_approval.glob('EMAIL_*.md'))
            if pending:
                logger.info(f'📧 {len(pending)} email(s) pending approval')
                for f in pending:
                    logger.info(f'   - {f.name}')


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        vault_path = Path('.')
    else:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        logger.error(f'Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    auto_employee = AutoEmployee(vault_path)
    auto_employee.run()


if __name__ == '__main__':
    main()
