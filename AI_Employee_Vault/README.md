# AI Employee Vault

Your personal AI employee's workspace - powered by Qwen Code.

## Quick Start

### 1. Start the File System Watcher

```bash
cd watchers
python filesystem_watcher.py .. ../DropFolder 30
```

This monitors the `DropFolder` for new files and creates action items in `Needs_Action/`.

### 2. Drop a File

Place any file in the `DropFolder/` directory. The watcher will:
- Detect the new file
- Create a Markdown action file in `Needs_Action/`
- Include suggested actions and metadata

### 3. Process with Qwen Code

Ask Qwen Code to:
- "Check the Needs_Action folder and process pending items"
- "Review the latest file drop and suggest next steps"
- "Update the Dashboard with current status"

### 4. Complete Tasks

After processing:
- Move completed action files to `Done/`
- The Dashboard will be updated automatically

---

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md           # Real-time summary (GUI)
├── Company_Handbook.md    # Rules of engagement
├── Business_Goals.md      # Q1 2026 objectives
├── Inbox/                 # Raw incoming items
├── Needs_Action/          # Items requiring processing
├── Done/                  # Completed tasks
├── Plans/                 # Multi-step task plans
├── Pending_Approval/      # Awaiting human approval
├── Approved/              # Approved actions
├── Rejected/              # Rejected actions
├── Accounting/            # Financial records
├── Briefings/             # CEO Briefings
├── DropFolder/            # Drop files here for processing
└── watchers/              # Python watcher scripts
```

---

## Bronze Tier Status ✅

**Completed:**
- ✅ Obsidian vault with Dashboard.md and Company_Handbook.md
- ✅ Working File System Watcher script
- ✅ Qwen Code integration ready
- ✅ Basic folder structure: /Inbox, /Needs_Action, /Done

**Verify:** `python watchers/verify_bronze.py`

---

## Watcher Commands

### Start Watcher (with watchdog - real-time)
```bash
python watchers/filesystem_watcher.py AI_Employee_Vault AI_Employee_Vault/DropFolder 30
```

### Start Watcher (polling mode)
```bash
# Watchdog not required - uses polling
python watchers/filesystem_watcher.py AI_Employee_Vault AI_Employee_Vault/DropFolder 60
```

### Test Installation
```bash
python watchers/verify_bronze.py AI_Employee_Vault
```

---

## Example Workflow

1. **Drop a file**: Save `invoice.pdf` to `DropFolder/`
2. **Watcher creates**: `Needs_Action/FILE_invoice_abc123.md`
3. **Qwen Code processes**: Reads the action file, analyzes the PDF
4. **Action taken**: Logs to Accounting, creates payment task
5. **Move to Done**: Action file moved to `Done/`
6. **Dashboard updated**: Summary refreshed

---

## Configuration

### Watcher Interval
Default: 30 seconds (polling mode)
```bash
python filesystem_watcher.py .. ../DropFolder 10  # 10 second interval
```

### Custom Watch Folder
```bash
python filesystem_watcher.py .. C:/Users/YourName/Documents/DropFolder 30
```

---

## Troubleshooting

### Watcher not detecting files
- Ensure file doesn't start with `.` (hidden files ignored)
- Check folder permissions
- Try increasing interval: `python filesystem_watcher.py .. ../DropFolder 60`

### Python errors
```bash
# Install dependencies
cd watchers
pip install -r requirements.txt
```

### Verify setup
```bash
python verify_bronze.py ..
```

---

## Next Steps (Silver Tier)

- [ ] Add Gmail Watcher
- [ ] Add WhatsApp Watcher
- [ ] Create MCP server for email sending
- [ ] Implement approval workflow
- [ ] Add scheduled tasks (cron/Task Scheduler)

---

*Built for the FTE-Hackathon-0: Personal AI Employee*
