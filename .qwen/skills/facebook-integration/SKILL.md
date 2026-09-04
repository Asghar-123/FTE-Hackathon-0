---
name: facebook-integration
description: |
  Post messages to Facebook using Playwright browser automation.
  Handles session-based posting (no API keys required).
---

# Facebook Integration (Playwright)

Automate your Facebook activity using browser automation.

## Prerequisites

### 1. Install Playwright
```bash
pip install playwright
playwright install chromium
```

### 2. Manual Login
The first time you run the script, it will use a persistent browser context in `~/.facebook_session`. You must manually log in if the session is not yet authenticated.

## Usage

### Start Facebook Watcher
```bash
python watchers/facebook_watcher.py AI_Employee_Vault
```

### Post to Facebook Immediately
```bash
python watchers/facebook_watcher.py AI_Employee_Vault --post "Hello from my AI Employee via Playwright!"
```

## How it Works
1.  **Session-Based**: Uses Playwright to launch a browser with your existing Facebook session.
2.  **No Graph API**: Bypasses the need for App IDs, Secrets, or Page Access Tokens.
3.  **Human-like**: Interacts with the Facebook UI elements directly.

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Element Not Found | Facebook UI changed; update selectors in `facebook_watcher.py` |
| Not Logged In | Run once without `--post` and log in manually in the browser window |
| Playwright Error | Ensure you ran `playwright install chromium` |
