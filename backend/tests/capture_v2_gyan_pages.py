import asyncio
import sys
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import TEMPLATES_DIR, ONEHIVE_LOGO_PATH, ONEHIVE_WEBSITE, ONEHIVE_EMAIL, ONEHIVE_PHONE, ONEHIVE_ADDRESS
from app.pdf.renderer import PDFRenderer
from app.services.audit_orchestrator import AuditOrchestrator

GYAN_DENTAL_URL = "https://maps.google.com/?cid=3648219209233379687&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQAhgEIAA"

async def capture_gyan_pages():
    artifact_dir = Path("/Users/rahulsahni/.gemini/antigravity-ide/brain/60d25ef6-d184-40bd-9fa1-dec83b7977bc")
    
    audit = await AuditOrchestrator.run(GYAN_DENTAL_URL, is_demo=False)
    
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR / "report")))
    template = env.get_template("report.html")
    with open(TEMPLATES_DIR / "report" / "report.css", "r", encoding="utf-8") as f:
        css_content = f.read()

    desktop_preview_path = Path(__file__).parent.parent / "storage" / "artifacts" / "previews" / f"{audit.audit_id}_desktop.png"
    mobile_preview_path = Path(__file__).parent.parent / "storage" / "artifacts" / "previews" / f"{audit.audit_id}_mobile.png"

    logo_base64 = PDFRenderer.get_base64_image(ONEHIVE_LOGO_PATH)
    preview_teaser_base64 = PDFRenderer.get_base64_image(desktop_preview_path) if desktop_preview_path.exists() else ""
    mobile_teaser_base64 = PDFRenderer.get_base64_image(mobile_preview_path) if mobile_preview_path.exists() else ""

    config_data = {
        "ONEHIVE_WEBSITE": ONEHIVE_WEBSITE,
        "ONEHIVE_EMAIL": ONEHIVE_EMAIL,
        "ONEHIVE_PHONE": ONEHIVE_PHONE,
        "ONEHIVE_ADDRESS": ONEHIVE_ADDRESS
    }

    norm_scores = {
        "discoverability": int(round((audit.scores.discoverability / 20) * 100)),
        "brand_identity": int(round((audit.scores.brand_identity / 15) * 100)),
        "trust_reputation": int(round((audit.scores.trust_reputation / 20) * 100)),
        "website_experience": int(round((audit.scores.website_experience / 15) * 100)),
        "lead_conversion": int(round((audit.scores.lead_conversion / 20) * 100)),
        "social_presence": int(round((audit.scores.social_presence / 10) * 100)),
    }
    services, positioning_statement, first_move, first_move_desc = PDFRenderer.get_vertical_details(audit.business, audit.scores)

    rendered_html = template.render(
        identity=audit.business,
        scores=audit.scores,
        norm_scores=norm_scores,
        strongest_asset=audit.strongest_asset,
        biggest_gap=audit.biggest_gap,
        opportunity=audit.top_opportunity,
        recommendations=audit.recommendations,
        services=services,
        positioning_statement=positioning_statement,
        first_move=first_move,
        first_move_desc=first_move_desc,
        css_content=css_content,
        logo_base64=logo_base64,
        date_str="September 11, 2026",
        config=config_data
    )

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 794, "height": 1123}, device_scale_factor=2)
        await page.set_content(rendered_html, wait_until="networkidle")

        pages = await page.query_selector_all(".page")
        print(f"Detected {len(pages)} .page elements in DOM")
        for i, p_el in enumerate(pages, 1):
            out_png = artifact_dir / f"v2_gyan_page_{i}.png"
            await p_el.screenshot(path=str(out_png))
            print(f"Captured Page {i}: {out_png}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_gyan_pages())
