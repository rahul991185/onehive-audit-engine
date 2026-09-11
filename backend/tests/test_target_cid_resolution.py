import asyncio
import pytest
from pathlib import Path
from pypdf import PdfReader
from app.services.audit_orchestrator import AuditOrchestrator
from app.config import REPORTS_DIR, PREVIEWS_DIR, QUICKWINS_DIR, SALESPACKS_DIR

TARGET_CID_URL = "https://maps.google.com/?cid=8429486214490638391&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQAhgEIAA"

@pytest.mark.asyncio
async def test_target_cid_full_execution():
    """
    MASTER SPECIFICATION SECTION 73 & SECTION 101 ACCEPTANCE TEST:
    Target URL: https://maps.google.com/?cid=8429486214490638391...
    1. Must resolve to verified business ('Dr. Budhiraja')
    2. MUST NEVER resolve to 'Apex Dental & Implant Centre'
    3. Generates complete verified Sales Pack
    4. Asserts all API endpoints serve valid artifacts
    """
    print(f"\n[ACCEPTANCE TEST] Resolving target CID URL: {TARGET_CID_URL}")
    result = await AuditOrchestrator.run(TARGET_CID_URL, is_demo=False)

    # 1. Identity assertion
    assert result is not None
    assert result.is_demo is False
    assert "Budhiraja" in result.business.business_name
    assert "Apex Dental" not in result.business.business_name
    print(f"[ACCEPTANCE TEST] Verified Business Name: {result.business.business_name}")
    print(f"[ACCEPTANCE TEST] Category: {result.business.category}")
    print(f"[ACCEPTANCE TEST] Rating: {result.business.rating}★")

    # 2. Score & Opportunity
    assert result.overall_score > 0
    assert result.top_opportunity is not None
    print(f"[ACCEPTANCE TEST] Overall Score: {result.overall_score}/100")
    print(f"[ACCEPTANCE TEST] #1 Growth Opportunity: {result.top_opportunity.title}")

    # 3. PDF verification
    pdf_matches = list(REPORTS_DIR.glob(f"*{result.audit_id}*.pdf"))
    if not pdf_matches:
        pdf_matches = list(REPORTS_DIR.glob("*budhiraja*.pdf"))
    assert len(pdf_matches) > 0
    pdf_file = pdf_matches[0]

    reader = PdfReader(str(pdf_file))
    assert len(reader.pages) == 5, f"Expected exactly 5 pages, found {len(reader.pages)}"
    print(f"[ACCEPTANCE TEST] PDF Verified: Exactly 5 pages ({pdf_file.name})")

    # 4. Desktop & Mobile preview images
    desktop_png = PREVIEWS_DIR / f"{result.audit_id}_desktop.png"
    mobile_png = PREVIEWS_DIR / f"{result.audit_id}_mobile.png"
    assert desktop_png.exists() and desktop_png.stat().st_size > 5000
    assert mobile_png.exists() and mobile_png.stat().st_size > 5000
    print(f"[ACCEPTANCE TEST] Desktop ({desktop_png.stat().st_size} bytes) & Mobile ({mobile_png.stat().st_size} bytes) concept previews verified")

    # 5. Quick Win & WhatsApp
    assert result.quick_win is not None
    assert len(result.whatsapp_message) > 50
    assert "Dr. Budhiraja" in result.whatsapp_message or "Budhiraja" in result.whatsapp_message

    # 6. Sales Pack ZIP
    zip_matches = list(SALESPACKS_DIR.glob("*budhiraja*.zip"))
    assert len(zip_matches) > 0
    zip_file = zip_matches[0]
    assert zip_file.stat().st_size > 10000
    print(f"[ACCEPTANCE TEST] Complete Growth Pack ZIP generated: {zip_file.name} ({zip_file.stat().st_size} bytes)")

    # 7. Test REST API Endpoints via HTTP against local running backend
    import requests
    base_url = "http://127.0.0.1:8050"

    # Check GET /api/audits/{id}
    res_audit = requests.get(f"{base_url}/api/audits/{result.audit_id}")
    assert res_audit.status_code == 200
    assert res_audit.json()["business"]["business_name"] == result.business.business_name

    # Check GET /api/audits/{id}/report
    res_pdf = requests.get(f"{base_url}/api/audits/{result.audit_id}/report")
    assert res_pdf.status_code == 200
    assert "pdf" in res_pdf.headers.get("content-type", "").lower()

    # Check GET /api/audits/{id}/preview/desktop
    res_desk = requests.get(f"{base_url}/api/audits/{result.audit_id}/preview/desktop")
    assert res_desk.status_code == 200
    assert "image/png" in res_desk.headers.get("content-type", "").lower()

    # Check GET /api/audits/{id}/preview/mobile
    res_mob = requests.get(f"{base_url}/api/audits/{result.audit_id}/preview/mobile")
    assert res_mob.status_code == 200
    assert "image/png" in res_mob.headers.get("content-type", "").lower()

    # Check GET /api/audits/{id}/quick-win
    res_qw = requests.get(f"{base_url}/api/audits/{result.audit_id}/quick-win")
    assert res_qw.status_code == 200

    # Check GET /api/audits/{id}/whatsapp
    res_wa = requests.get(f"{base_url}/api/audits/{result.audit_id}/whatsapp")
    assert res_wa.status_code == 200
    assert "whatsapp_message" in res_wa.json()

    # Check GET /api/audits/{id}/sales-brief
    res_sb = requests.get(f"{base_url}/api/audits/{result.audit_id}/sales-brief")
    assert res_sb.status_code == 200

    # Check GET /api/audits/{id}/sales-pack (ZIP download)
    res_zip = requests.get(f"{base_url}/api/audits/{result.audit_id}/sales-pack")
    assert res_zip.status_code == 200
    assert "zip" in res_zip.headers.get("content-type", "").lower()

    print("\n[ACCEPTANCE TEST COMPLETED SUCCESSFULLY] ALL 7 ARTIFACTS AND ALL 8 REST ENDPOINTS VERIFIED!")

