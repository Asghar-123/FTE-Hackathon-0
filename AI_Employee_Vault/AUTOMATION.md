# 🤖 AI Employee - Full Automation Mode

## Overview

This is a **fully autonomous AI employee** that automatically processes files you drop into the system. No manual intervention required for low-risk tasks!

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    Full Automation Workflow                     │
└─────────────────────────────────────────────────────────────────┘

1. DROP A FILE
   Save any file to: DropFolder/

        ▼
2. WATCHER DETECTS (real-time with watchdog)
   - Monitors DropFolder/
   - Triggers immediately on new file

        ▼
3. ACTION FILE CREATED
   - Creates Needs_Action/FILE_name_*.md
   - Includes metadata and suggested actions

        ▼
4. ORCHESTRATOR PROCESSES
   - Reads action file
   - Calls Qwen Code for analysis
   - Determines if approval needed

        ▼
5. AUTO-APPROVAL CHECK
   ├─ Low-risk (notes, documents) → Process automatically
   └─ High-risk (payments, emails) → Move to Pending_Approval/

        ▼
6. EXECUTE & UPDATE
   - Qwen Code analyzes and summarizes
   - Dashboard.md updated automatically
   - Plan.md created for multi-step tasks

        ▼
7. MOVE TO DONE
   - Completed action file → Done/
   - Completion timestamp added
```

---

## Quick Start

### Option 1: One-Click Start (Windows)

```bash
# Double-click this file or run:
start-automation.bat
```

### Option 2: Manual Start

```bash
# Navigate to vault
cd AI_Employee_Vault

# Start full automation
python watchers\auto_employee.py .
```

### Option 3: Separate Watcher + Orchestrator

```bash
# Terminal 1: Start watcher
python watchers\filesystem_watcher.py . DropFolder 30

# Terminal 2: Start orchestrator
python watchers\orchestrator.py . 15
```

---

## Auto-Approval Rules

The system automatically approves low-risk tasks:

### ✅ Auto-Approved (No Human Intervention)
- File drops (documents, notes, txt files)
- Informational tasks
- Task summaries
- Meeting notes processing

### ⚠️ Requires Approval
- Payments over $100
- Sending emails
- Social media posts
- Deletions or cancellations
- Any action with keywords: "approve", "payment", "send", "post", "delete"

---

## Example Usage

### Example 1: Drop Meeting Notes

```bash
# 1. Create a file
echo "Meeting notes for Project Alpha" > DropFolder\meeting.txt

# 2. Automation processes it
# - Watcher detects file
# - Creates action file
# - Qwen Code summarizes
# - Moves to Done/
# - Updates Dashboard

# 3. Check results
cat Done\FILE_meeting_*.md
cat Dashboard.md
```

### Example 2: Drop Invoice (Requires Approval)

```bash
# 1. Drop an invoice
echo "Invoice: $500 for services" > DropFolder\invoice.pdf

# 2. System detects payment
# - Moves to Pending_Approval/
# - Creates approval request

# 3. Human reviews and approves
# - Move file from Pending_Approval/ to Approved/

# 4. System processes automatically
# - Executes payment workflow
# - Moves to Done/
```

---

## Folder Structure

```
AI_Employee_Vault/
├── start-automation.bat    # One-click starter
├── Dashboard.md            # Auto-updated summary
├── DropFolder/             # ← Drop files here!
├── Needs_Action/           # Pending processing
├── Done/                   # Completed tasks
├── Pending_Approval/       # Awaiting your approval
├── Approved/               # Approved (will be processed)
├── Rejected/               # Rejected tasks
├── Plans/                  # Multi-step task plans
├── Accounting/             # Financial records
├── Briefings/              # CEO briefings
└── watchers/
    ├── auto_employee.py    # Combined watcher + orchestrator
    ├── orchestrator.py     # Main automation logic
    ├── filesystem_watcher.py # File monitoring
    ├── base_watcher.py     # Base class
    └── verify_bronze.py    # Verification script
```

---

## Configuration

### Change Check Interval

```bash
# Default: 5 seconds
python watchers\orchestrator.py . 10  # Check every 10 seconds
```

### Disable Auto-Approval

Edit `watchers\orchestrator.py`:

```python
class AutoApprovalRules:
    REQUIRE_APPROVAL_TYPES = {'file_drop', 'payment', 'email_send', 'social_post'}
    # Now file_drop also requires approval
```

---

## Output Examples

### Action File Created

```markdown
---
type: file_drop
category: document
original_name: meeting_notes.txt
file_type: txt
size: 256
created: 2026-03-10T16:00:00
status: pending
---

# File Drop for Processing

## File Details
- **Original Name**: meeting_notes.txt
- **File Type**: TXT
- **Size**: 256.0 B
- **Detected**: 2026-03-10T16:00:00

## Suggested Actions
- [ ] Review file contents
- [ ] Process or take action
- [ ] Mark as done when complete
```

### Plan Generated (for multi-step tasks)

```markdown
---
type: plan
task: meeting_notes
created: 2026-03-10T16:00:00
status: in_progress
---

# Plan: meeting_notes

## Steps
1. [ ] Read meeting notes
2. [ ] Extract action items
3. [ ] Create follow-up tasks
4. [ ] Schedule next meeting

## Progress
- Started: 2026-03-10T16:00:00
- Completed: -
- Steps Done: 0/4
```

### Dashboard Updated

```markdown
## ✅ Today's Completed Tasks
- [x] FILE_meeting_notes_abc123.md
- [x] FILE_invoice_def456.md

## 📥 Inbox Status
- **Needs Action**: 0
- **Pending Approval**: 1
```

---

## Troubleshooting

### Qwen Code Not Found

```bash
# Check installation
qwen --version

# Reinstall if needed
npm install -g @anthropic/qwen-code
```

### Watcher Not Detecting Files

```bash
# Install watchdog for real-time detection
pip install watchdog

# Or increase polling interval
python watchers\filesystem_watcher.py . DropFolder 60
```

### Dashboard Not Updating

Check orchestrator logs:
```
2026-03-10 16:00:00 - Orchestrator - INFO - Dashboard updated
```

If no logs, orchestrator might not be running.

### High CPU Usage

Increase check interval:
```bash
python watchers\orchestrator.py . 30  # Check every 30 seconds
```

---

## Stopping Automation

Press `Ctrl+C` in the terminal where automation is running.

---

## Next Steps

After automation is running:

1. **Drop files** into `DropFolder/`
2. **Watch logs** for processing status
3. **Check Dashboard.md** for updates
4. **Review Pending_Approval/** for tasks needing your input
5. **Move approved tasks** from `Pending_Approval/` to `Approved/`

---

*Built for FTE-Hackathon-0: Personal AI Employee*
