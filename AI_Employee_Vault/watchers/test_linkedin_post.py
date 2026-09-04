"""
Test LinkedIn Auto-Post

Usage:
    python test_linkedin_post.py
"""

from pathlib import Path
import sys
import time
sys.path.insert(0, str(Path(__file__).parent))

from playwright.sync_api import sync_playwright

# Test post
vault = Path('D:/hackathonAI0/FTE-Hackathon-0/AI_Employee_Vault')
session_path = vault.parent / '.linkedin_session'
session_path.mkdir(exist_ok=True)

print("🔵 LinkedIn Auto-Post Test")
print("=" * 50)
print("\nThis will:")
print("1. Open LinkedIn in a VISIBLE browser")
print("2. YOU log in (first time only)")
print("3. Wait 30 seconds for you to log in")
print("4. Post a test update")
print("\n⚠️  IMPORTANT: You must log in when browser opens!")
print("\nPress Enter to continue...")
input()

print("\n🌐 Opening LinkedIn...")

try:
    with sync_playwright() as p:
        # Launch visible browser
        browser = p.chromium.launch_persistent_context(
            str(session_path),
            headless=False,
            args=[
                '--disable-gpu',
                '--no-sandbox',
                '--window-size=1920,1080'
            ]
        )
        
        page = browser.pages[0] if browser.pages else browser.new_page()

        # Navigate to LinkedIn (use 'domcontentloaded' - faster than 'networkidle')
        print("📍 Navigating to LinkedIn.com...")
        try:
            page.goto('https://www.linkedin.com', wait_until='domcontentloaded', timeout=60000)
            # Wait additional time for page to render
            print("   ⌛ Waiting for page to render...")
            time.sleep(10)
        except Exception as e:
            print(f"   ⚠️ Navigation issue: {e}")
            print("   Continuing anyway...")
        
        # Wait for user to log in
        print("\n⏳ Waiting 30 seconds for you to log in...")
        print("   → Enter your email/password")
        print("   → Complete any CAPTCHA")
        print("   → Wait for your feed to load")
        
        for i in range(30, 0, -1):
            print(f"   ⏱️  {i} seconds remaining...    ", end='\r')
            time.sleep(1)
        
        print("\n\n📝 Posting test update...")
        
        # Wait for page to fully load
        print("   ⌛ Waiting for page to load...")
        time.sleep(5)
        
        # Generate dynamic content
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        posts = [
            f"Alhamdulillah! AI Employee email automation is working perfectly. Tested at {timestamp}! #AI #Automation",
            f"Silver Tier progress! 🚀 Just built autonomous email replies with Qwen Code. #{timestamp} #Productivity",
            f"🎉 Email sent successfully! AI Employee can now detect emails and auto-reply with approval. #Innovation",
            f"Working on AI Employee Silver Tier - Gmail + LinkedIn automation! Alhamdulillah for this progress. 🙏",
        ]
        import random
        content = random.choice(posts)
        
        # Try to find the post creation box
        try:
            # Take a screenshot to debug
            page.screenshot(path='linkedin_debug.png')
            print("   📸 Screenshot saved as linkedin_debug.png")
            
            # Try different selectors for the post button
            post_selectors = [
                'button:has-text("Start a post")',
                'button:has-text("Create a post")', 
                '[data-control-name="update-share"]',
                '.share-box-feed-entry__trigger',
                'button[aria-label="Create a post"]'
            ]
            
            clicked = False
            for selector in post_selectors:
                try:
                    if page.is_visible(selector):
                        page.click(selector)
                        print(f"   ✓ Clicked: {selector}")
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                # Try clicking anywhere in the post area
                print("   Trying alternative approach...")
                page.goto('https://www.linkedin.com/feed')
                time.sleep(3)
                
                # Find and click the post textbox directly
                textbox = page.locator('[contenteditable="true"]').first
                if textbox.is_visible():
                    textbox.click()
                    print("   ✓ Found editable textbox")
            
            # Wait for editor
            print("   ⌛ Waiting for editor...")
            time.sleep(3)
            
            # Type content
            print(f"   📝 Posting: {content[:50]}...")
            
            # Use keyboard type instead of fill
            editable = page.locator('[contenteditable="true"]').first
            editable.click()
            editable.type(content, delay=50)
            print("   ✓ Typed content")
            
            # Add hashtags
            editable.type('\n\n#AI #Automation #Productivity', delay=50)
            print("   ✓ Added hashtags")
            
            # Wait for post button to become enabled (LinkedIn takes time)
            print("   ⌛ Waiting for Post button to enable...")
            for i in range(10):
                time.sleep(1)
                print(f"      {i+1}s...", end='\r')
            
            # Find and click Post button - try multiple selectors
            post_button_selectors = [
                'button[aria-label="Post"]',
                'button:has-text("Post")',
                '.share-actions__post-button button',
                'button[class*="post-button"]'
            ]
            
            posted = False
            for selector in post_button_selectors:
                try:
                    post_button = page.locator(selector).first
                    if post_button.is_visible() and post_button.is_enabled():
                        post_button.click()
                        print(f"\n   ✓ Clicked Post button: {selector}")
                        posted = True
                        break
                except:
                    continue
            
            if posted:
                # Wait for confirmation
                time.sleep(5)
                print("\n✅ Post should be published! Check your LinkedIn profile.")
            else:
                # Manual fallback - keep browser open longer
                print("\n\n⚠️  AUTO-POST FAILED - MANUAL STEP REQUIRED:")
                print("   Browser will stay open for 30 more seconds")
                print("   → CLICK THE 'POST' BUTTON YOURSELF!")
                print("   → Content is already typed in the editor")
                time.sleep(30)
                
        except Exception as e:
            print(f"\n❌ Error posting: {e}")
            print("   Make sure you're logged in and can see your feed")
        
        print("\n🔒 Keeping browser open for 10 more seconds...")
        time.sleep(10)
        browser.close()
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\nDone!")
