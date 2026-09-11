import asyncio
import pytest
from pathlib import Path
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_frontend_flow():
    screenshot_dir = Path("/Users/rahulsahni/.gemini/antigravity-ide/brain/60d25ef6-d184-40bd-9fa1-dec83b7977bc")
    screenshot_path = screenshot_dir / "dashboard_result.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        print("Navigating to http://127.0.0.1:3001...")
        await page.goto("http://127.0.0.1:3001", wait_until="networkidle")
        await page.wait_for_selector(".btn-demo-mode", timeout=15000)
        await asyncio.sleep(1.5)
        
        print("Clicking Demo Mode preset button...")
        await page.click(".btn-demo-mode")
        
        # Wait for result card to appear
        print("Waiting for audit result card...")
        await page.wait_for_selector(".result-card", timeout=60000)
        
        # Extract details to verify
        biz_name = await page.inner_text(".result-business-info h2")
        score = await page.inner_text(".score-number")
        print(f"Audit completed for: {biz_name}, Score: {score}/100")
        
        # Verify 2-Page Report button exists
        pack_btn = page.locator("button:has-text('View 2-Page Report')")
        assert await pack_btn.is_visible(), "View 2-Page Report button not visible!"

        # Capture dashboard result screenshot
        await page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"Saved full page screenshot to: {screenshot_path}")

        # Open 2-Page Report Modal
        print("Clicking View 2-Page Report button...")
        await pack_btn.click()
        await page.wait_for_selector(".image-pack-modal-dialog", timeout=10000)
        
        modal = page.locator(".image-pack-modal-dialog")

        # Verify both page selector tabs exist inside modal
        btn_p1 = modal.locator("button:has-text('01 Digital Presence Snapshot')")
        btn_p2 = modal.locator("button:has-text('02 Your Growth Opportunity')")
        assert await btn_p1.is_visible(), "Page 1 tab not visible!"
        assert await btn_p2.is_visible(), "Page 2 tab not visible!"

        # Wait for Page 1 image to load
        await page.wait_for_selector("img[alt*='Page 1']", timeout=5000)
        await asyncio.sleep(1)
        # Capture modal screenshot on Page 1
        modal_shot = screenshot_dir / "frontend_2page_modal.png"
        await page.screenshot(path=str(modal_shot))
        print(f"Saved modal screenshot to: {modal_shot}")

        # Switch to Page 2
        print("Clicking Page 2 tab...")
        await btn_p2.click()
        await page.wait_for_selector("img[alt*='Page 2']", timeout=5000)
        await asyncio.sleep(1)
        modal_shot_p2 = screenshot_dir / "frontend_2page_modal_p2.png"
        await page.screenshot(path=str(modal_shot_p2))
        print(f"Saved modal Page 2 screenshot to: {modal_shot_p2}")

        # Switch to Side-by-Side QA Sheet
        print("Clicking Side-by-Side QA Sheet tab...")
        qa_btn = modal.locator("button:has-text('Side-by-Side QA Sheet')")
        await qa_btn.click()
        await page.wait_for_selector("img[alt*='Visual QA Contact Sheet']", timeout=5000)
        await asyncio.sleep(1.5)
        modal_shot_qa = screenshot_dir / "frontend_2page_modal_qa.png"
        await page.screenshot(path=str(modal_shot_qa))
        print(f"Saved modal QA sheet screenshot to: {modal_shot_qa}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_frontend_flow())
