import asyncio
import pytest
from pathlib import Path
from playwright.async_api import async_playwright

@pytest.mark.asyncio
async def test_modal():
    screenshot_dir = Path("/Users/rahulsahni/.gemini/antigravity-ide/brain/60d25ef6-d184-40bd-9fa1-dec83b7977bc")
    screenshot_path = screenshot_dir / "report_modal_result.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        await page.goto("http://127.0.0.1:3001", wait_until="domcontentloaded")
        await page.wait_for_selector(".btn-demo-mode", timeout=15000)
        await page.click(".btn-demo-mode")
        await page.wait_for_selector(".result-card", timeout=30000)
        
        # Click View 9-Image Pack
        print("Clicking View 9-Image Pack button...")
        await page.click("button:has-text('View 9-Image Pack')")
        
        # Wait for modal overlay
        await page.wait_for_selector(".modal-overlay", timeout=10000)
        await asyncio.sleep(1)
        
        await page.screenshot(path=str(screenshot_path))
        print(f"Saved modal screenshot to: {screenshot_path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_modal())
