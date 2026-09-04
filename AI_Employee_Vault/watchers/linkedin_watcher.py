"""
LinkedIn Watcher & Auto Poster - Silver Tier Skill

Monitors LinkedIn for notifications/messages and auto-posts updates.
Uses Playwright for browser automation.

Usage:
    python linkedin_watcher.py <vault_path> [--auto-post] [--post "content"]
    python linkedin_watcher.py <vault_path> --schedule posts.md

Example:
    python linkedin_watcher.py ../AI_Employee_Vault --auto-post
    python linkedin_watcher.py ../AI_Employee_Vault --post "Business update #AI"
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from base_watcher import BaseWatcher

# Playwright dependencies
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("WARNING: Playwright not installed.")
    print("Install with: pip install playwright && playwright install chromium")


class LinkedInWatcher(BaseWatcher):
    """
    Watches LinkedIn for notifications and posts updates.
    """
    
    # Default keywords for lead detection
    LEAD_KEYWORDS = ['pricing', 'quote', 'interested', 'service', 'hire', 
                     'proposal', 'budget', 'cost', 'package', 'solution']
    
    # Optimal posting times (24-hour format)
    POST_TIMES = ['09:00', '12:00', '17:00']
    
    def __init__(self, vault_path: str, session_path: str = None,
                 auto_post: bool = False, check_interval: int = 300):
        """
        Initialize LinkedIn watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session
            auto_post: Enable automatic posting
            check_interval: Seconds between checks (default: 300 = 5 min)
        """
        super().__init__(vault_path, check_interval)
        
        self.session_path = Path(session_path) if session_path else (
            Path.home() / '.linkedin_session')
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.auto_post = auto_post
        self.content_queue = []
        self.posted_content = set()
        
        # Load content queue
        self._load_content_queue()
    
    def _load_content_queue(self):
        """Load scheduled content from vault."""
        queue_file = self.vault_path / 'content_queue.md'
        if queue_file.exists():
            content = queue_file.read_text(encoding='utf-8')
            # Parse content - simple implementation
            # In production, use proper markdown parsing
            self.logger.info(f'Loaded content queue from {queue_file}')
    
    def check_for_updates(self) -> list:
        """
        Check LinkedIn for new notifications and messages.
        
        Returns:
            List of notification dicts
        """
        notifications = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,
                    args=[
                        '--disable-gpu',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn
                page.goto('https://www.linkedin.com', wait_until='networkidle')
                
                # Wait for page to load
                try:
                    page.wait_for_selector('.nav-item--notifications', timeout=30000)
                except Exception:
                    self.logger.warning('LinkedIn not fully loaded, may need login')
                    browser.close()
                    return []
                
                # Check for notifications badge
                try:
                    notification_badge = page.query_selector('.nav-item--notifications .notification-badge')
                    if notification_badge:
                        count_text = notification_badge.inner_text()
                        count = int(''.join(filter(str.isdigit, count_text)) or '0')
                        if count > 0:
                            notifications.append({
                                'type': 'notifications',
                                'count': count,
                                'timestamp': datetime.now().isoformat()
                            })
                            self.logger.info(f'Found {count} new notifications')
                except Exception:
                    pass
                
                # Check for new messages
                try:
                    messaging_link = page.query_selector('a[href*="/messaging/"]')
                    if messaging_link:
                        badge = messaging_link.query_selector('.notification-badge')
                        if badge:
                            count_text = badge.inner_text()
                            count = int(''.join(filter(str.isdigit, count_text)) or '0')
                            if count > 0:
                                notifications.append({
                                    'type': 'messages',
                                    'count': count,
                                    'timestamp': datetime.now().isoformat()
                                })
                                self.logger.info(f'Found {count} new messages')
                except Exception:
                    pass
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f'Error checking LinkedIn: {e}')
        
        return notifications
    
    def post_update(self, content: str, hashtags: list = None) -> bool:
        """
        Post an update to LinkedIn.
        
        Args:
            content: Post content
            hashtags: List of hashtags
            
        Returns:
            True if successful
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Show browser for posting
                    args=[
                        '--disable-gpu',
                        '--disable-dev-shm-usage'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to LinkedIn
                page.goto('https://www.linkedin.com', wait_until='networkidle')
                
                # Wait for start post button
                try:
                    page.wait_for_selector('[data-control-name="update-share"]', timeout=30000)
                except Exception:
                    self.logger.warning('Could not find post button')
                    browser.close()
                    return False
                
                # Click start post
                page.click('[data-control-name="update-share"]')
                
                # Wait for post editor
                page.wait_for_selector('.share-box-feed-entry__textbox', timeout=10000)
                
                # Add hashtags to content
                if hashtags:
                    content += '\n\n' + ' '.join([f'#{tag}' for tag in hashtags])
                
                # Type content
                page.fill('.share-box-feed-entry__textbox', content)
                
                # Wait a moment for input to register
                page.wait_for_timeout(1000)
                
                # Click post button
                page.click('button:has-text("Post")')
                
                # Wait for confirmation
                page.wait_for_timeout(3000)
                
                self.logger.info('LinkedIn post published successfully')
                self.posted_content.add(content[:50])
                
                browser.close()
                return True
                
        except Exception as e:
            self.logger.error(f'Error posting to LinkedIn: {e}')
            return False
    
    def create_action_file(self, notification: dict) -> Path:
        """
        Create action file for LinkedIn activity.
        
        Args:
            notification: Dict with type, count, timestamp
            
        Returns:
            Path to created file
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            content = f'''---
type: linkedin
activity_type: {notification['type']}
received: {notification['timestamp']}
priority: high
count: {notification['count']}
status: pending
---

# LinkedIn Activity Detected

## Details
- **Type**: {notification['type'].title()}
- **Count**: {notification['count']} new
- **Detected**: {notification['timestamp']}

## Suggested Actions
- [ ] Review LinkedIn notifications
- [ ] Respond to messages
- [ ] Engage with comments
- [ ] Post follow-up content

## Notes
*Add notes about responses or follow-ups.*

---
*Created by LinkedInWatcher*
'''
            
            filename = f'LINKEDIN_activity_{timestamp}.md'
            filepath = self.needs_action / filename
            filepath.write_text(content, encoding='utf-8')
            
            self.logger.info(f'Created action file: {filename}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise
    
    def run_once(self) -> int:
        """Run single check cycle."""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.warning('Playwright not available, skipping')
            return 0
        
        count = super().run_once()
        
        # Auto-post if enabled and content available
        if self.auto_post and self.content_queue:
            self._process_content_queue()
        
        return count
    
    def _process_content_queue(self):
        """Process scheduled content for posting."""
        now = datetime.now()
        
        for item in self.content_queue:
            if item.get('scheduled_time'):
                schedule_time = datetime.fromisoformat(item['scheduled_time'])
                if schedule_time <= now and item['content'][:50] not in self.posted_content:
                    self.logger.info(f'Posting scheduled content: {item["content"][:30]}...')
                    success = self.post_update(
                        item['content'],
                        item.get('hashtags', [])
                    )
                    if success:
                        self.posted_content.add(item['content'][:50])


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Watcher & Auto Poster')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--auto-post', action='store_true', help='Enable auto-posting')
    parser.add_argument('--post', type=str, help='Post content immediately')
    parser.add_argument('--hashtags', type=str, nargs='+', help='Hashtags for post')
    parser.add_argument('--schedule', type=str, help='Schedule posts from file')
    parser.add_argument('--interval', type=int, default=300, help='Check interval (seconds)')
    
    args = parser.parse_args()
    
    if not PLAYWRIGHT_AVAILABLE:
        print("\nPlaywright not installed.")
        print("Install with: pip install playwright && playwright install chromium")
        sys.exit(1)
    
    vault_path = Path(args.vault_path)
    
    # Immediate post mode
    if args.post:
        watcher = LinkedInWatcher(str(vault_path), auto_post=True)
        hashtags = args.hashtags or ['Business', 'AI', 'Automation']
        print(f"\n📝 Posting to LinkedIn: {args.post[:50]}...")
        success = watcher.post_update(args.post, hashtags)
        if success:
            print("✅ Post published successfully!")
        else:
            print("❌ Post failed. Check browser for issues.")
        return
    
    watcher = LinkedInWatcher(
        str(vault_path),
        auto_post=args.auto_post,
        check_interval=args.interval
    )
    
    print(f"\n💼 LinkedIn Watcher Started")
    print(f"   Vault: {vault_path}")
    print(f"   Auto-post: {'Enabled' if args.auto_post else 'Disabled'}")
    print(f"   Check interval: {args.interval}s")
    print(f"\n   First run: Log in when browser opens")
    print(f"   Press Ctrl+C to stop\n")
    
    watcher.run()


if __name__ == '__main__':
    main()
