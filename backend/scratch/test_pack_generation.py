import asyncio
from app.services.audit_orchestrator import AuditOrchestrator
from PIL import Image
from app.config import IMAGEPACKS_DIR, VISUAL_QA_DIR
import zipfile

async def main():
    print("Running audit with ImagePackRenderer...")
    resp = await AuditOrchestrator.run("https://demo.mode", is_demo=True)
    print("Audit ID:", resp.audit_id)
    print("Business:", resp.business.business_name)
    print("Image Pack URLs:", resp.image_pack_urls)
    print("ZIP URL:", resp.digital_pack_zip_url)
    print("Contact Sheet URL:", resp.contact_sheet_url)
    
    safe_slug = "".join(c if c.isalnum() else "_" for c in resp.business.business_name.lower())[:30].strip("_")
    images_dir = IMAGEPACKS_DIR / safe_slug
    assert images_dir.exists(), f"Dir {images_dir} does not exist"
    
    pngs = sorted(list(images_dir.glob("*.png")))
    assert len(pngs) == 5, f"Expected 5 PNGs, found {len(pngs)}"
    for p in pngs:
        im = Image.open(p)
        print(f"Page {p.name}: {im.size}")
        assert im.size == (2480, 3508), f"Image {p.name} size {im.size} is not (2480, 3508)!"
    
    # Check ZIP
    zip_path = IMAGEPACKS_DIR / f"onehive-{safe_slug}-digital-presence-pack.zip"
    assert zip_path.exists(), f"ZIP {zip_path} does not exist"
    with zipfile.ZipFile(str(zip_path), "r") as z:
        names = z.namelist()
        print("ZIP names:", names)
        assert len(names) >= 6, "ZIP should contain 5 PNGs + audit.json"
        assert any("01-cover.png" in n for n in names)
        assert any("02-digital-snapshot.png" in n for n in names)
        assert any("03-about-business.png" in n for n in names)
        assert any("04-scorecard.png" in n for n in names)
        assert any("05-opportunity.png" in n for n in names)
        assert any("audit.json" in n for n in names)
        
    # Check contact sheet
    cs_path = VISUAL_QA_DIR / f"{safe_slug}_contact_sheet.png"
    assert cs_path.exists(), f"Contact sheet {cs_path} does not exist"
    cs_im = Image.open(cs_path)
    print("Contact sheet size:", cs_im.size)
    print("\n>>> ALL IMAGE PACK TESTS PASSED WITH 100% SUCCESS! <<<")

if __name__ == "__main__":
    asyncio.run(main())
