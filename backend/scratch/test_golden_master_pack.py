import asyncio
from pathlib import Path
from PIL import Image
import pypdf
import zipfile

from app.services.audit_orchestrator import AuditOrchestrator
from app.config import IMAGEPACKS_DIR, VISUAL_QA_DIR, REPORTS_DIR

async def main():
    print("=== Testing Golden Master 9-Page Intelligence Pack via AuditOrchestrator ===")
    resp = await AuditOrchestrator.run("https://demo.mode", is_demo=True)
    print("Audit ID:", resp.audit_id)
    print("Business:", resp.business.business_name)
    print(f"Image Pack URLs count: {len(resp.image_pack_urls)}")
    assert len(resp.image_pack_urls) == 9, f"Expected 9 image pack URLs, got {len(resp.image_pack_urls)}"
    print("ZIP URL:", resp.digital_pack_zip_url)
    print("Contact Sheet URL:", resp.contact_sheet_url)

    safe_slug = "".join(c if c.isalnum() else "_" for c in resp.business.business_name.lower())[:30].strip("_")
    images_dir = IMAGEPACKS_DIR / safe_slug
    assert images_dir.exists(), f"Dir {images_dir} does not exist"

    expected_filenames = [
        "01-cover.png",
        "02-executive-summary.png",
        "03-about-business.png",
        "04-detailed-scorecard.png",
        "05-what-youre-doing-well.png",
        "06-your-no1-opportunity.png",
        "07-customer-journey.png",
        "08-recommended-solution.png",
        "09-next-steps.png"
    ]

    for fname in expected_filenames:
        img_p = images_dir / fname
        assert img_p.exists(), f"Image {fname} does not exist in {images_dir}!"
        im = Image.open(img_p)
        print(f"  Page {fname}: size={im.size}, mode={im.mode}")
        assert im.size == (2480, 3508), f"Image {fname} size {im.size} != (2480, 3508)!"

    # Check 3x3 Contact Sheet
    cs_path = VISUAL_QA_DIR / f"{safe_slug}_contact_sheet.png"
    assert cs_path.exists(), f"Contact sheet {cs_path} does not exist!"
    cs_im = Image.open(cs_path)
    print(f"Contact sheet: size={cs_im.size}")
    assert cs_im.size[0] >= 1000 and cs_im.size[1] >= 1400

    # Check ZIP Bundle
    zip_path = IMAGEPACKS_DIR / f"onehive-{safe_slug}-digital-presence-pack.zip"
    assert zip_path.exists(), f"ZIP {zip_path} does not exist!"
    with zipfile.ZipFile(str(zip_path), "r") as z:
        names = z.namelist()
        print(f"ZIP files count: {len(names)}")
        pngs_in_zip = [n for n in names if n.endswith(".png")]
        jsons_in_zip = [n for n in names if n.endswith(".json")]
        assert len(pngs_in_zip) == 9, f"Expected 9 PNGs in ZIP, got {len(pngs_in_zip)}"
        assert len(jsons_in_zip) == 1, f"Expected 1 audit.json in ZIP, got {len(jsons_in_zip)}"

    # Check Secondary PDF Export (Strictly 9 pages)
    pdf_path = REPORTS_DIR / f"{safe_slug}_digital_presence_report.pdf"
    assert pdf_path.exists(), f"PDF {pdf_path} does not exist!"
    reader = pypdf.PdfReader(str(pdf_path))
    print(f"PDF Page count: {len(reader.pages)}")
    assert len(reader.pages) == 9, f"Expected strictly 9 pages in PDF, got {len(reader.pages)}"

    print("\n============================================================")
    print("SUCCESS: 9-PAGE GOLDEN MASTER REPORT PIPELINE FULLY VALIDATED!")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(main())
