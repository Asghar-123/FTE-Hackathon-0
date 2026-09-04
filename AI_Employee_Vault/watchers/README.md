# AI Employee Watchers

Lightweight Python scripts that monitor external sources and create actionable Markdown files.

## Quick Start

### 1. Install Dependencies

```bash
cd watchers
pip install -r requirements.txt
```

### 2. Run the File System Watcher

```bash
# From the watchers folder
python filesystem_watcher.py ../AI_Employee_Vault ../DropFolder 30
```

Or from anywhere:

```bash
python AI_Employee_Vault/watchers/filesystem_watcher.py AI_Employee_Vault AI_Employee_Vault/DropFolder 30
```

### 3. Test by Dropping a File

1. Keep the watcher running
2. Drop any file into the `DropFolder`
3. Watch it create a `.md` file in `Needs_Action/`

## Available Watchers

### File System Watcher (Bronze Tier ✅)

Monitors a folder for new files and creates action items.

**Features:**
- Real-time monitoring with watchdog
- Automatic file categorization
- Deduplication (won't create duplicate actions)
- Human-readable action files

**Usage:**
```bash
python filesystem_watcher.py <vault_path> <watch_folder> [interval_seconds]
```

### Gmail Watcher (Silver Tier - Future)

Monitors Gmail for unread, important messages.

**Requirements:**
- Google Cloud project
- Gmail API credentials
- OAuth setup

### WhatsApp Watcher (Silver Tier - Future)

Monitors WhatsApp Web for urgent messages.

**Requirements:**
- Playwright installed
- WhatsApp Web session

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────────┐
│  External Source│────▶│   Watcher    │────▶│  Needs_Action/   │
│  (Gmail, Files) │     │  (Python)    │     │  (Markdown files)│
└─────────────────┘     └──────────────┘     └──────────────────┘
                                                      │
                                                      ▼
                                             ┌──────────────────┐
                                             │   Qwen Code      │
                                             │   (Processes)    │
                                             └──────────────────┘
```

## File Naming Convention

- `FILE_<name>_<id>.md` - File drop actions
- `EMAIL_<sender>_<id>.md` - Email actions (future)
- `WHATSAPP_<contact>_<id>.md` - WhatsApp actions (future)

## Troubleshooting

### Watcher not detecting files
- Check the watch folder path is correct
- Ensure file doesn't start with `.` (hidden files ignored)
- Try running with `-v` for verbose output

### Permission errors
- Ensure watcher has read access to watch folder
- Ensure watcher has write access to vault folder

### High CPU usage
- Increase check interval (default: 30s)
- Install `watchdog` for efficient event-based monitoring
