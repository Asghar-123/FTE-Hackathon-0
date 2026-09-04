---
name: twitter-integration
description: |
  Post messages to Twitter (X) and monitor feed activity using Playwright browser automation.
  Includes automated posting and activity reporting in Obsidian.
---

# Twitter (X) Integration

Automate your Twitter activity using Playwright browser automation.

## Prerequisites

### 1. Manual Login
Run the watcher once with the `--login` flag to authenticate your session:
```bash
python watchers/twitter_watcher.py AI_Employee_Vault --login
```

## Usage

### Start Twitter Watcher
```bash
python watchers/twitter_watcher.py AI_Employee_Vault
```

### Post Immediately
```bash
python watchers/twitter_watcher.py AI_Employee_Vault --post "Tweeting from my AI Employee! #Automation #GoldTier"
```

## Features
- **Browser Automation**: Direct interaction with x.com, bypassing API requirements.
- **Session Persistence**: Login once, automate forever (saved in `~/.twitter_session`).
- **Audit Integration**: Feeds into the Weekly CEO Briefing automatically.

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Element Not Found | Twitter UI updated; update selectors in `twitter_watcher.py` |
| Session Expired | Re-run with `--login` to refresh authentication |
