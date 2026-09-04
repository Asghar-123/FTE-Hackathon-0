---
name: whatsapp-watcher
description: |
  Monitor WhatsApp Web for new messages containing urgent keywords.
  Uses Playwright for browser automation to detect messages and create action files.
  Requires WhatsApp Web session and Playwright installation.
---

# WhatsApp Watcher

Monitor WhatsApp Web for urgent messages and create action files automatically.

## Prerequisites

### 1. Install Playwright

```bash
# Install Playwright
pip install playwright

# Install browser binaries
playwright install chromium
```

### 2. WhatsApp Web Access

- Have WhatsApp installed on your phone
- Be able to scan QR code for WhatsApp Web authentication
- Keep browser session persistent

## Usage

### Start WhatsApp Watcher

```bash
# Basic usage
python watchers/whatsapp_watcher.py ../AI_Employee_Vault

# With custom session path
python watchers/whatsapp_watcher.py ../AI_Employee_Vault --session-path ./whatsapp_session

# With custom keywords
python watchers/whatsapp_watcher.py ../AI_Employee_Vault --keywords "urgent,asap,help,payment"
```

### First-Time Setup

1. Run the watcher
2. Browser window opens with WhatsApp Web QR code
3. Scan QR code with your phone
4. Session is saved for future use

## Configuration

### Watched Keywords

Default keywords that trigger action file creation:
- `urgent`
- `asap`
- `invoice`
- `payment`
- `help`

Customize in code or via `--keywords` flag.

### Check Interval

Default: 30 seconds (to catch urgent messages quickly)

```bash
python watchers/whatsapp_watcher.py ../AI_Employee_Vault 60  # Check every 60 seconds
```

## Action File Format

When an urgent message is detected:

```markdown
---
type: whatsapp
from: +1234567890
contact_name: John Doe
received: 2026-03-10T16:00:00
priority: high
status: pending
keywords: urgent, payment
---

# WhatsApp Message Received

## Details
- **From**: John Doe (+1234567890)
- **Received**: 2026-03-10 16:00:00
- **Keywords Detected**: urgent, payment

## Message Content
[Message text]

## Suggested Actions
- [ ] Reply on WhatsApp
- [ ] Take action on request
- [ ] Mark as done when complete

## Notes
*Add notes about response.*

---
*Created by WhatsAppWatcher*
```

## Running in Background

### Windows (Task Scheduler)

```batch
schtasks /create /tn "WhatsAppWatcher" /tr "python C:\path\to\whatsapp_watcher.py C:\path\to\vault" /sc onlogon
```

### Linux/Mac (systemd)

```ini
# /etc/systemd/system/whatsapp-watcher.service
[Unit]
Description=WhatsApp Watcher
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/vault
ExecStart=/usr/bin/python3 /path/to/whatsapp_watcher.py /path/to/vault
Restart=always

[Install]
WantedBy=multi-user.target
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| QR code not showing | Clear session folder, restart watcher |
| Session expired | Delete session folder, re-scan QR |
| No messages detected | Check keywords, verify WhatsApp Web is loaded |
| Browser crashes | Update Playwright: `pip install --upgrade playwright` |

## Security Notes

- Session data is stored locally
- Never commit session files to git
- Use dedicated phone number for business if possible
- Review WhatsApp Terms of Service for automation

## Important Notes

⚠️ **WhatsApp Web Automation Warning:**
- This uses browser automation which may violate WhatsApp's Terms of Service
- Use at your own risk
- Consider using official WhatsApp Business API for production use
- Keep check intervals reasonable (not too frequent)

## Example Output

```
2026-03-10 16:00:00 - WhatsAppWatcher - INFO - Starting WhatsAppWatcher
2026-03-10 16:00:05 - WhatsAppWatcher - INFO - WhatsApp Web loaded
2026-03-10 16:00:30 - WhatsAppWatcher - INFO - Found 1 urgent message
2026-03-10 16:00:30 - WhatsAppWatcher - INFO - Created action file: WHATSAPP_John_Doe_160030.md
```
