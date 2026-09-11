import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_lead_prospecting_and_export():
    # 1. Prospect leads
    resp = client.post("/api/leads/prospect", json={
        "niche": "Cosmetic Dental Clinics",
        "location": "Indiranagar, Bengaluru",
        "limit": 3
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["niche"] == "Cosmetic Dental Clinics"
    assert data["location"] == "Indiranagar, Bengaluru"
    assert len(data["leads"]) == 3
    
    first_lead = data["leads"][0]
    assert "business_name" in first_lead
    assert "opportunity_flag" in first_lead
    assert first_lead["opportunity_flag"] in ["NO_WEBSITE", "NO_WHATSAPP", "REVIEW_DEFICIT", "GROWTH_OPPORTUNITY"]
    
    # 2. List leads
    list_resp = client.get("/api/leads?niche=Cosmetic")
    assert list_resp.status_code == 200
    leads = list_resp.json()
    assert len(leads) >= 1
    
    # 3. Export CSV
    csv_resp = client.get("/api/leads/export-csv")
    assert csv_resp.status_code == 200
    assert csv_resp.headers["content-type"].startswith("text/csv")
    csv_text = csv_resp.text
    assert "Lead ID,Business Name,Niche,Location" in csv_text
    assert first_lead["business_name"] in csv_text

    # 4. 1-Click Audit
    lead_id = first_lead["id"]
    audit_resp = client.post(f"/api/leads/{lead_id}/audit")
    assert audit_resp.status_code == 200
    audit_data = audit_resp.json()
    assert "audit_id" in audit_data
    assert "overall_score" in audit_data

    # Verify lead status updated
    updated_leads = client.get(f"/api/leads").json()
    matched = [l for l in updated_leads if l["id"] == lead_id]
    assert len(matched) == 1
    assert matched[0]["status"] == "AUDITED"
    assert matched[0]["audit_id"] == audit_data["audit_id"]
    assert matched[0]["audit_score"] == audit_data["overall_score"]

    # 5. Patch lead to finalized and change stage & notes
    patch_resp = client.patch(f"/api/leads/{lead_id}", json={
        "is_finalized": True,
        "stage": "CONTACTED",
        "notes": "Sent 2-page report via WhatsApp",
        "next_followup": "Tomorrow"
    })
    assert patch_resp.status_code == 200
    patched_lead = patch_resp.json()
    assert patched_lead["is_finalized"] is True
    assert patched_lead["stage"] == "CONTACTED"
    assert patched_lead["notes"] == "Sent 2-page report via WhatsApp"
    assert patched_lead["next_followup"] == "Tomorrow"

    # Query finalized leads
    finalized_leads = client.get("/api/leads?is_finalized=true").json()
    assert any(l["id"] == lead_id for l in finalized_leads)

    # 6. Delete lead
    del_resp = client.delete(f"/api/leads/{lead_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["status"] == "deleted"

    # Verify lead is gone
    after_del = client.get("/api/leads").json()
    assert not any(l["id"] == lead_id for l in after_del)
