import csv
import io
import json
import os
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse
from app.models.schemas import (
    AuditRequest, AuditResponse, BusinessIdentity, AuditScore, Opportunity,
    WebsiteConcept, QuickWin, SalesBrief, Recommendation,
    LeadProspectRequest, LeadItem, LeadProspectResponse, LeadUpdateRequest
)
from app.services.audit_orchestrator import AuditOrchestrator
from app.services.lead_prospector_engine import LeadProspectorEngine
from app.database import SessionLocal, AuditDB, LeadDB
from app.config import REPORTS_DIR, PREVIEWS_DIR, QUICKWINS_DIR, SALESPACKS_DIR, IMAGEPACKS_DIR, VISUAL_QA_DIR

router = APIRouter()

# Memory cache for active session fast access
MEMORY_AUDITS = {}

@router.post("/audits", response_model=AuditResponse)
@router.post("/audit", response_model=AuditResponse)
async def create_audit(req: AuditRequest):
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail="A valid URL is required.")
    
    audit_resp = await AuditOrchestrator.run(req.url.strip(), is_demo=req.is_demo)
    MEMORY_AUDITS[audit_resp.audit_id] = audit_resp
    return audit_resp

@router.get("/audits", response_model=List[dict])
async def list_recent_audits():
    db = SessionLocal()
    records = db.query(AuditDB).order_by(AuditDB.created_at.desc()).limit(20).all()
    results = []
    for r in records:
        results.append({
            "audit_id": r.id,
            "created_at": r.created_at.strftime("%B %d, %Y") if r.created_at else "",
            "business_name": r.business_name,
            "industry": r.industry or "Local Business",
            "location": r.location or "Local Area",
            "overall_score": r.overall_score,
            "status": r.status,
            "is_demo": r.is_demo,
            "source_url": r.source_url
        })
    db.close()
    return results

@router.get("/audits/{audit_id}", response_model=AuditResponse)
async def get_audit(audit_id: str):
    if audit_id in MEMORY_AUDITS:
        return MEMORY_AUDITS[audit_id]
    
    # Check DB
    db = SessionLocal()
    r = db.query(AuditDB).filter(AuditDB.id == audit_id).first()
    db.close()
    if not r:
        raise HTTPException(status_code=404, detail="Audit not found.")
    
    # Rehydrate AuditResponse from DB record
    try:
        scores_data = json.loads(r.scores_json) if r.scores_json else {}
        opp_data = json.loads(r.opportunity_json) if r.opportunity_json else {}
        concept_data = json.loads(r.website_concept_json) if r.website_concept_json else {}
        quick_win_data = json.loads(r.quick_win_json) if r.quick_win_json else {}
        sales_brief_data = json.loads(r.sales_brief_json) if r.sales_brief_json else {}

        business = BusinessIdentity(
            business_name=r.business_name,
            category=r.industry or "Local Business",
            address=r.location,
            source_url=r.source_url,
            resolved_url=r.resolved_url,
            identity_confidence=r.identity_confidence or 0.9,
            verified=True,
            is_demo=r.is_demo or False
        )

        resp = AuditResponse(
            audit_id=r.id,
            created_at=r.created_at.strftime("%B %d, %Y") if r.created_at else "",
            business=business,
            overall_score=r.overall_score or 0,
            scores=AuditScore(**scores_data) if scores_data else AuditScore(
                overall_score=r.overall_score or 0,
                discoverability=15, brand_identity=10, trust_reputation=15, website_experience=10, lead_conversion=10, social_presence=5
            ),
            strongest_asset=opp_data.get("strongest_asset") or opp_data.get("why_it_matters", "Verified Local Presence"),
            biggest_gap=opp_data.get("biggest_gap") or opp_data.get("finding", "Conversion friction"),
            attention_callout="We've identified one area we believe deserves immediate attention.",
            top_opportunity=Opportunity(**opp_data) if opp_data else Opportunity(
                title="Optimize Lead Conversion",
                priority="HIGH",
                finding="No clear conversion CTA",
                why_it_matters="High-intent visitors encounter friction",
                current_journey="Discovery -> Site -> Friction",
                improved_journey="Discovery -> CTA -> Enquiry",
                recommended_service="Conversion Architecture",
                confidence=0.95
            ),
            recommendations=[],
            website_concept=WebsiteConcept(**concept_data) if concept_data else WebsiteConcept(
                business_name=r.business_name, industry=r.industry or "Business", location=r.location or "City",
                headline="Modern Business Experience", subheadline="Capturing local enquiries",
                primary_cta="Enquire Now", secondary_cta="Learn More", services=[], trust_signals=[],
                whatsapp_cta="Chat with us", final_cta="Book Now"
            ),
            quick_win=QuickWin(**quick_win_data) if quick_win_data else QuickWin(
                title="WhatsApp Enquiry Flow", category="Lead Conversion",
                why_chosen="Instant lead capture", ready_to_use_asset="Hello! How can we assist you today?",
                instructions="Deploy on WhatsApp Business", asset_format="text"
            ),
            whatsapp_message=r.whatsapp_message or "Hello! We reviewed your digital presence.",
            sales_brief=SalesBrief(**sales_brief_data) if sales_brief_data else SalesBrief(
                business_name=r.business_name, industry=r.industry or "Business", location=r.location or "City",
                identity_confidence="HIGH", overall_score=r.overall_score or 0,
                scores=AuditScore(overall_score=r.overall_score or 0, discoverability=15, brand_identity=10, trust_reputation=15, website_experience=10, lead_conversion=10, social_presence=5),
                strongest_asset="Reputation", biggest_gap="Lead Conversion",
                top_opportunity="Capture High Intent Inbound", why_it_matters="Reduces friction",
                evidence_highlights=[], recommended_service="Lead Engine", likely_buying_trigger="Low inbound conversion",
                sales_angle="Consultative Diagnosis", opening_message="Hello!", objection_to_expect="Already busy",
                objection_response="Streamlines existing demand", recommended_next_step="Send visual teaser"
            ),
            report_pdf_url=f"/api/audits/{r.id}/report",
            report_download_url=f"/api/audits/{r.id}/report?download=true",
            report_page_1_url=f"/api/audits/{r.id}/images/1",
            report_page_2_url=f"/api/audits/{r.id}/images/2",
            desktop_preview_url=f"/api/audits/{r.id}/preview/desktop",
            mobile_preview_url=f"/api/audits/{r.id}/preview/mobile",
            quick_win_url=f"/api/audits/{r.id}/quick-win",
            sales_pack_zip_url=f"/api/audits/{r.id}/sales-pack",
            image_pack_urls=[f"/api/audits/{r.id}/images/{i+1}" for i in range(2)],
            image_pack_zip_url=f"/api/audits/{r.id}/image-pack-zip",
            digital_pack_zip_url=f"/api/audits/{r.id}/image-pack-zip",
            contact_sheet_url=f"/api/audits/{r.id}/contact-sheet",
            status="COMPLETED",
            is_demo=r.is_demo or False
        )
        MEMORY_AUDITS[r.id] = resp
        return resp
    except Exception as e:
        print(f"[get_audit] Error rehydrating: {e}")
        raise HTTPException(status_code=500, detail="Error rehydrating audit data.")

@router.get("/audits/{audit_id}/report")
@router.get("/reports/{audit_id}/download")
async def get_report_pdf(audit_id: str, download: bool = Query(False)):
    # Find PDF in reports dir
    candidates = list(REPORTS_DIR.glob(f"*{audit_id}*.pdf"))
    if not candidates:
        db = SessionLocal()
        record = db.query(AuditDB).filter(AuditDB.id == audit_id).first()
        db.close()
        if record and record.report_pdf_path and Path(record.report_pdf_path).exists():
            candidates = [Path(record.report_pdf_path)]
    
    if not candidates or not candidates[0].exists():
        raise HTTPException(status_code=404, detail="PDF report artifact not found.")

    pdf_file = candidates[0]
    filename = pdf_file.name
    disposition = "attachment" if download else "inline"

    return FileResponse(
        path=str(pdf_file),
        media_type="application/pdf",
        filename=filename,
        content_disposition_type=disposition
    )

@router.get("/audits/{audit_id}/preview/desktop")
async def get_desktop_preview(audit_id: str):
    path = PREVIEWS_DIR / f"{audit_id}_desktop.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Desktop preview not found.")
    return FileResponse(path=str(path), media_type="image/png")

@router.get("/audits/{audit_id}/preview/mobile")
async def get_mobile_preview(audit_id: str):
    path = PREVIEWS_DIR / f"{audit_id}_mobile.png"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Mobile preview not found.")
    return FileResponse(path=str(path), media_type="image/png")

@router.get("/audits/{audit_id}/quick-win")
async def get_quick_win(audit_id: str, format: Optional[str] = Query(None)):
    if format == "json" or audit_id in MEMORY_AUDITS:
        if audit_id in MEMORY_AUDITS:
            return JSONResponse(MEMORY_AUDITS[audit_id].quick_win.model_dump() if hasattr(MEMORY_AUDITS[audit_id].quick_win, 'model_dump') else MEMORY_AUDITS[audit_id].quick_win.dict())
    path = QUICKWINS_DIR / f"{audit_id}_quick_win.txt"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Quick win asset not found.")
    return FileResponse(path=str(path), media_type="text/plain", filename="onehive_quick_win.txt", content_disposition_type="attachment")

@router.get("/audits/{audit_id}/whatsapp")
async def get_whatsapp_message(audit_id: str):
    if audit_id in MEMORY_AUDITS:
        return {"whatsapp_message": MEMORY_AUDITS[audit_id].whatsapp_message}
    
    db = SessionLocal()
    record = db.query(AuditDB).filter(AuditDB.id == audit_id).first()
    db.close()
    if record and record.whatsapp_message:
        return {"whatsapp_message": record.whatsapp_message}
    raise HTTPException(status_code=404, detail="WhatsApp message not found for this audit.")

@router.get("/audits/{audit_id}/sales-brief")
async def get_sales_brief(audit_id: str, format: Optional[str] = Query(None)):
    if format == "json" or audit_id in MEMORY_AUDITS:
        if audit_id in MEMORY_AUDITS:
            return JSONResponse(MEMORY_AUDITS[audit_id].sales_brief.model_dump() if hasattr(MEMORY_AUDITS[audit_id].sales_brief, 'model_dump') else MEMORY_AUDITS[audit_id].sales_brief.dict())
    path = SALESPACKS_DIR / f"{audit_id}_sales_brief.txt"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Sales brief not found.")
    return FileResponse(path=str(path), media_type="text/plain", filename="onehive_sales_brief.txt", content_disposition_type="attachment")

@router.get("/audits/{audit_id}/sales-pack")
async def download_sales_pack(audit_id: str):
    # Find matching ZIP
    candidates = list(SALESPACKS_DIR.glob(f"*{audit_id}*.zip"))
    if not candidates:
        db = SessionLocal()
        record = db.query(AuditDB).filter(AuditDB.id == audit_id).first()
        db.close()
        if record and record.sales_pack_zip_path and Path(record.sales_pack_zip_path).exists():
            candidates = [Path(record.sales_pack_zip_path)]

    if not candidates or not candidates[0].exists():
        raise HTTPException(status_code=404, detail="Sales pack archive not found.")

    zip_file = candidates[0]
    return FileResponse(
        path=str(zip_file),
        media_type="application/zip",
        filename=zip_file.name,
        content_disposition_type="attachment"
    )

PAGE_FILENAMES = {
    1: "01-page1.png",
    2: "02-page2.png"
}

@router.get("/audits/{audit_id}/images/{page_num}")
async def get_audit_image_page(audit_id: str, page_num: int, download: bool = False):
    if page_num not in PAGE_FILENAMES:
        raise HTTPException(status_code=400, detail="Page number must be between 1 and 2.")
    
    filename = PAGE_FILENAMES[page_num]
    candidates = list(IMAGEPACKS_DIR.glob(f"**/{filename}"))
    
    audit_obj = MEMORY_AUDITS.get(audit_id)
    if audit_obj:
        safe_slug = "".join(c if c.isalnum() else "_" for c in audit_obj.business.business_name.lower())[:30].strip("_")
        specific = IMAGEPACKS_DIR / safe_slug / filename
        if specific.exists():
            candidates = [specific]
    else:
        db = SessionLocal()
        r = db.query(AuditDB).filter(AuditDB.id == audit_id).first()
        db.close()
        if r:
            safe_slug = "".join(c if c.isalnum() else "_" for c in r.business_name.lower())[:30].strip("_")
            specific = IMAGEPACKS_DIR / safe_slug / filename
            if specific.exists():
                candidates = [specific]

    if not candidates or not candidates[0].exists():
        raise HTTPException(status_code=404, detail=f"Image for page {page_num} not found.")

    img_file = candidates[0]
    disposition = "attachment" if download else "inline"
    return FileResponse(
        path=str(img_file),
        media_type="image/png",
        filename=filename,
        content_disposition_type=disposition
    )

@router.get("/audits/{audit_id}/contact-sheet")
async def get_audit_contact_sheet(audit_id: str):
    audit_obj = MEMORY_AUDITS.get(audit_id)
    if audit_obj:
        safe_slug = "".join(c if c.isalnum() else "_" for c in audit_obj.business.business_name.lower())[:30].strip("_")
        path = VISUAL_QA_DIR / f"{safe_slug}_contact_sheet.png"
        if path.exists():
            return FileResponse(path=str(path), media_type="image/png")
            
    candidates = list(VISUAL_QA_DIR.glob("*contact_sheet.png"))
    if candidates and candidates[0].exists():
        return FileResponse(path=str(candidates[0]), media_type="image/png")
    
    raise HTTPException(status_code=404, detail="Contact sheet not found.")

@router.get("/audits/{audit_id}/image-pack-zip")
async def download_image_pack_zip(audit_id: str):
    audit_obj = MEMORY_AUDITS.get(audit_id)
    if audit_obj:
        safe_slug = "".join(c if c.isalnum() else "_" for c in audit_obj.business.business_name.lower())[:30].strip("_")
        zip_path = IMAGEPACKS_DIR / f"onehive-{safe_slug}-digital-presence-pack.zip"
        if zip_path.exists():
            return FileResponse(
                path=str(zip_path),
                media_type="application/zip",
                filename=zip_path.name,
                content_disposition_type="attachment"
            )

    candidates = list(IMAGEPACKS_DIR.glob("*.zip"))
    if not candidates:
        raise HTTPException(status_code=404, detail="Image pack archive not found.")

    zip_file = candidates[0]
    return FileResponse(
        path=str(zip_file),
        media_type="application/zip",
        filename=zip_file.name,
        content_disposition_type="attachment"
    )

# -------------------------------------------------------------
# LEAD PROSPECTOR & PIPELINE ENGINE ENDPOINTS
# -------------------------------------------------------------

@router.post("/leads/prospect", response_model=LeadProspectResponse)
async def prospect_leads(req: LeadProspectRequest):
    if not req.niche or not req.niche.strip():
        raise HTTPException(status_code=400, detail="Niche category is required.")
    if not req.location or not req.location.strip():
        raise HTTPException(status_code=400, detail="Location / City is required.")
    
    return await LeadProspectorEngine.prospect(
        niche=req.niche.strip(),
        location=req.location.strip(),
        limit=req.limit or 10,
        webhook_url=req.webhook_url
    )

@router.get("/leads", response_model=List[LeadItem])
async def list_leads(
    niche: Optional[str] = None, 
    location: Optional[str] = None, 
    status: Optional[str] = None,
    is_finalized: Optional[bool] = None,
    stage: Optional[str] = None
):
    db = SessionLocal()
    query = db.query(LeadDB)
    if niche:
        query = query.filter(LeadDB.niche.ilike(f"%{niche}%"))
    if location:
        query = query.filter(LeadDB.location.ilike(f"%{location}%"))
    if status:
        query = query.filter(LeadDB.status == status)
    if is_finalized is not None:
        query = query.filter(LeadDB.is_finalized == is_finalized)
    if stage:
        query = query.filter(LeadDB.stage == stage)
    
    records = query.order_by(LeadDB.created_at.desc()).limit(150).all()
    
    results = []
    for r in records:
        clean_digits = "".join(filter(str.isdigit, r.phone or ""))
        whatsapp_link = None
        if len(clean_digits) >= 10:
            pitch_msg = (
                f"Hi {r.business_name}, I reviewed your digital presence in {r.location}. "
                f"We created a custom 2-Page Digital Presence Intelligence Report for your business highlighting immediate growth opportunities. "
                f"May I share the report here?"
            )
            whatsapp_link = f"https://wa.me/{clean_digits}?text={urllib.parse.quote(pitch_msg)}"

        results.append(LeadItem(
            id=r.id,
            created_at=r.created_at.strftime("%B %d, %Y") if r.created_at else "",
            business_name=r.business_name,
            niche=r.niche or "",
            location=r.location or "",
            category=r.category or "",
            phone=r.phone,
            website=r.website,
            maps_url=r.maps_url,
            rating=r.rating,
            review_count=r.review_count,
            opportunity_flag=r.opportunity_flag or "GROWTH_OPPORTUNITY",
            opportunity_summary=r.opportunity_summary or "",
            status=r.status or "NEW",
            audit_id=r.audit_id,
            audit_score=r.audit_score,
            whatsapp_pitch_link=whatsapp_link,
            is_finalized=r.is_finalized or False,
            stage=r.stage or "PITCH_READY",
            notes=r.notes,
            next_followup=r.next_followup,
            last_contacted=r.last_contacted
        ))
    db.close()
    return results

@router.patch("/leads/{lead_id}", response_model=LeadItem)
async def update_lead(lead_id: str, req: LeadUpdateRequest):
    db = SessionLocal()
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
    if not lead:
        db.close()
        raise HTTPException(status_code=404, detail="Lead not found.")

    if req.is_finalized is not None:
        lead.is_finalized = req.is_finalized
    if req.stage is not None:
        lead.stage = req.stage
    if req.notes is not None:
        lead.notes = req.notes
    if req.next_followup is not None:
        lead.next_followup = req.next_followup
    if req.last_contacted is not None:
        lead.last_contacted = req.last_contacted
    if req.status is not None:
        lead.status = req.status

    db.commit()
    db.refresh(lead)

    clean_digits = "".join(filter(str.isdigit, lead.phone or ""))
    whatsapp_link = None
    if len(clean_digits) >= 10:
        pitch_msg = (
            f"Hi {lead.business_name}, I reviewed your digital presence in {lead.location}. "
            f"We created a custom 2-Page Digital Presence Intelligence Report for your business highlighting immediate growth opportunities. "
            f"May I share the report here?"
        )
        whatsapp_link = f"https://wa.me/{clean_digits}?text={urllib.parse.quote(pitch_msg)}"

    item = LeadItem(
        id=lead.id,
        created_at=lead.created_at.strftime("%B %d, %Y") if lead.created_at else "",
        business_name=lead.business_name,
        niche=lead.niche or "",
        location=lead.location or "",
        category=lead.category or "",
        phone=lead.phone,
        website=lead.website,
        maps_url=lead.maps_url,
        rating=lead.rating,
        review_count=lead.review_count,
        opportunity_flag=lead.opportunity_flag or "GROWTH_OPPORTUNITY",
        opportunity_summary=lead.opportunity_summary or "",
        status=lead.status or "NEW",
        audit_id=lead.audit_id,
        audit_score=lead.audit_score,
        whatsapp_pitch_link=whatsapp_link,
        is_finalized=lead.is_finalized or False,
        stage=lead.stage or "PITCH_READY",
        notes=lead.notes,
        next_followup=lead.next_followup,
        last_contacted=lead.last_contacted
    )
    db.close()
    return item

@router.delete("/leads/{lead_id}")
async def delete_lead(lead_id: str):
    db = SessionLocal()
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
    if not lead:
        db.close()
        raise HTTPException(status_code=404, detail="Lead not found.")

    db.delete(lead)
    db.commit()
    db.close()
    return {"status": "deleted", "lead_id": lead_id}

@router.get("/leads/export-csv")
async def export_leads_csv(niche: Optional[str] = None, location: Optional[str] = None):
    db = SessionLocal()
    query = db.query(LeadDB)
    if niche:
        query = query.filter(LeadDB.niche.ilike(f"%{niche}%"))
    if location:
        query = query.filter(LeadDB.location.ilike(f"%{location}%"))
    records = query.order_by(LeadDB.created_at.desc()).limit(200).all()
    db.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Lead ID", "Business Name", "Niche", "Location", "Phone", "Website",
        "Rating", "Reviews", "Opportunity Trigger", "Consultative Strategy",
        "Pipeline Status", "OneHive Audit Score", "Report Viewer Link", "Google Maps URL"
    ])

    for r in records:
        report_link = f"http://localhost:3001/api/audits/{r.audit_id}/report" if r.audit_id else "Not Audited Yet"
        writer.writerow([
            r.id,
            r.business_name,
            r.niche,
            r.location,
            r.phone or "N/A",
            r.website or "NO WEBSITE (High Value Opportunity)",
            r.rating or "N/A",
            r.review_count or 0,
            r.opportunity_flag,
            r.opportunity_summary,
            r.status,
            r.audit_score or "Pending",
            report_link,
            r.maps_url or "N/A"
        ])

    csv_content = output.getvalue()
    filename = f"onehive_leads_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/leads/{lead_id}/audit", response_model=AuditResponse)
async def audit_lead(lead_id: str):
    db = SessionLocal()
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
    if not lead:
        db.close()
        raise HTTPException(status_code=404, detail="Lead not found.")

    target_url = lead.website or lead.maps_url
    if not target_url:
        db.close()
        raise HTTPException(status_code=400, detail="Lead has no valid website or Google Maps URL to audit.")

    db.close()

    # Run audit
    audit_resp = await AuditOrchestrator.run(target_url, is_demo=False)
    MEMORY_AUDITS[audit_resp.audit_id] = audit_resp

    # Update Lead record
    db = SessionLocal()
    lead = db.query(LeadDB).filter(LeadDB.id == lead_id).first()
    if lead:
        lead.status = "AUDITED"
        lead.audit_id = audit_resp.audit_id
        lead.audit_score = audit_resp.overall_score
        db.commit()
    db.close()

    return audit_resp

