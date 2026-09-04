# 🚀 Silver Tier - Quick Start Guide

## One Command to Run Everything

```bash
cd D:\hackathonAI0\FTE-Hackathon-0\AI_Employee_Vault\watchers

# Run full automation
python auto_employee.py ..
```

That's it! This single command handles:
- ✅ Processing Gmail emails (when gmail_watcher is running)
- ✅ Processing files in DropFolder
- ✅ Sending approved email replies
- ✅ Updating Dashboard
- ✅ Creating plans for complex tasks
- ✅ Processing approvals

---

## Email Reply Workflow (Automatic!)

### Step 1: Gmail Watcher Detects Email
```bash
# In a separate terminal (optional - for real-time email detection)
python gmail_watcher.py .. 30
```

### Step 2: Edit Reply Draft
Open the action file in `Needs_Action/`:

```markdown
**Draft Response**:

Dear Sender,

[TYPE YOUR REPLY HERE]  ← Just edit this part!

Best regards,
Your Name
```

### Step 3: Move to Pending_Approval
```bash
# Move the file to approve
mv Needs_Action/EMAIL_*.md Pending_Approval/
```

### Step 4: System Sends Automatically! ✅

The `auto_employee.py` script (running every 30 seconds) will:
1. Detect the file in `Pending_Approval/`
2. Send the email via Gmail API
3. Move it to `Done/`
4. Update Dashboard

**No extra commands needed!**

---

## Folder Structure

```
Needs_Action/       ← New emails and tasks arrive here
    ↓ (edit reply draft)
Pending_Approval/   ← Move here to approve
    ↓ (auto-processed every 30s)
Done/               ← Completed!

DropFolder/         ← Drop files here for processing
```

---

## Commands Reference

### Full Automation (Run This!)
```bash
python auto_employee.py ..
```

### Gmail Watcher (Optional - for real-time email detection)
```bash
python gmail_watcher.py .. 30
```

### Process Email Replies Only
```bash
python email_reply_processor.py .. --process
```

### Verify Silver Tier
```bash
python verify_silver.py ..
```

---

## What Happens Automatically

| Event | Automatic Action |
|-------|------------------|
| New email detected | Creates action file in Needs_Action/ |
| File dropped in DropFolder/ | Creates action file |
| File moved to Pending_Approval/ | Sends email reply (within 30s) |
| Task completed | Moves to Done/ |
| Every 30 seconds | Updates Dashboard.md |
| Complex task detected | Creates Plan.md |

---

## Example: Reply to an Email

```bash
# 1. Start automation (keep this running)
python auto_employee.py ..

# 2. In another terminal, start Gmail watcher
python gmail_watcher.py .. 30

# 3. When email arrives, you'll see:
#    ✓ Created: EMAIL_Testing_20260316_*.md

# 4. Open the file and edit the draft:
#    nano Needs_Action/EMAIL_Testing_*.md
#    [Type your reply]

# 5. Move to approve:
#    mv Needs_Action/EMAIL_Testing_*.md Pending_Approval/

# 6. Within 30 seconds, email is sent! ✅
#    File moved to Done/
```

---

## Troubleshooting

### Email Not Sending
```bash
# Check if file is in correct folder
ls Pending_Approval/

# Manually process
python email_reply_processor.py .. --process
```

### Gmail Not Connected
```bash
# Re-authenticate
python gmail_watcher.py .. --authenticate
```

### Dashboard Not Updating
```bash
# The auto_employee script updates every 30 seconds
# Just wait or restart:
python auto_employee.py ..
```

---

## Status Check

```bash
# Check pending emails
ls Pending_Approval/EMAIL_*.md

# Check completed
ls Done/

# Check Dashboard
cat Dashboard.md
```

---

*Silver Tier - Gmail + LinkedIn + Email Replies*
*Built for FTE-Hackathon-0*
