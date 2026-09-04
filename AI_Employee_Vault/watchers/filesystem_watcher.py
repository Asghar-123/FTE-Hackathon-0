"""
File System Watcher - Monitors a drop folder for new files.

When files are added to the monitored folder, this watcher:
1. Detects the new file
2. Creates a Markdown action file in Needs_Action folder
3. Copies metadata about the file for processing

Usage:
    python filesystem_watcher.py /path/to/vault /path/to/watch [interval_seconds]
    
Example:
    python filesystem_watcher.py ../AI_Employee_Vault C:/Users/YourName/DropFolder 30
"""

import sys
import shutil
import hashlib
import time
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

# Use watchdog for efficient file system monitoring
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events for the drop folder."""
    
    def __init__(self, watcher, watch_folder: Path):
        self.watcher = watcher
        self.watch_folder = watch_folder
    
    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return
        
        source = Path(event.src_path)
        
        # Wait a moment for file to be fully written
        import time
        time.sleep(0.5)
        
        try:
            self.watcher.process_new_file(source)
        except Exception as e:
            self.watcher.logger.error(f'Error processing new file: {e}')


class FilesystemWatcher(BaseWatcher):
    """
    Watches a folder for new files and creates action files.
    
    This is the Bronze tier watcher - simple, reliable, and doesn't
    require external API credentials.
    """
    
    def __init__(self, vault_path: str, watch_folder: str, check_interval: int = 30):
        """
        Initialize the filesystem watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            watch_folder: Path to the folder to monitor for new files
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        self.watch_folder = Path(watch_folder)
        self.processed_files = set()
        
        # Ensure watch folder exists
        self.watch_folder.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f'Watching folder: {self.watch_folder}')
    
    def get_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of file for deduplication."""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return str(filepath.stat().st_mtime)
    
    def check_for_updates(self) -> list:
        """
        Check for new files in the watch folder.
        
        Returns:
            List of new file paths
        """
        new_files = []
        
        try:
            for filepath in self.watch_folder.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    file_hash = self.get_file_hash(filepath)
                    if file_hash not in self.processed_files:
                        new_files.append(filepath)
                        self.processed_files.add(file_hash)
        except Exception as e:
            self.logger.error(f'Error scanning watch folder: {e}')
        
        return new_files
    
    def process_new_file(self, filepath: Path):
        """Process a newly detected file immediately."""
        file_hash = self.get_file_hash(filepath)
        if file_hash not in self.processed_files:
            self.processed_files.add(file_hash)
            self.create_action_file(filepath)
    
    def create_action_file(self, filepath: Path) -> Path:
        """
        Create a Markdown action file for the new file.
        
        Args:
            filepath: Path to the new file
            
        Returns:
            Path to the created action file
        """
        try:
            stat = filepath.stat()
            timestamp = datetime.now().isoformat()
            
            # Generate unique ID from filename and timestamp
            file_id = hashlib.md5(f"{filepath.name}{timestamp}".encode()).hexdigest()[:8]
            
            # Determine file type based on extension
            file_type = filepath.suffix.lower().replace('.', '')
            type_category = self._categorize_file_type(file_type)
            
            content = f'''---
type: file_drop
category: {type_category}
original_name: {filepath.name}
file_type: {file_type}
size: {stat.st_size}
created: {timestamp}
source_folder: {self.watch_folder}
status: pending
---

# File Drop for Processing

## File Details
- **Original Name**: {filepath.name}
- **File Type**: {file_type.upper()}
- **Size**: {self._format_size(stat.st_size)}
- **Detected**: {timestamp}

## Suggested Actions
- [ ] Review file contents
- [ ] Process or take action
- [ ] Move original file if needed
- [ ] Mark as done when complete

## Notes
*Add notes about how to process this file.*

---
*Created by FilesystemWatcher*
'''
            
            # Create action file
            action_filename = f'FILE_{filepath.stem}_{file_id}.md'
            action_filepath = self.needs_action / action_filename
            action_filepath.write_text(content)
            
            self.logger.info(f'Created action file for: {filepath.name}')
            
            return action_filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise
    
    def _categorize_file_type(self, file_type: str) -> str:
        """Categorize file type for processing priority."""
        categories = {
            'pdf': 'document',
            'doc': 'document',
            'docx': 'document',
            'txt': 'document',
            'md': 'document',
            'xls': 'spreadsheet',
            'xlsx': 'spreadsheet',
            'csv': 'spreadsheet',
            'jpg': 'image',
            'jpeg': 'image',
            'png': 'image',
            'gif': 'image',
            'mp3': 'audio',
            'wav': 'audio',
            'mp4': 'video',
            'avi': 'video',
            'zip': 'archive',
            'rar': 'archive',
            '7z': 'archive',
        }
        return categories.get(file_type, 'other')
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def run_with_watchdog(self):
        """
        Run using watchdog for real-time file monitoring.
        More efficient than polling.
        """
        if not WATCHDOG_AVAILABLE:
            self.logger.warning('watchdog not installed, falling back to polling')
            self.run()
            return
        
        self.logger.info(f'Starting {self.__class__.__name__} with watchdog')
        self.logger.info(f'Watch folder: {self.watch_folder}')
        
        event_handler = DropFolderHandler(self, self.watch_folder)
        observer = Observer()
        observer.schedule(event_handler, str(self.watch_folder), recursive=False)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


def main():
    """Main entry point for running the watcher."""
    if len(sys.argv) < 3:
        print("Usage: python filesystem_watcher.py <vault_path> <watch_folder> [interval]")
        print("\nExample:")
        print("  python filesystem_watcher.py ../AI_Employee_Vault C:/Users/YourName/DropFolder 30")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    watch_folder = sys.argv[2]
    interval = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    watcher = FilesystemWatcher(vault_path, watch_folder, interval)
    
    print(f"\n👁️  Filesystem Watcher Started")
    print(f"   Vault: {vault_path}")
    print(f"   Watching: {watch_folder}")
    print(f"   Interval: {interval}s")
    print(f"\n   Press Ctrl+C to stop\n")
    
    # Try watchdog first, fall back to polling
    if WATCHDOG_AVAILABLE:
        watcher.run_with_watchdog()
    else:
        watcher.run()


if __name__ == '__main__':
    main()
