---
name: gmail-watcher
description: |
  Monitor Gmail for new unread/important emails and create action files in Obsidian vault.
  Automatically detects new emails and creates Markdown files in Needs_Action folder for processing.
  Requires Gmail API credentials setup.
---

# Gmail Watcher

Monitor Gmail and create action files for new emails automatically.

## Prerequisites

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`

### 2. Install Dependencies

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 3. First-Time Authentication

```bash
python watchers/gmail_watcher.py --authenticate
```

## Usage

### Start Gmail Watcher

```bash
# Basic usage
python watchers/gmail_watcher.py ../AI_Employee_Vault

# With custom check interval (seconds)
python watchers/gmail_watcher.py ../AI_Employee_Vault 120

# Authenticate first
python watchers/gmail_watcher.py ../AI_Employee_Vault --authenticate
```

### Run as Background Service

```bash
# Windows (Task Scheduler)
schtasks /create /tn "GmailWatcher" /tr "python C:\path\to\gmail_watcher.py C:\path\to\vault" /sc onlogon

# Linux/Mac (cron)
crontab -e
# Add: */2 * * * * python /path/to/gmail_watcher.py /path/to/vault
```

## Configuration

### Gmail API Scopes

The watcher uses these scopes:
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails

### Environment Variables

```bash
# Set in .env file or environment
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_TOKEN_PATH=/path/to/token.json
```

## Action File Format

When an email is detected, creates:

```markdown
---
type: email
from: sender@example.com
subject: Important: Project Update
received: 2026-03-10T16:00:00
priority: high
status: pending
---

# Email Content

[Email body text]

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

## Filtering Options

Edit `gmail_watcher.py` to customize filters:

```python
# Only important unread emails
query = 'is:unread is:important'

# Or customize:
query = 'is:unread from:boss@company.com'  # Only from boss
query = 'is:unread has:attachment'  # With attachments
query = 'is:unread subject:invoice'  # Subject contains
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Re-run `--authenticate` |
| No emails detected | Check Gmail API query filter |
| Token expired | Delete `token.json`, re-authenticate |
| API quota exceeded | Wait 24 hours or upgrade quota |

## Security Notes

- Never commit `token.json` or `credentials.json` to git
- Store credentials securely
- Use app-specific passwords if 2FA enabled
- Review Gmail API permissions regularly

## Example Output

```
2026-03-10 16:00:00 - GmailWatcher - INFO - Starting GmailWatcher
2026-03-10 16:00:00 - GmailWatcher - INFO - Vault path: ../AI_Employee_Vault
2026-03-10 16:02:00 - GmailWatcher - INFO - Found 2 new emails
2026-03-10 16:02:00 - GmailWatcher - INFO - Created action file: EMAIL_18a3b2c4d5e6f7g8.md
2026-03-10 16:02:00 - GmailWatcher - INFO - Created action file: EMAIL_29b4c3d5e6f7g8h9.md
```
