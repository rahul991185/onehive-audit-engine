import base64
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
import pypdf
from app.core.config import TEMPLATES_DIR, ONEHIVE_LOGO_PATH, PDF_DIR
from app.schemas.audit import StructuredAudit

def get_logo_base64() -> str:
    """Encodes official OneHive logo to base64 data URI for reliable offline PDF rendering."""
    if ONEHIVE_LOGO_PATH.exists():
        with open(ONEHIVE_LOGO_PATH, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    return ""

async def generate_5page_pdf(audit: StructuredAudit) -> tuple[Path, int]:
    """
    Renders the fixed OneHive 5-page report template to PDF via Playwright Chromium.
    Validates with pypdf that the resulting PDF contains exactly 5 pages.
    """
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report.html")
    
    css_path = TEMPLATES_DIR / "report.css"
    with open(css_path, "r", encoding="utf-8") as f:
        css_content = f.read()

    logo_base64 = get_logo_base64()

    rendered_html = template.render(
        audit=audit,
        css_content=css_content,
        logo_base64=logo_base64
    )

    output_pdf_path = PDF_DIR / f"{audit.audit_id}_report.pdf"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = await browser.new_context(
            viewport={"width": 794, "height": 1123},  # Standard A4 96dpi approx
            device_scale_factor=2
        )
        page = await context.new_page()
        
        # Set HTML content and wait for font and style load
        await page.set_content(rendered_html, wait_until="networkidle")
        await page.emulate_media(media="print")
        
        # Print exact A4 without outer browser margins
        await page.pdf(
            path=str(output_pdf_path),
            format="A4",
            print_background=True,
            prefer_css_page_size=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
        )
        await browser.close()

    # Verify page count with pypdf
    reader = pypdf.PdfReader(str(output_pdf_path))
    num_pages = len(reader.pages)
    
    if num_pages != 5:
        print(f"[WARNING] Generated PDF has {num_pages} pages, expected exactly 5!")
    else:
        print(f"[SUCCESS] Generated verified 5-page PDF: {output_pdf_path}")

    return output_pdf_path, num_pages
