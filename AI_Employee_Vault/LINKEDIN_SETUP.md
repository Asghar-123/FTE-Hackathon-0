# 🟦 LinkedIn Automation Setup Guide

## ✅ Installation Complete

- ✅ Playwright installed
- ✅ Chromium browser installed
- ✅ LinkedIn watcher script ready

## Quick Start

### 1. Test LinkedIn Connection

```bash
cd AI_Employee_Vault\watchers
python linkedin_watcher.py ..
```

**First Run:**
- Browser will open
- LinkedIn.com will load
- **You must log in manually**
- Session will be saved for future runs

### 2. Auto-Post to LinkedIn

```bash
# Post immediately
python linkedin_watcher.py .. --post "Excited to announce our new AI Employee automation system! #AI #Automation #Productivity"
```

### 3. Monitor LinkedIn

```bash
# Start monitoring (checks every 5 minutes)
python linkedin_watcher.py .. 300
```

## Content Queue Format

Create `content_queue.md` in vault root:

```markdown
---
type: linkedin_posts
---

# LinkedIn Content Queue

## Post 1
**Content**: Just completed Silver Tier of AI Employee hackathon! Built an autonomous email reply system.
**Hashtags**: AI, Automation, Productivity
**Schedule**: 2026-03-17 14:00

## Post 2
**Content**: 5 tips for automating your business communications...
**Hashtags**: Business, Tips, Automation
**Schedule**: 2026-03-18 09:00
```

## Features

| Feature | Status |
|---------|--------|
| Post to LinkedIn | ✅ Ready |
| Monitor notifications | ✅ Ready |
| Detect lead messages | ✅ Ready |
| Auto-reply to messages | ⏳ Manual approval |
| Schedule posts | ✅ Ready |

## Best Practices

### Posting Frequency
- **Recommended**: 1-2 posts per day
- **Maximum**: 5 posts per day
- **Optimal times**: 9 AM, 12 PM, 5 PM

### Content Guidelines
- Keep posts professional
- Use 3-5 relevant hashtags
- Engage with comments within 24 hours
- Follow LinkedIn's Terms of Service

## ⚠️ Important Warning

**LinkedIn Automation Risks:**
- Automated posting may violate LinkedIn's Terms of Service
- Use responsibly and at your own risk
- Don't post excessively (max 1-2 times/day)
- Consider using LinkedIn API for production use

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Browser doesn't open | Run `playwright install chromium` again |
| Login required every time | Check session folder exists |
| Post failed | Check content length (< 3000 chars) |
| Rate limited | Reduce posting frequency |

## Test Commands

```bash
# Test connection (opens LinkedIn)
python linkedin_watcher.py ..

# Test posting
python linkedin_watcher.py .. --post "Test post from AI Employee #Testing"

# Monitor for leads
python linkedin_watcher.py .. --monitor-leads
```

---
*Built for FTE-Hackathon-0 Silver Tier*
