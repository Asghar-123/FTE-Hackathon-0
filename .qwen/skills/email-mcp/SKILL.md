---
name: email-mcp
description: |
  Email MCP Server - Send, draft, and manage emails via SMTP or Gmail API.
  Provides MCP (Model Context Protocol) server for Qwen Code to send emails,
  create drafts, and search email archives. Supports both SMTP and Gmail API.
---

# Email MCP Server

MCP server for email operations - send, draft, search emails.

## Features

- **Send Emails**: Send emails via SMTP or Gmail API
- **Create Drafts**: Save email drafts without sending
- **Search Emails**: Search sent/received emails
- **Attachments**: Support for file attachments
- **HTML/Plain Text**: Support both formats

## Prerequisites

### Option 1: SMTP (Any Email Provider)

```bash
# You need:
# - SMTP server address
# - SMTP port
# - Username (email)
# - Password (or app-specific password)
```

### Option 2: Gmail API

```bash
# You need:
# - Google Cloud project
# - Gmail API enabled
# - OAuth2 credentials (credentials.json)
```

## Installation

```bash
# Install dependencies
pip install smtplib email google-api-python-client google-auth-httplib2 google-auth-oauthlib

# For MCP server
pip install mcp
```

## Usage

### Start MCP Server

```bash
# Using SMTP
python watchers/email_mcp_server.py --smtp smtp.gmail.com --port 587 \
  --user your@gmail.com --password your-app-password

# Using Gmail API
python watchers/email_mcp_server.py --gmail-api --credentials credentials.json
```

### MCP Server Configuration

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "email": {
      "command": "python",
      "args": [
        "C:/path/to/email_mcp_server.py",
        "--smtp", "smtp.gmail.com",
        "--port", "587",
        "--user", "your@gmail.com",
        "--password", "your-app-password"
      ]
    }
  }
}
```

## Tools

### send_email

Send an email immediately.

**Parameters:**
```json
{
  "to": "recipient@example.com",
  "subject": "Hello",
  "body": "Email content",
  "html": false,
  "attachments": []
}
```

### create_draft

Create a draft email (don't send).

**Parameters:**
```json
{
  "to": "recipient@example.com",
  "subject": "Hello",
  "body": "Email content"
}
```

### search_emails

Search emails in sent/received folders.

**Parameters:**
```json
{
  "query": "from:boss subject:meeting",
  "max_results": 10
}
```

### get_email

Get a specific email by ID.

**Parameters:**
```json
{
  "email_id": "message_id_123"
}
```

## Examples

### Example 1: Send Email via Qwen Code

```bash
qwen "Use the email MCP server to send an email to client@example.com 
with subject 'Project Update' and body 'The project is on track.'"
```

### Example 2: Create Draft

```bash
qwen "Create a draft email to team@company.com with subject 'Meeting Tomorrow' 
but don't send it yet"
```

### Example 3: Search Emails

```bash
qwen "Search my emails for messages from John about the budget"
```

## Security

### App-Specific Password (Gmail)

If using Gmail with 2FA:

1. Go to Google Account settings
2. Security → 2-Step Verification
3. App passwords → Generate
4. Use the generated password (not your regular password)

### Environment Variables

Store credentials securely:

```bash
# .env file (never commit to git)
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USER=your@gmail.com
EMAIL_PASSWORD=your-app-password
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Use app-specific password for Gmail |
| Connection timeout | Check SMTP server and port |
| Port blocked | Try port 465 (SSL) or 587 (TLS) |
| Gmail API error | Enable Gmail API in Google Cloud Console |
