import asyncio
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
from app.core.config import TEMPLATES_DIR
from app.services.classifier import classify_url
from app.services.research.mock_data import generate_mock_audit
from app.services.pdf_generator import get_logo_base64

async def capture_pages():
    artifact_dir = Path("/Users/rahulsahni/.gemini/antigravity-ide/brain/60d25ef6-d184-40bd-9fa1-dec83b7977bc")
    
    url = "https://www.google.com/maps/place/Apex+Dental+Clinic+Indiranagar"
    audit = generate_mock_audit(url, classify_url(url))

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report.html")
    with open(TEMPLATES_DIR / "report.css", "r", encoding="utf-8") as f:
        css_content = f.read()

    rendered_html = template.render(
        audit=audit,
        css_content=css_content,
        logo_base64=get_logo_base64()
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 210mm x 297mm at 96dpi is 794 x 1123, with scale factor 2
        page = await browser.new_page(viewport={"width": 794, "height": 1123}, device_scale_factor=2)
        await page.set_content(rendered_html, wait_until="networkidle")

        pages = await page.query_selector_all(".page")
        for i, page_el in enumerate(pages, 1):
            out_path = artifact_dir / f"report_page_{i}.png"
            await page_el.screenshot(path=str(out_path))
            print(f"Captured Page {i}: {out_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_pages())
