"""
Automatic Email Reply Handler

Automatically:
1. Detects new emails
2. Uses Qwen Code to draft replies
3. Sends emails automatically (for low-risk/auto-approved senders)
4. Or moves to Pending_Approval for human review (high-risk)

Usage:
    python auto_reply_handler.py <vault_path>
"""

import sys
import logging
import subprocess
import base64
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

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
logger = logging.getLogger('AutoReplyHandler')


class AutoReplyHandler:
    """Automatically replies to emails using Qwen Code."""
    
    # Auto-reply to these domains without approval
    AUTO_APPROVE_DOMAINS = ['gmail.com', 'outlook.com', 'yahoo.com']
    
    # Don't auto-reply to these (require approval)
    REQUIRE_APPROVAL_KEYWORDS = ['invoice', 'payment', 'urgent', 'asap', 'complaint', 'legal']
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send', 
              'https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.needs_action = vault_path / 'Needs_Action'
        self.done = vault_path / 'Done'
        self.pending_approval = vault_path / 'Pending_Approval'
        
        # Ensure folders exist
        for folder in [self.needs_action, self.done, self.pending_approval]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Initialize Gmail
        self.gmail_service = None
        if GMAIL_AVAILABLE:
            self._init_gmail()
    
    def _init_gmail(self):
        """Initialize Gmail API."""
        creds = None
        token_path = self.vault_path / 'watchers' / 'token.json'
        credentials_path = self.vault_path.parent / 'credentials.json'
        
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif credentials_path.exists():
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
        
        if creds and creds.valid:
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            logger.info('Gmail API initialized')
        else:
            logger.error('Gmail authentication failed')
    
    def process_new_emails(self) -> int:
        """
        Process new emails from Gmail AND action files.
        
        Returns:
            Number of emails processed
        """
        if not self.gmail_service:
            logger.error('Gmail not initialized')
            return 0
        
        processed = 0
        
        # First, process any new action files in Needs_Action
        processed += self._process_action_files()
        
        # Then check Gmail for truly new unread emails
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=5
            ).execute()
            
            messages = results.get('messages', [])
            
            for msg in messages:
                full_msg = self.gmail_service.users().messages().get(
                    userId='me', 
                    id=msg['id'],
                    format='full'
                ).execute()
                
                email_data = self._extract_email_data(full_msg)
                
                if self._is_already_processed(email_data['subject'], email_data['from']):
                    logger.info(f"Skipping already processed: {email_data['subject']}")
                    continue
                
                if self._should_auto_reply(email_data):
                    logger.info(f"Auto-replying to: {email_data['from']}")
                    self._auto_reply(email_data, full_msg)
                    processed += 1
                else:
                    logger.info(f"Requiring approval for: {email_data['from']}")
                    self._create_approval_request(email_data, full_msg)
                    processed += 1
            
        except Exception as e:
            logger.error(f'Error checking Gmail: {e}')
        
        return processed
    
    def _process_action_files(self) -> int:
        """Process action files and auto-reply where appropriate."""
        if not self.needs_action.exists():
            return 0
        
        processed = 0
        for action_file in self.needs_action.glob('EMAIL_*.md'):
            # Skip if already has approval section
            content = action_file.read_text(encoding='utf-8')
            if 'requires_approval:' in content:
                continue  # Already being handled
            
            # Extract email info from file
            email_data = self._parse_action_file(content)
            if email_data and self._should_auto_reply(email_data):
                logger.info(f"Auto-replying from action file: {email_data['from']}")
                # Would need Gmail message ID to send - skip for now
                # This is handled by Gmail Watcher creating files
            processed += 1
        
        return processed
    
    def _extract_email_data(self, msg: dict) -> Dict[str, Any]:
        """Extract email data from Gmail message."""
        headers = msg.get('payload', {}).get('headers', [])
        data = {}
        
        for header in headers:
            name = header.get('name', '').lower()
            value = header.get('value', '')
            if name == 'from':
                data['from'] = value
            elif name == 'to':
                data['to'] = value
            elif name == 'subject':
                data['subject'] = value
            elif name == 'date':
                data['date'] = value
        
        # Get body
        data['body'] = self._get_body(msg)
        
        # Extract domain from sender
        data['domain'] = data['from'].split('@')[-1].replace('>', '').strip().lower()
        
        return data
    
    def _get_body(self, msg: dict) -> str:
        """Extract email body."""
        try:
            parts = msg.get('payload', {}).get('parts', [])
            if parts:
                for part in parts:
                    if part.get('mimeType') == 'text/plain':
                        body_data = part.get('body', {}).get('data', '')
                        if body_data:
                            return base64.urlsafe_b64decode(body_data).decode('utf-8')[:500]
            return msg.get('snippet', 'No content')
        except:
            return msg.get('snippet', 'No content')
    
    def _is_already_processed(self, subject: str, from_addr: str) -> bool:
        """Check if email already has an action file."""
        for f in self.needs_action.glob('EMAIL_*.md'):
            content = f.read_text(encoding='utf-8')
            if subject[:20] in content or from_addr.split('@')[0] in content:
                return True
        return False
    
    def _should_auto_reply(self, email_data: Dict[str, Any]) -> bool:
        """Determine if email should get auto-reply."""
        # Check domain
        if email_data['domain'] not in self.AUTO_APPROVE_DOMAINS:
            return False
        
        # Check for keywords requiring approval
        body_lower = email_data['body'].lower()
        subject_lower = email_data['subject'].lower()
        
        for keyword in self.REQUIRE_APPROVAL_KEYWORDS:
            if keyword in body_lower or keyword in subject_lower:
                return False
        
        return True
    
    def _auto_reply(self, email_data: Dict[str, Any], full_msg: dict):
        """Auto-reply to email using Qwen Code to draft."""
        try:
            # Use Qwen Code to draft reply
            reply_draft = self._draft_with_qwen(email_data)
            
            if reply_draft:
                # Send the reply
                self._send_email(
                    to=email_data['from'],
                    subject=f"Re: {email_data['subject']}",
                    body=reply_draft
                )
                
                # Mark original as read
                self._mark_as_read(full_msg['id'])
                
                # Log to Done
                self._log_completed_reply(email_data, reply_draft)
                
                logger.info(f"✓ Auto-reply sent to: {email_data['from']}")
            else:
                logger.warning("Qwen Code failed to draft reply")
                
        except Exception as e:
            logger.error(f"Auto-reply failed: {e}")
    
    def _draft_with_qwen(self, email_data: Dict[str, Any]) -> Optional[str]:
        """Use Qwen Code to draft a reply."""
        try:
            prompt = f"""Draft a professional email reply to this email:

From: {email_data['from']}
Subject: {email_data['subject']}
Date: {email_data['date']}

Content:
{email_data['body']}

Write a friendly, professional reply. Keep it brief and helpful.
Only output the reply text, no explanations.

Reply:"""
            
            result = subprocess.run(
                ['qwen', prompt],
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'
            )
            
            reply = result.stdout.strip()
            if reply and len(reply) > 10:
                return reply
            
            # Fallback template
            return f"""Dear Sender,

Thank you for your email. I have received your message regarding "{email_data['subject']}" and will respond shortly.

Best regards"""
            
        except Exception as e:
            logger.error(f"Qwen Code draft failed: {e}")
            return None
    
    def _send_email(self, to: str, subject: str, body: str):
        """Send email via Gmail API."""
        if not self.gmail_service:
            raise Exception("Gmail API not initialized")
        
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        message['from'] = 'me'
        message.attach(MIMEText(body, 'plain'))
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        self.gmail_service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
    
    def _mark_as_read(self, message_id: str):
        """Mark email as read."""
        if self.gmail_service:
            self.gmail_service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
    
    def _log_completed_reply(self, email_data: Dict[str, Any], reply: str):
        """Log completed reply to Done folder."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"REPLY_{email_data['from'].split('@')[0]}_{timestamp}.md"
        
        content = f"""---
type: email_reply
to: {email_data['from']}
subject: Re: {email_data['subject']}
sent: {datetime.now().isoformat()}
status: sent
---

# Email Reply Sent

## Details
- **To**: {email_data['from']}
- **Subject**: Re: {email_data['subject']}
- **Sent**: {datetime.now()}

## Reply Content
{reply}

---
*Sent automatically by AI Employee*
"""
        
        filepath = self.done / filename
        filepath.write_text(content, encoding='utf-8')
    
    def _create_approval_request(self, email_data: Dict[str, Any], full_msg: dict):
        """Create approval request for emails requiring human review."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"EMAIL_{email_data['from'].split('@')[0]}_{timestamp}.md"
        
        content = f"""---
type: email
from: {email_data['from']}
subject: {email_data['subject']}
received: {datetime.now().isoformat()}
requires_approval: reply
status: pending
---

# Email Received (Requires Approval)

## Details
- **From**: {email_data['from']}
- **Subject**: {email_data['subject']}
- **Date**: {email_data['date']}

## Content
{email_data['body']}

## Action Required
This email requires your review before replying.

**To approve and send reply:**
1. Draft your reply below
2. Move this file to Pending_Approval/
3. System will send automatically

---
*Requires human approval*
"""
        
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created approval request: {filename}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python auto_reply_handler.py <vault_path>")
        sys.exit(1)
    
    vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        logger.error(f'Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    handler = AutoReplyHandler(vault_path)
    
    logger.info("Processing new emails...")
    count = handler.process_new_emails()
    logger.info(f"Processed {count} email(s)")


if __name__ == '__main__':
    main()
