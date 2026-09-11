import base64
import json
import zipfile
import io
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
from PIL import Image

from app.config import (
    TEMPLATES_DIR,
    ONEHIVE_LOGO_PATH,
    REPORTS_DIR,
    IMAGEPACKS_DIR,
    VISUAL_QA_DIR,
    ONEHIVE_WEBSITE,
    ONEHIVE_EMAIL,
    ONEHIVE_PHONE,
    ONEHIVE_ADDRESS
)
from app.models.schemas import BusinessIdentity, AuditScore, Opportunity, Recommendation
from app.pdf.verifier import PDFVerifier
from app.services.report_v2_adapter import ReportV2Adapter

class ImagePackRenderer:
    """
    Primary Client Deliverable Engine:
    Renders the 2 High-Resolution PNG pages (2480x3508 A4 300DPI equivalent),
    assembles the OneHive Digital Presence Pack ZIP, creates the side-by-side QA Contact Sheet,
    and exports the secondary strictly 2-page PDF.
    """

    PAGE_SELECTORS = [
        (".page-1", "01-page1.png"),
        (".page-2", "02-page2.png")
    ]

    @staticmethod
    def get_base64_image(file_path: Path) -> str:
        if file_path and file_path.exists():
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                mime = "image/png" if file_path.suffix == ".png" else "image/jpeg"
                return f"data:{mime};base64,{encoded}"
        return ""

    @staticmethod
    def generate_contact_sheet(image_paths: List[Path], output_path: Path) -> Path:
        """
        Assembles both 2-page PNGs into a side-by-side editorial contact sheet for visual QA.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        images = [Image.open(p) for p in image_paths if p.exists()]
        if not images:
            return output_path

        # Thumbnails at 700 x 990 (A4 aspect ratio)
        thumb_w, thumb_h = 700, 990
        thumbs = [img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS) for img in images]

        cols = len(thumbs)
        gap_x = 36
        pad_x = 48
        pad_y = 48

        sheet_w = (thumb_w * cols) + (gap_x * (cols - 1)) + (pad_x * 2)
        sheet_h = thumb_h + (pad_y * 2)

        sheet = Image.new("RGB", (sheet_w, sheet_h), color=(241, 245, 249))

        for idx, thumb in enumerate(thumbs):
            x = pad_x + idx * (thumb_w + gap_x)
            y = pad_y
            sheet.paste(thumb, (x, y))

        sheet.save(str(output_path), "PNG", quality=95)
        return output_path

    @staticmethod
    def build_pack_zip(
        audit_id: str,
        safe_name: str,
        image_paths: List[Path],
        audit_dict: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Builds the client ZIP bundle containing:
        onehive-[business]-digital-presence-pack/
            01-page1.png
            02-page2.png
            audit.json
        """
        safe_slug = "".join(c if c.isalnum() else "_" for c in safe_name.lower())[:30].strip("_")
        zip_filename = f"onehive-{safe_slug}-digital-presence-pack.zip"
        zip_dest = IMAGEPACKS_DIR / zip_filename
        zip_dest.parent.mkdir(parents=True, exist_ok=True)

        folder_prefix = f"onehive-{safe_slug}-digital-presence-pack"

        with zipfile.ZipFile(str(zip_dest), "w", zipfile.ZIP_DEFLATED) as z:
            for img_path in image_paths:
                if img_path.exists():
                    z.write(str(img_path), arcname=f"{folder_prefix}/{img_path.name}")
            
            if audit_dict:
                audit_json_str = json.dumps(audit_dict, indent=2, default=str)
                z.writestr(f"{folder_prefix}/audit.json", audit_json_str)

        return zip_dest

    @staticmethod
    async def render(
        audit_id: str,
        identity: BusinessIdentity,
        scores: AuditScore,
        strongest_asset: str,
        biggest_gap: str,
        opp: Opportunity,
        recommendations: List[Recommendation],
        audit_dict: Optional[Dict[str, Any]] = None,
        evidence: Optional[List[Any]] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Path], Path, Path, Path, bool, List[str]]:
        """
        Primary Render Execution:
        Renders the 2-page report, side-by-side contact sheet, ZIP bundle, and strictly 2-page PDF.
        Returns (image_paths, zip_path, contact_sheet_path, pdf_path, is_valid, errors)
        """
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR / "report")))
        template = env.get_template("report.html")

        css_path = TEMPLATES_DIR / "report" / "report.css"
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        page_data = ReportV2Adapter.build_page_data(
            audit_id=audit_id,
            identity=identity,
            scores=scores,
            strongest_asset=strongest_asset,
            biggest_gap=biggest_gap,
            opp=opp,
            recommendations=recommendations,
            evidence=evidence,
            extra_data=extra_data
        )

        rendered_html = template.render(
            p=page_data,
            css_content=css_content
        )

        safe_slug = "".join(c if c.isalnum() else "_" for c in identity.business_name.lower())[:30].strip("_")
        
        # Setup output directories
        pack_dir = IMAGEPACKS_DIR / safe_slug
        pack_dir.mkdir(parents=True, exist_ok=True)
        output_pdf_path = REPORTS_DIR / f"{safe_slug}_digital_presence_report.pdf"

        image_paths: List[Path] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = await browser.new_context(
                viewport={"width": 1240, "height": 1754},
                device_scale_factor=2
            )
            page = await context.new_page()
            await page.set_content(rendered_html, wait_until="networkidle")

            # 1. Screenshot both of the 2 pages and guarantee exact 2480 x 3508 resolution
            for selector, filename in ImagePackRenderer.PAGE_SELECTORS:
                img_path = pack_dir / filename
                el = page.locator(selector)
                raw_bytes = await el.screenshot(type="png")
                with Image.open(io.BytesIO(raw_bytes)) as pil_img:
                    final_img = pil_img.resize((2480, 3508), Image.Resampling.LANCZOS)
                    final_img.save(str(img_path), "PNG", quality=95)
                image_paths.append(img_path)

            # 2. Secondary export: Strictly 2-page PDF
            await page.emulate_media(media="print")
            await page.pdf(
                path=str(output_pdf_path),
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
            )
            await browser.close()

        # 3. Build standalone Pack ZIP
        zip_path = ImagePackRenderer.build_pack_zip(
            audit_id=audit_id,
            safe_name=identity.business_name,
            image_paths=image_paths,
            audit_dict=audit_dict
        )

        # 4. Generate Side-by-Side Visual QA Contact Sheet
        contact_sheet_path = VISUAL_QA_DIR / f"{safe_slug}_contact_sheet.png"
        ImagePackRenderer.generate_contact_sheet(image_paths, contact_sheet_path)

        # Also copy contact sheet to conversation brain artifacts for user inspection
        brain_cs_dir = Path("/Users/rahulsahni/.gemini/antigravity-ide/brain/60d25ef6-d184-40bd-9fa1-dec83b7977bc/visual_qa")
        brain_cs_dir.mkdir(parents=True, exist_ok=True)
        brain_cs_path = brain_cs_dir / "contact-sheet.png"
        try:
            import shutil
            shutil.copyfile(str(contact_sheet_path), str(brain_cs_path))
        except Exception:
            pass

        # 5. Automated PDF QA check
        is_valid, errors = PDFVerifier.verify(output_pdf_path, identity, scores)

        return image_paths, zip_path, contact_sheet_path, output_pdf_path, is_valid, errors
