"""
WhatsApp Watcher - Silver Tier Skill

Monitors WhatsApp Web for urgent messages and creates action files.
Uses Playwright for browser automation.

Usage:
    python whatsapp_watcher.py <vault_path> [check_interval_seconds]
    python whatsapp_watcher.py <vault_path> --login
    python whatsapp_watcher.py <vault_path> --keywords "urgent,asap,help"
"""

import sys
import logging
import time
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

# Playwright dependencies
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class WhatsAppWatcher(BaseWatcher):
    DEFAULT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency']
    
    def __init__(self, vault_path: str, session_path: str = None,
                 keywords: list = None, check_interval: int = 30):
        super().__init__(vault_path, check_interval)
        self.session_path = Path(session_path) if session_path else (Path.home() / '.whatsapp_session')
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.keywords = keywords or self.DEFAULT_KEYWORDS

    def open_login_window(self):
        """Opens a visible browser to scan WhatsApp QR code."""
        with sync_playwright() as p:
            print("Opening WhatsApp Web for QR Scan...")
            browser = p.chromium.launch_persistent_context(
                str(self.session_path), 
                headless=False,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )
            page = browser.pages[0]
            page.goto('https://web.whatsapp.com')
            print("---")
            print("PLEASE SCAN THE QR CODE.")
            print("Once your chats load, CLOSE THIS WINDOW to save the session.")
            print("---")
            while len(browser.pages) > 0:
                time.sleep(1)
            print("WhatsApp session saved successfully.")

    def check_for_updates(self) -> list:
        messages = []
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(str(self.session_path), headless=True)
                page = browser.pages[0]
                page.goto('https://web.whatsapp.com', wait_until='load')
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=20000)
                except:
                    self.logger.warning('WhatsApp Web not loaded (QR scan needed?)')
                    browser.close()
                    return []
                
                unread_chats = page.query_selector_all('[aria-label*="unread"]')
                for chat in unread_chats:
                    try:
                        chat_name = chat.query_selector('[dir="auto"]').inner_text()
                        message_text = chat.query_selector('span[dir="auto"]').inner_text().lower()
                        matched = [kw for kw in self.keywords if kw in message_text]
                        if matched:
                            messages.append({
                                'chat_name': chat_name,
                                'text': message_text,
                                'keywords': matched,
                                'timestamp': datetime.now().isoformat()
                            })
                    except: continue
                browser.close()
        except Exception as e: self.logger.error(f'Error: {e}')
        return messages

    def create_action_file(self, message: dict) -> Path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        content = f"---\ntype: whatsapp\nfrom: {message['chat_name']}\nstatus: pending\n---\n# WhatsApp Message\n{message['text']}"
        filename = f'WHATSAPP_{timestamp}.md'
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')
        return filepath

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('vault_path')
    parser.add_argument('--login', action='store_true')
    parser.add_argument('--keywords', type=str)
    args = parser.parse_args()
    
    keywords = [k.strip() for k in args.keywords.split(',')] if args.keywords else None
    watcher = WhatsAppWatcher(args.vault_path, keywords=keywords)
    
    if args.login: watcher.open_login_window()
    else: watcher.run()
