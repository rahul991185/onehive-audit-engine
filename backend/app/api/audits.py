import os
from typing import Dict, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from app.schemas.audit import AuditRequest, AuditResponse, StructuredAudit
from app.services.classifier import classify_url
from app.services.research.mock_data import generate_mock_audit
from app.services.pdf_generator import generate_5page_pdf
from app.core.config import PDF_DIR

router = APIRouter()

# In-memory store for MVP fast retrieval
AUDIT_STORE: Dict[str, StructuredAudit] = {}
AUDIT_HISTORY: List[StructuredAudit] = []

@router.post("/audit", response_model=AuditResponse)
async def create_audit(request: AuditRequest):
    if not request.url or not request.url.strip():
        raise HTTPException(status_code=400, detail="A valid business URL is required.")
    
    url = request.url.strip()
    source_type = classify_url(url)
    
    # Generate structured audit data
    audit = generate_mock_audit(url, source_type)
    
    # Generate the verified 5-page PDF synchronously so it's immediately ready for viewing/download
    pdf_path, num_pages = await generate_5page_pdf(audit)
    
    audit.report_pdf_url = f"/api/reports/{audit.audit_id}/pdf"
    audit.report_download_url = f"/api/reports/{audit.audit_id}/download"
    
    # Cache in store
    AUDIT_STORE[audit.audit_id] = audit
    AUDIT_HISTORY.insert(0, audit)
    
    return AuditResponse(status="success", audit=audit)

@router.get("/audit/{audit_id}", response_model=AuditResponse)
async def get_audit(audit_id: str):
    if audit_id not in AUDIT_STORE:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return AuditResponse(status="success", audit=AUDIT_STORE[audit_id])

@router.get("/audits", response_model=List[StructuredAudit])
async def list_audits():
    return AUDIT_HISTORY[:15]

@router.get("/reports/{audit_id}/pdf")
async def view_report_pdf(audit_id: str):
    pdf_path = PDF_DIR / f"{audit_id}_report.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF report not found.")
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"{audit_id}_report.pdf",
        content_disposition_type="inline"
    )

@router.get("/reports/{audit_id}/download")
async def download_report_pdf(audit_id: str):
    pdf_path = PDF_DIR / f"{audit_id}_report.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF report not found.")
    
    audit = AUDIT_STORE.get(audit_id)
    business_slug = "Business"
    if audit and audit.business and audit.business.name:
        business_slug = audit.business.name.replace(" ", "_")
    
    filename = f"{business_slug}_OneHive_Digital_Intelligence_Report.pdf"
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=filename,
        content_disposition_type="attachment"
    )
