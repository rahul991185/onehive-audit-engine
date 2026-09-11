import asyncio
from pathlib import Path
from PIL import Image
import pypdf
import zipfile

from app.services.audit_orchestrator import AuditOrchestrator
from app.config import IMAGEPACKS_DIR, VISUAL_QA_DIR, REPORTS_DIR

async def main():
    print("=== Generating Gyan Dairy 9-Page Golden Master Deliverable ===")
    resp = await AuditOrchestrator.run("https://gyandairy.com", is_demo=False)
    print("Audit ID:", resp.audit_id)
    print("Business:", resp.business.business_name)
    print("Score:", resp.overall_score)
    print(f"Image Pack URLs ({len(resp.image_pack_urls)}): {resp.image_pack_urls}")

    safe_slug = "".join(c if c.isalnum() else "_" for c in resp.business.business_name.lower())[:30].strip("_")
    images_dir = IMAGEPACKS_DIR / safe_slug
    assert images_dir.exists()

    for p in sorted(images_dir.glob("*.png")):
        im = Image.open(p)
        print(f"  {p.name}: {im.size}")
        assert im.size == (2480, 3508)

    cs_path = VISUAL_QA_DIR / f"{safe_slug}_contact_sheet.png"
    assert cs_path.exists()
    print(f"Contact Sheet: {cs_path}")

    pdf_path = REPORTS_DIR / f"{safe_slug}_digital_presence_report.pdf"
    assert pdf_path.exists()
    reader = pypdf.PdfReader(str(pdf_path))
    print(f"PDF Page count: {len(reader.pages)}")
    assert len(reader.pages) == 9

    print("=== Gyan Dairy 9-Page Deliverable Successfully Generated! ===")

if __name__ == "__main__":
    asyncio.run(main())
