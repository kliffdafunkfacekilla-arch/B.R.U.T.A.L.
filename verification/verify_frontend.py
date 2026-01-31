from playwright.sync_api import sync_playwright

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # 1. Navigate to the root URL (Frontend)
        page.goto("http://localhost:8000")

        # 2. Check initial state
        assert "Infinite Dungeon Master" in page.title()
        assert page.is_visible("#setup-panel")

        # 3. Start Session
        page.fill("#campaign-type", "Haunted Forest")
        page.click("button:has-text('Start Adventure')")

        # Wait for the game panel to appear
        page.wait_for_selector("#game-panel", state="visible")

        # Verify DM message (Intro)
        page.wait_for_selector(".dm-message")
        intro_text = page.inner_text(".dm-message")
        print(f"Intro: {intro_text}")
        assert "Haunted Forest" in intro_text

        # 4. Interact
        page.fill("#user-input", "I look around")
        page.click("button:has-text('Act')")

        # Wait for response
        page.wait_for_selector(".user-message") # My message
        page.wait_for_function("document.querySelectorAll('.dm-message').length > 1") # DM response

        # Take screenshot
        page.screenshot(path="verification/frontend_verify.png")
        print("Screenshot saved to verification/frontend_verify.png")

        browser.close()

if __name__ == "__main__":
    verify_frontend()
