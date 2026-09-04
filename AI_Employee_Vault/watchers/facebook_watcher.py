import os
import sys
import logging
import time
import json
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

# Playwright dependencies
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class FacebookWatcher(BaseWatcher):
    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 600):
        super().__init__(vault_path, check_interval)
        self.session_path = Path(session_path) if session_path else (Path.home() / '.facebook_session')
        self.session_path.mkdir(parents=True, exist_ok=True)

    def is_logged_in(self, page) -> bool:
        try:
            # Relaxed wait for login check
            page.goto('https://www.facebook.com', wait_until='load')
            time.sleep(2)
            if page.query_selector('input[name="email"]'): return False
            if page.query_selector('[aria-label="Search Facebook"]') or page.query_selector('[aria-label="Your profile"]'): return True
            return False
        except: return False

    def open_login_window(self):
        with sync_playwright() as p:
            print("Opening browser for manual login...")
            browser = p.chromium.launch_persistent_context(str(self.session_path), headless=False)
            page = browser.pages[0]
            page.goto('https://www.facebook.com', wait_until='load')
            print("PLEASE LOG IN MANUALLY. Close the browser window when finished.")
            while len(browser.pages) > 0:
                time.sleep(1)
            print("Login session saved.")

    def post_update(self, message: str) -> bool:
        print(f"Attempting to post: {message}")
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(str(self.session_path), headless=False)
            page = browser.pages[0]
            
            try:
                # Using 'load' instead of 'networkidle' for reliability on heavy sites
                page.goto('https://www.facebook.com', wait_until='load')
                print("Page loaded, waiting for UI to stabilize...")
                time.sleep(5) 
                
                trigger_selectors = [
                    'div[role="button"]:has-text("What\'s on your mind")',
                    'span:has-text("What\'s on your mind")',
                    '[aria-label^="What\'s on your mind"]',
                ]
                
                trigger = None
                for sel in trigger_selectors:
                    try:
                        trigger = page.wait_for_selector(sel, timeout=7000)
                        if trigger: 
                            trigger.click()
                            break
                    except: continue
                
                if not trigger:
                    print("Post trigger not found via selectors, searching for text...")
                    page.get_by_text("What's on your mind?").first.click()

                print("Waiting for textbox...")
                textbox = page.wait_for_selector('div[role="textbox"]', timeout=10000)
                textbox.fill(message)
                
                print("Clicking Post button...")
                time.sleep(2) # Wait for text to settle
                try:
                    page.click('div[aria-label="Post"]')
                except:
                    page.get_by_role("button", name="Post").click()
                
                print("Finalizing post...")
                time.sleep(5)
                browser.close()
                print("✅ Successfully posted to Facebook!")
                return True
            except Exception as e:
                print(f"❌ Error during post process: {e}")
                try: page.screenshot(path="fb_error_debug.png")
                except: pass
                browser.close()
                return False

    def check_for_updates(self) -> list:
        return []

    def create_action_file(self, notification: dict) -> Path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        content = f"---\ntype: facebook_activity\nstatus: pending\n---\n# Facebook Activity\nDetected activity: {notification}"
        filepath = self.needs_action / f'FB_ACTIVITY_{timestamp}.md'
        filepath.write_text(content, encoding='utf-8')
        return filepath

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('vault_path')
    parser.add_argument('--post', type=str)
    parser.add_argument('--login', action='store_true')
    args = parser.parse_args()
    watcher = FacebookWatcher(args.vault_path)
    if args.login: watcher.open_login_window()
    elif args.post: watcher.post_update(args.post)
    else: watcher.run()
