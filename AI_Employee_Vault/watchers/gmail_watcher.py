"""
Gmail Watcher - Silver Tier Skill

Monitors Gmail for new unread/important emails and creates action files.

Usage:
    python gmail_watcher.py <vault_path> [check_interval_seconds]
    python gmail_watcher.py <vault_path> --authenticate

Example:
    python gmail_watcher.py ../AI_Employee_Vault 120
    python gmail_watcher.py ../AI_Employee_Vault --authenticate
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

# Gmail API dependencies
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    import pickle
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("WARNING: Gmail API packages not installed.")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new unread/important emails.
    
    Creates action files in Needs_Action folder for each new email.
    """
    
    # Gmail API scopes - including SEND for auto-reply
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.send']
    
    def __init__(self, vault_path: str, credentials_path: str = None, 
                 check_interval: int = 120):
        """
        Initialize Gmail watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            credentials_path: Path to Gmail credentials.json
            check_interval: Seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)
        
        # Default paths - look for credentials.json in project root
        if credentials_path:
            self.credentials_path = credentials_path
        elif os.path.exists('../../credentials.json'):
            self.credentials_path = '../../credentials.json'
        elif os.path.exists('../credentials.json'):
            self.credentials_path = '../credentials.json'
        elif os.path.exists('credentials.json'):
            self.credentials_path = 'credentials.json'
        else:
            self.credentials_path = os.environ.get(
                'GMAIL_CREDENTIALS_PATH', 'credentials.json')
        
        self.token_path = os.environ.get(
            'GMAIL_TOKEN_PATH', 'token.json')
        
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    self.logger.error(
                        f'Credentials file not found: {self.credentials_path}\n'
                        f'Download from: https://console.cloud.google.com/apis/credentials')
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build service
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info('Gmail authentication successful')
    
    def check_for_updates(self) -> list:
        """
        Check for new unread emails.

        Returns:
            List of new message IDs
        """
        if not self.service:
            return []

        try:
            # Query: unread emails (removed 'is:important' to catch all unread)
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            
            # Filter out already processed
            new_messages = [
                m for m in messages 
                if m['id'] not in self.processed_ids
            ]
            
            return new_messages
            
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            return []
    
    def create_action_file(self, message: dict) -> Path:
        """
        Create action file for an email.
        
        Args:
            message: Gmail message dict with 'id' key
            
        Returns:
            Path to created file
        """
        try:
            # Get full message
            msg = self.service.users().messages().get(
                userId='me', 
                id=message['id'],
                format='full',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()
            
            # Extract headers
            headers = msg.get('payload', {}).get('headers', [])
            email_data = {}
            
            for header in headers:
                name = header.get('name', '').lower()
                value = header.get('value', '')
                if name == 'from':
                    email_data['from'] = value
                elif name == 'to':
                    email_data['to'] = value
                elif name == 'subject':
                    email_data['subject'] = value
                elif name == 'date':
                    email_data['date'] = value
            
            # Get body content
            body = self._extract_body(msg)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_subject = self._sanitize_filename(
                email_data.get('subject', 'No Subject')[:30])
            
            # Create content with reply suggestion
            content = f'''---
type: email
from: {email_data.get('from', 'Unknown')}
to: {email_data.get('to', 'Unknown')}
subject: {email_data.get('subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: high
status: pending
requires_approval: reply
---

# Email Received

## Details
- **From**: {email_data.get('from', 'Unknown')}
- **To**: {email_data.get('to', 'Unknown')}
- **Subject**: {email_data.get('subject', 'No Subject')}
- **Received**: {email_data.get('date', 'Unknown')}

## Content
{body}

## Suggested Actions
- [ ] Read full email in Gmail
- [ ] Reply to sender (requires approval)
- [ ] Forward to relevant party
- [ ] Archive after processing

## Reply Draft (for approval)
*To reply, draft your response below and move this file to /Pending_Approval*

---
**Reply To**: {email_data.get('from', '')}
**Subject**: Re: {email_data.get('subject', '')}

**Draft Response**:

Dear Sender,

[Type your response here]

Best regards,
[Your Name]

---
*Created by GmailWatcher*
'''
            
            # Write file
            filename = f'EMAIL_{safe_subject}_{timestamp}.md'
            filepath = self.needs_action / filename
            filepath.write_text(content, encoding='utf-8')
            
            # Mark as processed
            self.processed_ids.add(message['id'])
            
            self.logger.info(f'Created action file: {filename}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise
    
    def _extract_body(self, msg: dict) -> str:
        """Extract email body from Gmail message."""
        try:
            payload = msg.get('payload', {})
            parts = payload.get('parts', [])
            
            # Try to get body from parts
            if parts:
                for part in parts:
                    if part.get('mimeType') == 'text/plain':
                        body_data = part.get('body', {}).get('data', '')
                        if body_data:
                            import base64
                            body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                            return body[:500]  # Limit to 500 chars
            
            # Fallback to snippet
            return msg.get('snippet', 'No content available')
            
        except Exception as e:
            self.logger.error(f'Error extracting body: {e}')
            return msg.get('snippet', 'No content available')
    
    def _sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filename."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            text = text.replace(char, '_')
        return text.strip()
    
    def run_once(self) -> int:
        """Run single check cycle (for testing)."""
        if not self.service:
            self.logger.warning('Not authenticated, skipping')
            return 0
        
        return super().run_once()


def authenticate_only(vault_path: str, credentials_path: str = None):
    """Run authentication flow only."""
    print("Gmail Authentication")
    print("=" * 40)
    print("\nThis will open a browser window for Gmail authentication.")
    print("Follow the prompts to authorize the application.\n")
    
    watcher = GmailWatcher(vault_path, credentials_path)
    
    if watcher.service:
        print("\n✓ Authentication successful!")
        print(f"Token saved to: {watcher.token_path}")
    else:
        print("\n✗ Authentication failed")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python gmail_watcher.py <vault_path> [interval_seconds]")
        print("       python gmail_watcher.py <vault_path> --authenticate")
        print("\nExample:")
        print("  python gmail_watcher.py ../AI_Employee_Vault 120")
        print("  python gmail_watcher.py ../AI_Employee_Vault --authenticate")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    
    # Check for authenticate flag
    if len(sys.argv) > 2 and '--authenticate' in sys.argv:
        authenticate_only(vault_path)
        return
    
    check_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    
    if not GMAIL_AVAILABLE:
        print("\nGmail API packages not installed.")
        print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        sys.exit(1)
    
    watcher = GmailWatcher(vault_path, check_interval=check_interval)
    
    if not watcher.service:
        print("\nAuthentication required. Run with --authenticate flag first.")
        sys.exit(1)
    
    print(f"\n📧 Gmail Watcher Started")
    print(f"   Vault: {vault_path}")
    print(f"   Check interval: {check_interval}s")
    print(f"   Query: is:unread")
    print(f"\n   Running initial check...")
    print(f"   Press Ctrl+C to stop\n")

    # Run initial check immediately
    try:
        items = watcher.check_for_updates()
        if items:
            print(f"   Found {len(items)} new email(s)!")
            for item in items:
                filepath = watcher.create_action_file(item)
                print(f"   ✓ Created: {filepath.name}")
        else:
            print("   No new unread emails found.")
    except Exception as e:
        print(f"   Initial check error: {e}")
    
    print(f"\n   Continuing to monitor (every {check_interval}s)...\n")
    watcher.run()


if __name__ == '__main__':
    main()
