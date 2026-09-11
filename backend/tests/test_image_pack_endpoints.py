import io
import zipfile
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_image_pack_full_pipeline():
    # 1. Trigger audit on demo URL
    payload = {
        "url": "https://maps.app.goo.gl/apex-dental-mock-demo",
        "is_demo": True
    }
    response = client.post("/api/audits", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    audit_id = data["audit_id"]

    assert "image_pack_urls" in data
    assert len(data["image_pack_urls"]) == 2, f"Expected 2 image_pack_urls, got {len(data['image_pack_urls'])}"
    assert "digital_pack_zip_url" in data
    assert "contact_sheet_url" in data

    # 2. Test each individual page image endpoint (1 to 2)
    for page in range(1, 3):
        img_resp = client.get(f"/api/audits/{audit_id}/images/{page}")
        assert img_resp.status_code == 200, f"Page {page} failed"
        assert img_resp.headers["content-type"] == "image/png"

        # Verify exact 2480x3508 resolution
        img = Image.open(io.BytesIO(img_resp.content))
        assert img.size == (2480, 3508), f"Page {page} dimension mismatch: {img.size}"

    # 3. Test side-by-side contact sheet endpoint
    cs_resp = client.get(f"/api/audits/{audit_id}/contact-sheet")
    assert cs_resp.status_code == 200
    assert cs_resp.headers["content-type"] == "image/png"
    cs_img = Image.open(io.BytesIO(cs_resp.content))
    assert cs_img.size[0] >= 1400 and cs_img.size[1] >= 900

    # 4. Test image pack standalone ZIP endpoint
    zip_resp = client.get(f"/api/audits/{audit_id}/image-pack-zip")
    assert zip_resp.status_code == 200
    assert "zip" in zip_resp.headers["content-type"]

    with zipfile.ZipFile(io.BytesIO(zip_resp.content)) as z:
        names = z.namelist()
        # Should contain 2 images and audit.json
        png_names = [n for n in names if n.endswith(".png")]
        json_names = [n for n in names if n.endswith(".json")]
        assert len(png_names) == 2, f"Expected 2 pngs in zip, found {len(png_names)}"
        assert len(json_names) == 1, f"Expected 1 json in zip, found {json_names}"
