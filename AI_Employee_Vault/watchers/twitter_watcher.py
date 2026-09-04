import os
import sys
import time
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class TwitterWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 600):
        super().__init__(vault_path, check_interval)
        self.session_path = Path(session_path) if session_path else (Path.home() / '.twitter_session')
        self.session_path.mkdir(parents=True, exist_ok=True)

    def open_login_window(self):
        """Opens a high-stealth browser for manual login."""
        with sync_playwright() as p:
            print("Opening Twitter in Ultra-Stealth Mode...")
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,
                # Hide the "Automation" flag that Twitter detects
                ignore_default_args=["--enable-automation"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                viewport={'width': 1280, 'height': 800},
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = browser.pages[0]
            page.goto('https://x.com/i/flow/login')
            
            print("---")
            print("PLEASE LOG IN MANUALLY.")
            print("If the 'Log in' button doesn't work, try pressing the ENTER key.")
            print("---")
            
            while len(browser.pages) > 0:
                time.sleep(1)
            print("Twitter session saved successfully.")

    def post_update(self, message: str) -> bool:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(self.session_path), 
                headless=False,
                ignore_default_args=["--enable-automation"],
                args=["--disable-blink-features=AutomationControlled"]
            )
            page = browser.pages[0]
            try:
                page.goto('https://x.com/home', wait_until='load')
                time.sleep(5)
                textbox = page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)
                textbox.fill(message)
                page.click('[data-testid="tweetButtonInline"]')
                time.sleep(5)
                browser.close()
                return True
            except Exception as e:
                print(f"Error: {e}")
                browser.close()
                return False

    def check_for_updates(self) -> list: return []
    def create_action_file(self, n) -> Path: return Path()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('vault_path')
    parser.add_argument('--post', type=str)
    parser.add_argument('--login', action='store_true')
    args = parser.parse_args()
    watcher = TwitterWatcher(args.vault_path)
    if args.login: watcher.open_login_window()
    elif args.post: watcher.post_update(args.post)
    else: watcher.run()
