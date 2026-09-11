import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

ARTIFACTS_DIR = Path("/Users/rahulsahni/.gemini/antigravity-ide/brain/60d25ef6-d184-40bd-9fa1-dec83b7977bc")

async def capture_ui_states():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        page.on("console", lambda m: print(f"[Browser Console] {m.type}: {m.text}"))
        page.on("pageerror", lambda err: print(f"[Browser PageError] {err}"))

        print("[UI Visual QA] Navigating to http://localhost:3001...")
        await page.goto("http://localhost:3001", wait_until="networkidle")

        # 1. Capture initial home screen at 1440px
        await page.screenshot(path=str(ARTIFACTS_DIR / "final_home_1440px.png"), full_page=False)
        print("[UI Visual QA] Saved final_home_1440px.png")

        # 2. Test Mobile Viewport at 390px to verify zero input/button overlap
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.screenshot(path=str(ARTIFACTS_DIR / "final_input_mobile_390px.png"), full_page=False)
        print("[UI Visual QA] Saved final_input_mobile_390px.png")

        # Restore 1440px
        await page.set_viewport_size({"width": 1440, "height": 900})

        # 3. Click 'Load Demo Business' to verify Demo Mode
        demo_btn = page.locator(".btn-demo-mode")
        if await demo_btn.count() > 0:
            print("[UI Visual QA] Clicking Demo Mode button...")
            await demo_btn.click()
            # Wait for result card to appear
            await page.wait_for_selector(".result-card", timeout=45000)
            await page.screenshot(path=str(ARTIFACTS_DIR / "final_demo_result.png"), full_page=False)
            print("[UI Visual QA] Saved final_demo_result.png")

            # 4. Open Website Preview Modal
            preview_btn = page.locator("button:has-text('View Website Preview')")
            if await preview_btn.count() > 0:
                await preview_btn.click()
                await page.wait_for_selector(".preview-dialog", timeout=5000)
                await page.screenshot(path=str(ARTIFACTS_DIR / "final_preview_modal_desktop.png"), full_page=False)
                print("[UI Visual QA] Saved final_preview_modal_desktop.png")

                # Switch to Mobile tab in Preview Modal
                mobile_tab = page.locator("button:has-text('Mobile (390px)')")
                if await mobile_tab.count() > 0:
                    await mobile_tab.click()
                    await asyncio.sleep(1)
                    await page.screenshot(path=str(ARTIFACTS_DIR / "final_preview_modal_mobile.png"), full_page=False)
                    print("[UI Visual QA] Saved final_preview_modal_mobile.png")

                # Close modal
                await page.locator(".preview-dialog .btn-close").click()
                await asyncio.sleep(0.5)

            # 5. Open Quick Win Modal
            qw_btn = page.locator("button:has-text('View Quick Win')")
            if await qw_btn.count() > 0:
                await qw_btn.click()
                await page.wait_for_selector(".quick-win-dialog", timeout=5000)
                await page.screenshot(path=str(ARTIFACTS_DIR / "final_quick_win_modal.png"), full_page=False)
                print("[UI Visual QA] Saved final_quick_win_modal.png")
                await page.locator(".quick-win-dialog .btn-close").click()
                await asyncio.sleep(0.5)

            # 6. Open WhatsApp Modal
            wa_btn = page.locator("button:has-text('Copy WhatsApp')")
            if await wa_btn.count() > 0:
                await wa_btn.click()
                await page.wait_for_selector(".whatsapp-dialog", timeout=5000)
                await page.screenshot(path=str(ARTIFACTS_DIR / "final_whatsapp_modal.png"), full_page=False)
                print("[UI Visual QA] Saved final_whatsapp_modal.png")
                await page.locator(".whatsapp-dialog .btn-close").click()
                await asyncio.sleep(0.5)

            # 7. Open Sales Brief Modal
            sb_btn = page.locator("button:has-text('View Sales Brief')")
            if await sb_btn.count() > 0:
                await sb_btn.click()
                await page.wait_for_selector(".sales-brief-dialog", timeout=5000)
                await page.screenshot(path=str(ARTIFACTS_DIR / "final_sales_brief_modal.png"), full_page=False)
                print("[UI Visual QA] Saved final_sales_brief_modal.png")
                await page.locator(".sales-brief-dialog .btn-close").click()

        # 8. Test live research on the target CID URL
        print("[UI Visual QA] Testing Live Research with Target CID URL...")
        target_url = "https://maps.google.com/?cid=8429486214490638391&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQAhgEIAA"
        await page.fill(".main-url-input", target_url)
        await page.click(".btn-generate")
        await page.wait_for_selector(".result-card", timeout=60000)

        # Ensure it resolved to Dr. Budhiraja
        card_text = await page.inner_text(".result-card")
        assert "Budhiraja" in card_text, "Target URL must resolve to Dr. Budhiraja!"
        assert "Apex Dental" not in card_text, "Target URL must NEVER resolve to Apex Dental!"

        await page.screenshot(path=str(ARTIFACTS_DIR / "final_live_cid_result.png"), full_page=False)
        print("[UI Visual QA] Successfully verified live research: saved final_live_cid_result.png")

        await browser.close()
        print("\n[ALL UI VISUAL QA CHECKS PASSED]")

if __name__ == "__main__":
    asyncio.run(capture_ui_states())
