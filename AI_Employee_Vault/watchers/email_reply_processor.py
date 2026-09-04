"""
Email Reply Processor - Silver Tier Skill

Processes email replies with human-in-the-loop approval.
Workflow:
1. Gmail Watcher creates action file with reply draft
2. User edits draft and moves to Pending_Approval
3. Approval Workflow processes and sends via Email MCP
4. Sent email logged and action moved to Done

Usage:
    python email_reply_processor.py <vault_path>
    python email_reply_processor.py <vault_path> --send FILE
"""

import sys
import logging
import smtplib
import base64
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any

# Gmail API support
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    import pickle
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EmailReplyProcessor')


class EmailReplyProcessor:
    """
    Processes email replies with approval workflow.
    """
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, vault_path: Path, credentials_path: str = None):
        """
        Initialize Email Reply Processor.
        
        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to Gmail credentials.json
        """
        self.vault_path = vault_path
        self.needs_action = vault_path / 'Needs_Action'
        self.pending_approval = vault_path / 'Pending_Approval'
        self.approved = vault_path / 'Approved'
        self.done = vault_path / 'Done'
        self.rejected = vault_path / 'Rejected'
        
        # Ensure folders exist
        for folder in [self.pending_approval, self.approved, self.done, self.rejected]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Find credentials
        if credentials_path:
            self.credentials_path = credentials_path
        elif (vault_path.parent / 'credentials.json').exists():
            self.credentials_path = vault_path.parent / 'credentials.json'
        else:
            self.credentials_path = Path('credentials.json')
        
        self.token_path = self.vault_path / 'watchers' / 'token.json'
        self.gmail_service = None
        
        # Initialize Gmail API
        if GMAIL_AVAILABLE:
            self._init_gmail()
    
    def _init_gmail(self):
        """Initialize Gmail API for sending emails."""
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Get new credentials if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    logger.error(f'Credentials not found: {self.credentials_path}')
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.gmail_service = build('gmail', 'v1', credentials=creds)
        logger.info('Gmail API initialized for sending')
    
    def process_pending_replies(self) -> int:
        """
        Process all pending reply approvals.
        
        Returns:
            Number of replies processed
        """
        count = 0
        
        # Check approved folder for reply requests
        if not self.approved.exists():
            return 0
        
        for approval_file in self.approved.glob('EMAIL_*.md'):
            try:
                content = approval_file.read_text(encoding='utf-8')
                
                # Check if this is a reply request
                if 'requires_approval: reply' in content:
                    logger.info(f'Processing approved reply: {approval_file.name}')
                    
                    # Extract reply details
                    reply_data = self._parse_reply(content)
                    
                    if reply_data and self.send_reply(reply_data):
                        # Move to Done
                        dest = self.done / approval_file.name
                        approval_file.rename(dest)
                        
                        # Add completion note
                        self._add_completion_note(dest)
                        
                        count += 1
                        logger.info(f'Reply sent successfully: {reply_data["to"]}')
                    else:
                        logger.error(f'Failed to send reply: {approval_file.name}')
                        
            except Exception as e:
                logger.error(f'Error processing {approval_file.name}: {e}')
        
        return count
    
    def _parse_reply(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse reply details from action file."""
        try:
            # Extract reply section
            if '**Reply To**:' not in content:
                return None

            lines = content.split('\n')
            reply_data = {}
            in_reply_section = False
            in_draft = False
            draft_lines = []

            for line in lines:
                if '**Reply To**:' in line:
                    # Extract email after "**Reply To**: "
                    parts = line.split('**Reply To**:')
                    if len(parts) > 1:
                        reply_data['to'] = parts[1].strip()
                    in_reply_section = True
                elif '**Subject**:' in line and in_reply_section:
                    # Extract subject after "**Subject**: "
                    parts = line.split('**Subject**:')
                    if len(parts) > 1:
                        reply_data['subject'] = parts[1].strip()
                elif '**Draft Response**:' in line:
                    in_draft = True
                elif in_draft and line.strip() and not line.startswith('---'):
                    draft_lines.append(line)
                elif line.startswith('---') and in_draft:
                    break

            if draft_lines:
                reply_data['body'] = '\n'.join(draft_lines).strip()

            # Validate required fields
            if not all(k in reply_data for k in ['to', 'subject', 'body']):
                return None

            return reply_data

        except Exception as e:
            logger.error(f'Error parsing reply: {e}')
            return None
    
    def send_reply(self, reply_data: Dict[str, Any]) -> bool:
        """
        Send email reply via Gmail API.
        
        Args:
            reply_data: Dict with to, subject, body
            
        Returns:
            True if successful
        """
        try:
            if not self.gmail_service:
                logger.error('Gmail API not initialized')
                return False
            
            # Create message
            message = MIMEMultipart()
            message['to'] = reply_data['to']
            message['subject'] = reply_data['subject']
            message['from'] = 'me'
            
            # Add In-Reply-To header if original message ID available
            if 'in_reply_to' in reply_data:
                message['In-Reply-To'] = reply_data['in_reply_to']
            
            # Attach body
            message.attach(MIMEText(reply_data['body'], 'plain'))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send via Gmail API
            result = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f'Email sent: {result["id"]}')
            return True
            
        except Exception as e:
            logger.error(f'Error sending email: {e}')
            return False
    
    def _add_completion_note(self, filepath: Path):
        """Add completion note to action file."""
        try:
            content = filepath.read_text(encoding='utf-8')
            content += f'\n\n---\n## Completed\n- **Reply Sent**: {datetime.now().isoformat()}\n- **Status**: Sent via Gmail API\n'
            filepath.write_text(content, encoding='utf-8')
        except Exception as e:
            logger.error(f'Error adding completion note: {e}')
    
    def create_approval_request(self, action_file: Path, reply_draft: str) -> Path:
        """
        Create approval request for email reply.
        
        Args:
            action_file: Original action file path
            reply_draft: Draft reply content
            
        Returns:
            Path to approval request file
        """
        # Read original action file
        content = action_file.read_text(encoding='utf-8')
        
        # Create approval request
        approval_content = f'''---
type: approval_request
action: email_reply
source_file: {action_file.name}
created: {datetime.now().isoformat()}
status: pending
---

# Approval Required: Email Reply

## Original Email
{content[:500]}...

## Proposed Reply
{reply_draft}

## To Approve
1. Review the reply above
2. Edit if needed
3. Move this file to /Approved folder

## To Reject
Move this file to /Rejected folder with reason

---
*Created by Email Reply Processor*
'''
        
        approval_path = self.pending_approval / f'APPROVAL_{action_file.name}'
        approval_path.write_text(approval_content, encoding='utf-8')
        
        logger.info(f'Created approval request: {approval_path.name}')
        return approval_path


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python email_reply_processor.py <vault_path>")
        print("       python email_reply_processor.py <vault_path> --process")
        print("\nExamples:")
        print("  python email_reply_processor.py ../AI_Employee_Vault")
        print("  python email_reply_processor.py ../AI_Employee_Vault --process")
        sys.exit(1)
    
    vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        logger.error(f'Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    processor = EmailReplyProcessor(vault_path)
    
    if '--process' in sys.argv:
        count = processor.process_pending_replies()
        print(f"\n✅ Processed {count} pending replies")
    else:
        print(f"\n📧 Email Reply Processor Ready")
        print(f"   Vault: {vault_path}")
        print(f"\n   Workflow:")
        print(f"   1. Gmail Watcher creates action file in Needs_Action/")
        print(f"   2. Edit reply draft in the action file")
        print(f"   3. Move file to Pending_Approval/")
        print(f"   4. Run: python email_reply_processor.py .. --process")
        print(f"   5. Reply sent and file moved to Done/")


if __name__ == '__main__':
    main()
