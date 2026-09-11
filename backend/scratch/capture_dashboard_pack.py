import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def capture():
    dest_dir = Path("/Users/rahulsahni/.gemini/antigravity-ide/brain/60d25ef6-d184-40bd-9fa1-dec83b7977bc")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        
        # Load Next.js dashboard
        await page.goto("http://127.0.0.1:3001", wait_until="networkidle")
        await page.click("button:has-text('Google Maps')")
        await page.click(".btn-generate")
        await page.wait_for_selector(".result-card", timeout=30000)
        
        # 1. Capture Dashboard with 5-Image Pack Section
        await page.screenshot(path=str(dest_dir / "dashboard_image_pack_view.png"), full_page=True)
        print("Captured dashboard_image_pack_view.png")

        # 2. Click View 5-Image Pack button
        await page.click("button:has-text('VIEW 5-IMAGE PACK')")
        await page.wait_for_selector(".image-pack-modal-dialog", timeout=10000)
        await asyncio.sleep(2)
        await page.screenshot(path=str(dest_dir / "modal_image_pack_page1.png"))
        print("Captured modal_image_pack_page1.png")

        # 3. Click Page 4 button inside modal
        await page.click("button:has-text('04 Detailed 6-D Scorecard')")
        await asyncio.sleep(2)
        await page.screenshot(path=str(dest_dir / "modal_image_pack_page4.png"))
        print("Captured modal_image_pack_page4.png")

        # 4. Switch to QA Sheet tab
        await page.click("button:has-text('QA Sheet')")
        await asyncio.sleep(2)
        await page.screenshot(path=str(dest_dir / "modal_image_pack_qa_sheet.png"))
        print("Captured modal_image_pack_qa_sheet.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture())
