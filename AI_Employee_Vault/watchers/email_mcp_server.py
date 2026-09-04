"""
Email MCP Server - Silver Tier Skill

MCP server for sending and managing emails via SMTP or Gmail API.

Usage:
    python email_mcp_server.py --smtp smtp.gmail.com --port 587 --user EMAIL --password PASSWORD
    python email_mcp_server.py --gmail-api --credentials credentials.json

Example:
    python email_mcp_server.py --smtp smtp.gmail.com --port 587 --user me@gmail.com --password app-pass
"""

import sys
import os
import json
import logging
import smtplib
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional, List, Dict, Any

# Gmail API support
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    import base64
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('EmailMCP')


class EmailServer:
    """Email server supporting SMTP and Gmail API."""
    
    # Gmail API scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.send',
              'https://www.googleapis.com/auth/gmail.readonly',
              'https://www.googleapis.com/auth/gmail.draft']
    
    def __init__(self, smtp_server: str = None, smtp_port: int = 587,
                 username: str = None, password: str = None,
                 use_gmail_api: bool = False, credentials_path: str = None):
        """
        Initialize email server.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port (587 for TLS, 465 for SSL)
            username: Email username
            password: Email password (or app-specific password)
            use_gmail_api: Use Gmail API instead of SMTP
            credentials_path: Path to Gmail API credentials.json
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_gmail_api = use_gmail_api
        self.gmail_service = None
        
        # Gmail API setup
        if use_gmail_api and GMAIL_AVAILABLE:
            self._setup_gmail_api(credentials_path)
    
    def _setup_gmail_api(self, credentials_path: str = None):
        """Set up Gmail API connection."""
        creds = None
        token_path = 'token.json'
        
        # Load existing token
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = Credentials.from_authorized_user_file(token, self.SCOPES)
        
        # Get new credentials if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not credentials_path:
                    credentials_path = os.environ.get('GMAIL_CREDENTIALS', 'credentials.json')
                
                if not os.path.exists(credentials_path):
                    logger.error(f'Gmail credentials not found: {credentials_path}')
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(token_path, 'wb') as token:
                token.write(creds.to_json())
        
        self.gmail_service = build('gmail', 'v1', credentials=creds)
        logger.info('Gmail API connected')
    
    def send_email(self, to: str, subject: str, body: str, 
                   html: bool = False, attachments: List[str] = None,
                   cc: str = None, bcc: str = None) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            html: True if body is HTML, False for plain text
            attachments: List of file paths to attach
            cc: CC recipient
            bcc: BCC recipient
            
        Returns:
            Dict with success status and message_id
        """
        try:
            if self.use_gmail_api and self.gmail_service:
                return self._send_gmail_api(to, subject, body, html, attachments, cc, bcc)
            else:
                return self._send_smtp(to, subject, body, html, attachments, cc, bcc)
                
        except Exception as e:
            logger.error(f'Failed to send email: {e}')
            return {'success': False, 'error': str(e)}
    
    def _send_smtp(self, to: str, subject: str, body: str,
                   html: bool = False, attachments: List[str] = None,
                   cc: str = None, bcc: str = None) -> Dict[str, Any]:
        """Send email via SMTP."""
        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to
        msg['Subject'] = subject
        
        if cc:
            msg['Cc'] = cc
        if bcc:
            # BCC is not added to headers, just used for sending
            pass
        
        # Add body
        content_type = 'html' if html else 'plain'
        msg.attach(MIMEText(body, content_type))
        
        # Add attachments
        if attachments:
            for file_path in attachments:
                try:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={os.path.basename(file_path)}'
                        )
                        msg.attach(part)
                except Exception as e:
                    logger.warning(f'Failed to attach {file_path}: {e}')
        
        # Send
        recipients = [to]
        if cc:
            recipients.extend(cc.split(','))
        if bcc:
            recipients.extend(bcc.split(','))
        
        try:
            # Connect and send
            if self.smtp_port == 465:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            
            server.login(self.username, self.password)
            server.sendmail(self.username, recipients, msg.as_string())
            server.quit()
            
            logger.info(f'Email sent to {to}')
            return {'success': True, 'message_id': f'smtp_{int(__import__("time").time())}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _send_gmail_api(self, to: str, subject: str, body: str,
                        html: bool = False, attachments: List[str] = None,
                        cc: str = None, bcc: str = None) -> Dict[str, Any]:
        """Send email via Gmail API."""
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            message['from'] = 'me'
            
            if cc:
                message['cc'] = cc
            
            # Add body
            content_type = 'html' if html else 'plain'
            message.attach(MIMEText(body, content_type))
            
            # Add attachments
            if attachments:
                for file_path in attachments:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={os.path.basename(file_path)}'
                        )
                        message.attach(part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send via API
            result = self.gmail_service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f'Email sent via Gmail API: {result["id"]}')
            return {'success': True, 'message_id': result['id']}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_draft(self, to: str, subject: str, body: str,
                     html: bool = False) -> Dict[str, Any]:
        """Create a draft email."""
        if not self.gmail_service:
            return {'success': False, 'error': 'Gmail API required for drafts'}
        
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            message['from'] = 'me'
            
            content_type = 'html' if html else 'plain'
            message.attach(MIMEText(body, content_type))
            
            # Encode
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Create draft
            result = self.gmail_service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()
            
            logger.info(f'Draft created: {result["id"]}')
            return {'success': True, 'draft_id': result['id']}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_emails(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search emails."""
        if not self.gmail_service:
            return []
        
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                detail = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                
                emails.append({
                    'id': detail['id'],
                    'headers': {h['name']: h['value'] for h in detail['payload']['headers']}
                })
            
            return emails
            
        except Exception as e:
            logger.error(f'Search failed: {e}')
            return []


# MCP Server Implementation
class EmailMCPServer:
    """MCP server for email operations."""
    
    def __init__(self, email_server: EmailServer):
        self.email = email_server
        self.tools = {
            'send_email': {
                'description': 'Send an email',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'to': {'type': 'string', 'description': 'Recipient email'},
                        'subject': {'type': 'string', 'description': 'Email subject'},
                        'body': {'type': 'string', 'description': 'Email body'},
                        'html': {'type': 'boolean', 'description': 'HTML format'},
                        'attachments': {'type': 'array', 'items': {'type': 'string'}}
                    },
                    'required': ['to', 'subject', 'body']
                }
            },
            'create_draft': {
                'description': 'Create a draft email',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'to': {'type': 'string'},
                        'subject': {'type': 'string'},
                        'body': {'type': 'string'},
                        'html': {'type': 'boolean'}
                    },
                    'required': ['to', 'subject', 'body']
                }
            },
            'search_emails': {
                'description': 'Search emails',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'query': {'type': 'string'},
                        'max_results': {'type': 'integer'}
                    }
                }
            }
        }
    
    def handle_tool_call(self, tool_name: str, arguments: Dict) -> Dict:
        """Handle MCP tool call."""
        if tool_name == 'send_email':
            return self.email.send_email(**arguments)
        elif tool_name == 'create_draft':
            return self.email.create_draft(**arguments)
        elif tool_name == 'search_emails':
            results = self.email.search_emails(
                arguments.get('query', ''),
                arguments.get('max_results', 10)
            )
            return {'emails': results}
        else:
            return {'error': f'Unknown tool: {tool_name}'}


def main():
    """Main entry point - run as MCP server or CLI."""
    parser = argparse.ArgumentParser(description='Email MCP Server')
    parser.add_argument('--smtp', help='SMTP server address')
    parser.add_argument('--port', type=int, default=587, help='SMTP port')
    parser.add_argument('--user', help='Email username')
    parser.add_argument('--password', help='Email password')
    parser.add_argument('--gmail-api', action='store_true', help='Use Gmail API')
    parser.add_argument('--credentials', help='Gmail API credentials.json path')
    parser.add_argument('--test', help='Send test email to this address')
    
    args = parser.parse_args()
    
    # Create email server
    if args.gmail_api:
        email = EmailServer(use_gmail_api=True, credentials_path=args.credentials)
    else:
        if not args.smtp or not args.user or not args.password:
            print("For SMTP: --smtp, --user, --password required")
            print("For Gmail API: --gmail-api --credentials required")
            sys.exit(1)
        email = EmailServer(
            smtp_server=args.smtp,
            smtp_port=args.port,
            username=args.user,
            password=args.password
        )
    
    # Test mode
    if args.test:
        result = email.send_email(
            to=args.test,
            subject='Test Email',
            body='This is a test email from Email MCP Server.'
        )
        print(f"Test email result: {result}")
        return
    
    # MCP Server mode (stdio)
    print("Email MCP Server ready. Waiting for requests...", file=sys.stderr)
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get('method')
            params = request.get('params', {})
            
            if method == 'initialize':
                response = {
                    'jsonrpc': '2.0',
                    'id': request.get('id'),
                    'result': {
                        'protocolVersion': '2024-11-05',
                        'capabilities': {'tools': {}},
                        'serverInfo': {'name': 'email-mcp', 'version': '1.0.0'}
                    }
                }
            elif method == 'tools/list':
                response = {
                    'jsonrpc': '2.0',
                    'id': request.get('id'),
                    'result': {'tools': [
                        {'name': k, **v} for k, v in EmailMCPServer(email).tools.items()
                    ]}
                }
            elif method == 'tools/call':
                tool_name = params.get('name')
                tool_args = params.get('arguments', {})
                mcp = EmailMCPServer(email)
                result = mcp.handle_tool_call(tool_name, tool_args)
                response = {
                    'jsonrpc': '2.0',
                    'id': request.get('id'),
                    'result': {'content': [{'type': 'text', 'text': json.dumps(result)}]}
                }
            else:
                response = {
                    'jsonrpc': '2.0',
                    'id': request.get('id'),
                    'error': {'code': -32601, 'message': 'Method not found'}
                }
            
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            error_response = {
                'jsonrpc': '2.0',
                'id': request.get('id') if 'request' in dir() else None,
                'error': {'code': -32603, 'message': str(e)}
            }
            print(json.dumps(error_response), flush=True)


if __name__ == '__main__':
    main()
