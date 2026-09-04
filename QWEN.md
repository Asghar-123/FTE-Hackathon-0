# FTE-Hackathon-0: Personal AI Employee

## Project Overview

This is a **hackathon project** for building a "Digital FTE" (Full-Time Equivalent) — an autonomous AI employee that manages personal and business affairs 24/7. The project uses **Qwen Code** as the reasoning engine and **Obsidian** (local Markdown) as the knowledge base/dashboard.

**Tagline:** *Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.*

### Architecture

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Qwen Code | Reasoning engine, task execution |
| **Memory/GUI** | Obsidian | Dashboard, long-term memory (local Markdown) |
| **Senses** | Python Watchers | Monitor Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | External actions (email, browser automation, payments) |
| **Persistence** | Ralph Wiggum Loop | Stop hook for autonomous multi-step task completion |

### Key Features

- **Watcher Architecture**: Lightweight Python scripts monitor inputs and create actionable `.md` files in `/Needs_Action`
- **Human-in-the-Loop**: Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Monday Morning CEO Briefing**: Autonomous weekly audit generating revenue reports, bottleneck analysis, and proactive suggestions
- **Browser Automation**: Playwright MCP for web interactions (form filling, data extraction, screenshots)

---

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Qwen Code](https://github.com/QwenLM/qwen-code) | Latest | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |
| [Node.js](https://nodejs.org/) | v24+ LTS | MCP servers & automation |
| [GitHub Desktop](https://desktop.github.com/download/) | Latest | Version control |

### Hardware Requirements

- **Minimum**: 8GB RAM, 4-core CPU, 20GB free disk space
- **Recommended**: 16GB RAM, 8-core CPU, SSD storage

### Setup Commands

```bash
# 1. Create Obsidian vault
mkdir AI_Employee_Vault
cd AI_Employee_Vault
mkdir Inbox Needs_Action Done Plans Pending_Approval Approved

# 2. Verify Qwen Code
qwen --version

# 3. Start Playwright MCP Server (for browser automation)
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# 4. Verify Playwright server
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py

# 5. Stop Playwright server (when done)
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### Playwright MCP Commands

```bash
# Navigate to URL
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Get page snapshot (accessibility tree)
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_snapshot -p '{}'

# Click element
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_click \
  -p '{"element": "Submit button", "ref": "e42"}'

# Take screenshot
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_take_screenshot \
  -p '{"type": "png", "fullPage": true}'
```

### Ralph Wiggum Loop (Autonomous Execution)

```bash
# Start autonomous loop
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

---

## Development Conventions

### Folder Structure

```
AI_Employee_Vault/
├── Inbox/              # Raw incoming items
├── Needs_Action/       # Items requiring processing
├── In_Progress/        # Items being worked on (claim-by-move rule)
├── Pending_Approval/   # Actions awaiting human approval
├── Approved/           # Approved actions (triggers execution)
├── Rejected/           # Rejected actions
├── Done/               # Completed tasks
├── Plans/              # Generated plans (Plan.md)
├── Briefings/          # CEO Briefings (weekly reports)
├── Accounting/         # Bank transactions, invoices
├── Dashboard.md        # Real-time summary
└── Company_Handbook.md # Rules of engagement
```

### File Naming Conventions

- **Action Files**: `TYPE_Description_Date.md` (e.g., `EMAIL_ClientA_2026-01-07.md`)
- **Approval Files**: `APPROVAL_REQUIRED_Action_Description.md`
- **Briefings**: `YYYY-MM-DD_Day_Briefing.md`

### YAML Frontmatter Schema

All `.md` files should include structured metadata:

```yaml
---
type: email|whatsapp|payment|task|approval_request
from: Sender Name
subject: Subject Line
received: 2026-01-07T10:30:00Z
priority: high|medium|low
status: pending|in_progress|completed|approved|rejected
---
```

### Watcher Pattern

All Watcher scripts follow the `BaseWatcher` abstract class:

```python
from base_watcher import BaseWatcher

class GmailWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass

    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass
```

### Human-in-the-Loop Pattern

For sensitive actions, Qwen Code writes an approval request instead of acting:

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
status: pending
---

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

---

## Hackathon Tiers

| Tier | Time | Deliverables | Status |
|------|------|--------------|--------|
| **Bronze** | 8-12h | Obsidian vault, 1 Watcher, Qwen Code reading/writing | ✅ **COMPLETE** |
| **Silver** | 20-30h | 2+ Watchers, Plan.md generation, 1 MCP server, HITL workflow | ⏳ Pending |
| **Gold** | 40+h | Full integration, Odoo MCP, Weekly Audit, Ralph Wiggum loop | ⏳ Pending |
| **Platinum** | 60+h | Cloud deployment, Cloud/Local split, Vault sync, A2A upgrade | ⏳ Pending |

---

## Bronze Tier - Completed Deliverables

### ✅ Vault Structure
```
AI_Employee_Vault/
├── Dashboard.md           # Real-time summary
├── Company_Handbook.md    # Rules of engagement
├── Business_Goals.md      # Q1 2026 objectives
├── README.md              # Quick start guide
├── start-watcher.bat      # Windows quick start
├── Inbox/
├── Needs_Action/
├── Done/
├── Plans/
├── Pending_Approval/
├── Approved/
├── Rejected/
├── Accounting/
├── Briefings/
├── DropFolder/            # Drop files here
└── watchers/              # Python scripts
```

### ✅ File System Watcher
- **Location**: `AI_Employee_Vault/watchers/filesystem_watcher.py`
- **Features**: Real-time monitoring, auto-categorization, deduplication
- **Start**: `python watchers/filesystem_watcher.py .. DropFolder 30`
- **Verify**: `python watchers/verify_bronze.py ..`

### ✅ Documentation
- Dashboard.md with real-time summary template
- Company_Handbook.md with Rules of Engagement
- Business_Goals.md with Q1 2026 objectives
- README.md with quick start guide

---

## Resources

- **Main Documentation**: `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Playwright Tools**: `.qwen/skills/browsing-with-playwright/references/playwright-tools.md`
- **Zoom Meeting**: Wednesdays 10:00 PM (ID: 871 8870 7642, Passcode: 744832)
- **YouTube**: https://www.youtube.com/@panaversity

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Watcher not detecting files | Ensure file doesn't start with `.` (hidden files ignored) |
| Watcher not starting | Run `pip install -r watchers/requirements.txt` |
| Playwright server not responding | `bash scripts/stop-server.sh && bash scripts/start-server.sh` |
| Element not found | Run `browser_snapshot` first to get current refs |
| Click fails | Try `browser_hover` first, then click |
| Ralph loop exits early | Check completion promise or file movement to `/Done` |

---

## Quick Start (Bronze Tier)

```bash
# 1. Navigate to vault
cd AI_Employee_Vault

# 2. Start the watcher (Windows)
start-watcher.bat

# Or start manually (any OS)
python watchers/filesystem_watcher.py . DropFolder 30

# 3. Drop a file into DropFolder/
# Watcher creates action file in Needs_Action/

# 4. Ask Qwen Code to process
# "Check Needs_Action folder and process pending items"

# 5. Verify Bronze tier completion
python watchers/verify_bronze.py .
```
