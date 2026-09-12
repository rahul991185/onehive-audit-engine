import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, LeadDB
import uuid

client = TestClient(app)

def test_bulk_delete_and_stage_update():
    db = SessionLocal()
    # Create 3 test leads
    id1 = f"TEST-{uuid.uuid4().hex[:8]}"
    id2 = f"TEST-{uuid.uuid4().hex[:8]}"
    id3 = f"TEST-{uuid.uuid4().hex[:8]}"
    
    for lid in [id1, id2, id3]:
        lead = LeadDB(
            id=lid,
            business_name=f"Clinic {lid}",
            niche="Dental",
            location="Bengaluru",
            category="Dentist",
            opportunity_flag="NO_WEBSITE",
            opportunity_summary="Missing digital presence",
            stage="PITCH_READY"
        )
        db.add(lead)
    db.commit()
    db.close()

    # Test 1: Bulk stage update id1 and id2 to CONTACTED
    res_stage = client.post("/api/leads/bulk-stage", json={
        "lead_ids": [id1, id2],
        "stage": "CONTACTED"
    })
    assert res_stage.status_code == 200
    data_stage = res_stage.json()
    assert data_stage["status"] == "updated"
    assert data_stage["updated_count"] == 2

    # Verify stage in DB
    db = SessionLocal()
    l1 = db.query(LeadDB).filter(LeadDB.id == id1).first()
    l3 = db.query(LeadDB).filter(LeadDB.id == id3).first()
    assert l1.stage == "CONTACTED"
    assert l3.stage == "PITCH_READY"
    db.close()

    # Test 2: Bulk delete all 3 test leads
    res_del = client.post("/api/leads/bulk-delete", json={
        "lead_ids": [id1, id2, id3]
    })
    assert res_del.status_code == 200
    data_del = res_del.json()
    assert data_del["status"] == "deleted"
    assert data_del["deleted_count"] == 3

    # Verify deletion in DB
    db = SessionLocal()
    remaining = db.query(LeadDB).filter(LeadDB.id.in_([id1, id2, id3])).all()
    assert len(remaining) == 0
    db.close()
