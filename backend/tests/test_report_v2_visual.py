import io
import zipfile
import pytest
from PIL import Image
import pypdf
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_report_v2_two_page_pack():
    """
    Automated QA Test for 2-Page Digital Presence Intelligence Report Engine:
    - Verifies 2 PNG images generated at exact 2480x3508 resolution (300 DPI A4)
    - Verifies side-by-side QA contact sheet
    - Verifies ZIP deliverable contains 2 images + audit.json
    - Verifies secondary PDF export contains strictly 2 pages
    - Verifies all REST API endpoints for individual images, zip, contact sheet, and PDF
    """
    # 1. Trigger audit on demo fixture
    payload = {
        "url": "https://maps.app.goo.gl/apex-dental-mock-demo",
        "is_demo": True
    }
    response = client.post("/api/audits", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    audit_id = data["audit_id"]

    # 2. Verify response schema metadata
    assert "image_pack_urls" in data
    assert len(data["image_pack_urls"]) == 2, f"Expected 2 image_pack_urls, got {len(data['image_pack_urls'])}"
    assert "digital_pack_zip_url" in data
    assert "contact_sheet_url" in data
    assert "report_pdf_url" in data

    # 3. Verify all 2 individual image endpoints & exact dimensions
    for page in [1, 2]:
        url = f"/api/audits/{audit_id}/images/{page}"
        img_resp = client.get(url)
        assert img_resp.status_code == 200, f"Failed fetching page {page} from {url}"
        assert img_resp.headers["content-type"] == "image/png"

        img = Image.open(io.BytesIO(img_resp.content))
        assert img.size == (2480, 3508), f"Page {page} dimensions {img.size} != (2480, 3508)!"

    # 4. Verify side-by-side QA contact sheet
    cs_resp = client.get(f"/api/audits/{audit_id}/contact-sheet")
    assert cs_resp.status_code == 200
    assert cs_resp.headers["content-type"] == "image/png"
    cs_img = Image.open(io.BytesIO(cs_resp.content))
    # Side-by-side should be wide (>= 1400 px width)
    assert cs_img.size[0] >= 1400 and cs_img.size[1] >= 900, f"Contact sheet size {cs_img.size} is unexpected"

    # 5. Verify ZIP deliverable pack
    zip_resp = client.get(f"/api/audits/{audit_id}/image-pack-zip")
    assert zip_resp.status_code == 200
    assert "zip" in zip_resp.headers["content-type"]

    with zipfile.ZipFile(io.BytesIO(zip_resp.content)) as z:
        names = z.namelist()
        png_names = [n for n in names if n.endswith(".png")]
        json_names = [n for n in names if n.endswith(".json")]
        assert len(png_names) == 2, f"Expected 2 PNGs in ZIP, got {len(png_names)}"
        assert len(json_names) == 1, f"Expected 1 audit.json in ZIP, got {len(json_names)}"

    # 6. Verify secondary PDF export has strictly 2 pages
    pdf_resp = client.get(f"/api/audits/{audit_id}/report")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    reader = pypdf.PdfReader(io.BytesIO(pdf_resp.content))
    assert len(reader.pages) == 2, f"Expected strictly 2 pages in PDF, got {len(reader.pages)}"
