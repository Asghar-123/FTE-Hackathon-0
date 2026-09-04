---
name: linkedin-watcher
description: |
  Monitor LinkedIn for notifications, messages, and automatically post updates.
  Uses Playwright for browser automation to detect engagement and post content
  to LinkedIn for business growth and lead generation.
---

# LinkedIn Watcher & Auto Poster

Monitor LinkedIn and automatically post updates to generate business leads.

## Features

- **Auto Post**: Schedule and post content automatically
- **Engagement Monitoring**: Track likes, comments, notifications
- **Message Detection**: Monitor LinkedIn messages for leads
- **Content Scheduling**: Queue posts for optimal times
- **Analytics**: Track post performance

## Prerequisites

### Install Playwright

```bash
pip install playwright
playwright install chromium
```

### LinkedIn Account

- Have a LinkedIn account
- Keep session persistent (first run requires login)
- Follow LinkedIn's Terms of Service

## Usage

### Start LinkedIn Watcher

```bash
# Basic monitoring
python watchers/linkedin_watcher.py ../AI_Employee_Vault

# With auto-posting
python watchers/linkedin_watcher.py ../AI_Employee_Vault --auto-post

# Schedule posts from file
python watchers/linkedin_watcher.py ../AI_Employee_Vault --schedule posts.md
```

### First-Time Setup

1. Run the watcher
2. Browser opens LinkedIn login page
3. Log in to LinkedIn
4. Session is saved for future use

## Auto-Post Configuration

### Create Content Queue

Create `content_queue.md`:

```markdown
---
type: linkedin_posts
created: 2026-03-10
---

# LinkedIn Content Queue

## Post 1
**Content**: Excited to announce our new AI Employee automation service! 
#AI #Automation #Business

**Schedule**: 2026-03-11 09:00

## Post 2
**Content**: 5 tips for improving business productivity with AI...

**Schedule**: 2026-03-12 14:00
```

### Post via Command

```bash
# Post immediately
python watchers/linkedin_watcher.py ../AI_Employee_Vault \
  --post "Excited to announce our new AI Employee service! #AI #Automation"

# Schedule post
python watchers/linkedin_watcher.py ../AI_Employee_Vault \
  --schedule-post "Business tips..." --time "2026-03-11 09:00"
```

## Monitoring Features

### Notifications Monitored

- New connection requests
- Message notifications
- Post engagement (likes, comments)
- Profile views

### Keywords for Lead Detection

Configure keywords that indicate potential leads:
- "pricing"
- "quote"
- "interested"
- "service"
- "hire"

## Action File Format

When LinkedIn activity is detected:

```markdown
---
type: linkedin
activity_type: message
from: John Doe
received: 2026-03-10T16:00:00
priority: high
keywords: pricing, interested
---

# LinkedIn Activity

## Details
- **From**: John Doe
- **Type**: Message
- **Received**: 2026-03-10 16:00

## Content
Hi, I'm interested in your AI services. Can you share pricing?

## Suggested Actions
- [ ] Reply on LinkedIn
- [ ] Send pricing information
- [ ] Schedule call
- [ ] Mark as lead

---
*Created by LinkedInWatcher*
```

## Best Practices

### Posting Frequency

- **Recommended**: 1-2 posts per day
- **Maximum**: 5 posts per day
- **Optimal times**: 9 AM, 12 PM, 5 PM (weekday)

### Content Guidelines

- Keep posts professional
- Use 3-5 relevant hashtags
- Include engaging visuals when possible
- Respond to comments within 24 hours

### LinkedIn Compliance

⚠️ **Important**: 
- Follow LinkedIn's Terms of Service
- Don't spam or post excessively
- Use automation responsibly
- Consider LinkedIn's automation policies

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Login required | Session expired, re-login |
| Post failed | Check content length (< 3000 chars) |
| Browser crashes | Update Playwright |
| Rate limited | Reduce posting frequency |

## Example Output

```
2026-03-10 16:00:00 - LinkedInWatcher - INFO - Starting LinkedInWatcher
2026-03-10 16:00:05 - LinkedInWatcher - INFO - LinkedIn loaded
2026-03-10 16:00:30 - LinkedInWatcher - INFO - Found 2 new notifications
2026-03-10 16:00:30 - LinkedInWatcher - INFO - Created action file: LINKEDIN_John_Doe_160030.md
2026-03-10 16:01:00 - LinkedInWatcher - INFO - Posted update successfully
```
