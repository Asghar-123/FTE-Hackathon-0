# 📧 Email Reply Workflow with Approval

## Overview

The AI Employee can now reply to emails with **human-in-the-loop approval**. Here's how it works:

```
┌─────────────────────────────────────────────────────────────────┐
│              Email Reply Workflow with Approval                 │
└─────────────────────────────────────────────────────────────────┘

1. GMAIL WATCHER DETECTS EMAIL
   ↓
2. CREATES ACTION FILE in Needs_Action/
   - Includes email content
   - Includes reply draft template
   ↓
3. HUMAN WRITES REPLY
   - Edit the draft in the action file
   - Move file to Pending_Approval/
   ↓
4. APPROVAL PROCESSOR SENDS EMAIL
   - Orchestrator detects approved file
   - Sends reply via Gmail API
   - Moves to Done/
   ↓
5. COMPLETE ✅
```

---

## Step-by-Step Guide

### Step 1: Gmail Watcher Detects Email

```bash
# Start Gmail Watcher
python watchers/gmail_watcher.py .. 30
```

When a new email arrives, the watcher creates an action file:

```
Needs_Action/
└── EMAIL_Hello_how_are_20260316_183504.md
```

### Step 2: Review and Draft Reply

Open the action file in Obsidian or any text editor:

```markdown
---
type: email
from: friend@example.com
subject: Hello how are you?
status: pending
requires_approval: reply
---

# Email Received

## Content
Hello how are you?

## Reply Draft (for approval)
**Reply To**: friend@example.com
**Subject**: Re: Hello how are you?

**Draft Response**:

Dear Sender,

[Type your response here]

Best regards,
[Your Name]
```

**Edit the draft response** with your reply:

```markdown
**Draft Response**:

Dear Friend,

I'm doing great, thank you for asking! How about you?

Let's catch up soon.

Best regards,
Your Name
```

### Step 3: Move to Pending_Approval

Once you've written your reply:

```bash
# Move file to approval folder
mv Needs_Action/EMAIL_Hello_how_are_*.md Pending_Approval/
```

Or in Windows:
```batch
move Needs_Action\EMAIL_Hello_how_are_*.md Pending_Approval\
```

### Step 4: Process Approved Replies

Run the orchestrator or email reply processor:

```bash
# Process all pending replies
python watchers/email_reply_processor.py .. --process

# Or run the full orchestrator
python watchers/orchestrator.py .. 30
```

### Step 5: Email Sent! ✅

The reply is sent via Gmail API and the action file is moved to `Done/`:

```
Done/
└── EMAIL_Hello_how_are_20260316_183504.md
```

The file includes a completion note:

```markdown
---
## Completed
- **Reply Sent**: 2026-03-16T18:45:00
- **Status**: Sent via Gmail API
```

---

## Quick Commands

```bash
# Start Gmail Watcher (monitors for new emails)
python watchers/gmail_watcher.py .. 30

# Process pending email replies
python watchers/email_reply_processor.py .. --process

# Run full automation (includes email processing)
python watchers/auto_employee.py ..
```

---

## Folder Workflow

```
Needs_Action/          ← New emails arrive here
    ↓ (edit reply draft)
Pending_Approval/      ← Move here when ready to send
    ↓ (auto-processed)
Approved/              ← Being processed
    ↓ (email sent)
Done/                  ← Reply sent successfully

Rejected/              ← If you change your mind
```

---

## Example Action File

```markdown
---
type: email
from: client@company.com
subject: Project Update Request
received: 2026-03-16T18:30:00
priority: high
status: pending
requires_approval: reply
---

# Email Received

## Details
- **From**: client@company.com
- **Subject**: Project Update Request
- **Received**: 2026-03-16 18:30:00

## Content
Hi, can you please send me the latest project update?

## Suggested Actions
- [ ] Read full email in Gmail
- [ ] Reply to sender (requires approval) ← Select this!
- [ ] Forward to relevant party
- [ ] Archive after processing

## Reply Draft (for approval)
*To reply, draft your response below and move this file to /Pending_Approval*

---
**Reply To**: client@company.com
**Subject**: Re: Project Update Request

**Draft Response**:

Dear Client,

Thank you for reaching out. I'm pleased to share the latest project update:

1. Phase 1: Completed ✅
2. Phase 2: In Progress (80% complete)
3. Phase 3: Scheduled for next week

I'll send the detailed report by end of day.

Best regards,
Your Name

---
*Created by GmailWatcher*
```

---

## Security & Approval

### What Requires Approval?

| Action | Approval Required |
|--------|-------------------|
| Email replies | ✅ Always |
| Payments > $100 | ✅ Yes |
| Social media posts | ✅ Yes |
| Internal tasks | ❌ No |

### Why Approval?

- **Prevents accidental sends** - You review every reply
- **Quality control** - Ensure tone and content are correct
- **Security** - No unauthorized emails sent
- **Audit trail** - All sent emails are logged

---

## Troubleshooting

### Email Not Sending

```bash
# Check if Gmail API is authenticated
python watchers/gmail_watcher.py .. --authenticate

# Check token exists
ls watchers/token.json
```

### Reply Not Processed

1. Ensure file is in `Pending_Approval/` (not `Needs_Action/`)
2. Check file has `requires_approval: reply` in frontmatter
3. Ensure draft response is between `**Draft Response**:` and `---`

### Gmail API Error

```bash
# Re-authenticate Gmail
python watchers/gmail_watcher.py .. --authenticate

# Delete token and re-authenticate
rm watchers/token.json
python watchers/gmail_watcher.py .. --authenticate
```

---

## Best Practices

1. **Review before approving** - Always read the draft before moving to Pending_Approval
2. **Keep drafts professional** - Remember this is business communication
3. **Include context** - Reference original email in your reply
4. **Test with yourself** - Send test emails to your other account first
5. **Monitor Done folder** - Verify replies are sent successfully

---

*Built for FTE-Hackathon-0: Personal AI Employee*
*Silver Tier - Email Reply with Approval*
