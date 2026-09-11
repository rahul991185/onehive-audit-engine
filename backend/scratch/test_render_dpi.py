import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 1240 x 1754 at deviceScaleFactor 2 -> exactly 2480 x 3508
        ctx = await browser.new_context(
            viewport={"width": 1240, "height": 1754},
            device_scale_factor=2
        )
        page = await ctx.new_page()
        await page.set_content("""
        <html>
        <body style="margin:0; background:white;">
            <div id="test-page" style="width: 1240px; height: 1754px; background: #fff; border: 1px solid #ddd; padding: 40px; box-sizing: border-box;">
                <h1 style="font-size: 48px; color: #101828;">Test High Resolution</h1>
                <p style="font-size: 20px; color: #475467;">Testing 2480 x 3508 pixel output</p>
            </div>
        </body>
        </html>
        """)
        out_path = "/Users/rahulsahni/.gemini/antigravity-ide/brain/60d25ef6-d184-40bd-9fa1-dec83b7977bc/scratch/test_res.png"
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        element = page.locator("#test-page")
        await element.screenshot(path=out_path)
        await browser.close()

        img = Image.open(out_path)
        print(f"Rendered image size: {img.size}")
        assert img.size == (2480, 3508), f"Expected (2480, 3508), got {img.size}"
        print("SUCCESS: Exact 2480 x 3508 resolution achieved!")

if __name__ == "__main__":
    asyncio.run(test())
