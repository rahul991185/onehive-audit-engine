import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import HTTPException
from app.models.schemas import AuditResponse
from app.services.identity_resolver import IdentityResolver
from app.services.scoring_engine import ScoringEngine
from app.services.opportunity_engine import OpportunityEngine
from app.services.website_preview_engine import WebsitePreviewEngine
from app.services.quick_win_engine import QuickWinEngine
from app.services.whatsapp_engine import WhatsAppEngine
from app.services.sales_brief_engine import SalesBriefEngine
from app.services.sales_pack_engine import SalesPackEngine
from app.pdf.renderer import PDFRenderer
from app.pdf.image_pack_renderer import ImagePackRenderer
from app.database import SessionLocal, AuditDB

class AuditOrchestrator:
    """
    End-to-End Orchestrator executing the complete OneHive Digital Growth Pack pipeline.
    """

    @staticmethod
    async def run(url: str, is_demo: bool = False) -> AuditResponse:
        audit_id = f"OH-AUDIT-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        # 1. Identity Resolution & Evidence Collection
        identity, evidence, extra_data = await IdentityResolver.resolve(url, is_demo=is_demo)

        if not identity or not identity.verified:
            raise HTTPException(
                status_code=422,
                detail="Business identification could not be verified from this URL. Please provide a direct Google Maps place link, website URL, or social business profile."
            )

        # 2. Deterministic Scoring
        scores = ScoringEngine.calculate(identity, evidence)

        # 3. Opportunity Isolation
        strongest_asset, biggest_gap, opp, recs = OpportunityEngine.evaluate(identity, scores, evidence, extra_data=extra_data)

        # 4. Website Concept & Screenshot Rendering (Desktop 1440px & Mobile 390px - Unbundled Stage 2 Asset)
        concept = WebsitePreviewEngine.build_concept(identity, scores, opp)
        desktop_png, mobile_png = await WebsitePreviewEngine.render_previews(audit_id, concept)

        # 5. Quick Win Generation
        quick_win, quick_win_path = QuickWinEngine.generate(audit_id, identity, opp)

        # 6. WhatsApp Outreach Copy
        whatsapp_msg = WhatsAppEngine.generate(identity, opp)

        # 7. Internal Sales Intelligence Brief
        sales_brief, sales_brief_path = SalesBriefEngine.generate(
            audit_id=audit_id,
            identity=identity,
            scores=scores,
            strongest_asset=strongest_asset,
            biggest_gap=biggest_gap,
            opp=opp
        )

        audit_dict = {
            "audit_id": audit_id,
            "business": identity.dict(),
            "overall_score": scores.overall_score,
            "scores": scores.dict(),
            "top_opportunity": opp.dict(),
            "recommendations": [r.dict() for r in recs],
            "quick_win": quick_win.dict(),
            "created_at": datetime.utcnow().isoformat()
        }

        # 8. Primary Deliverable: 2 High-Resolution PNG Pages + Client ZIP + QA Contact Sheet + Secondary PDF
        image_paths, digital_pack_zip, contact_sheet_path, pdf_path, is_valid, pdf_errors = await ImagePackRenderer.render(
            audit_id=audit_id,
            identity=identity,
            scores=scores,
            strongest_asset=strongest_asset,
            biggest_gap=biggest_gap,
            opp=opp,
            recommendations=recs,
            audit_dict=audit_dict,
            evidence=evidence,
            extra_data=extra_data
        )

        if not is_valid:
            print(f"[AuditOrchestrator] Warning: PDF QA encountered issues: {pdf_errors}")

        # 9. Build Complete Internal Sales Pack ZIP
        zip_path = SalesPackEngine.build_zip(
            audit_id=audit_id,
            safe_name=identity.business_name,
            report_pdf_path=pdf_path,
            desktop_preview_path=desktop_png,
            mobile_preview_path=mobile_png,
            quick_win_path=quick_win_path,
            sales_brief_path=sales_brief_path,
            whatsapp_text=whatsapp_msg,
            audit_dict=audit_dict
        )

        # 10. Persist to Database
        try:
            opp_dict = opp.model_dump() if hasattr(opp, 'model_dump') else opp.dict()
            opp_dict["strongest_asset"] = strongest_asset
            opp_dict["biggest_gap"] = biggest_gap

            db = SessionLocal()
            db_record = AuditDB(
                id=audit_id,
                source_url=url,
                resolved_url=identity.resolved_url,
                source_type=identity.source_url,
                business_name=identity.business_name,
                industry=identity.category,
                location=identity.city or identity.address,
                overall_score=scores.overall_score,
                identity_confidence=identity.identity_confidence,
                status="COMPLETED",
                is_demo=is_demo,
                scores_json=json.dumps(scores.model_dump() if hasattr(scores, 'model_dump') else scores.dict()),
                evidence_json=json.dumps([e.model_dump() if hasattr(e, 'model_dump') else e.dict() for e in evidence]),
                opportunity_json=json.dumps(opp_dict),
                website_concept_json=json.dumps(concept.model_dump() if hasattr(concept, 'model_dump') else concept.dict()),
                quick_win_json=json.dumps(quick_win.model_dump() if hasattr(quick_win, 'model_dump') else quick_win.dict()),
                sales_brief_json=json.dumps(sales_brief.model_dump() if hasattr(sales_brief, 'model_dump') else sales_brief.dict()),
                report_pdf_path=str(pdf_path),
                desktop_preview_path=str(desktop_png),
                mobile_preview_path=str(mobile_png),
                quick_win_path=str(quick_win_path),
                sales_pack_zip_path=str(zip_path),
                whatsapp_message=whatsapp_msg
            )
            db.add(db_record)
            db.commit()
            db.close()
        except Exception as e:
            print(f"[AuditOrchestrator] DB Save Note: {e}")

        # Return full response with all asset URLs
        return AuditResponse(
            audit_id=audit_id,
            created_at=datetime.now().strftime("%B %d, %Y"),
            business=identity,
            overall_score=scores.overall_score,
            scores=scores,
            strongest_asset=strongest_asset,
            biggest_gap=biggest_gap,
            attention_callout="We've identified one area we believe deserves immediate attention.",
            top_opportunity=opp,
            recommendations=recs,
            website_concept=concept,
            quick_win=quick_win,
            whatsapp_message=whatsapp_msg,
            sales_brief=sales_brief,
            report_pdf_url=f"/api/audits/{audit_id}/report",
            report_download_url=f"/api/audits/{audit_id}/report?download=true",
            report_page_1_url=f"/api/audits/{audit_id}/images/1",
            report_page_2_url=f"/api/audits/{audit_id}/images/2",
            desktop_preview_url=f"/api/audits/{audit_id}/preview/desktop",
            mobile_preview_url=f"/api/audits/{audit_id}/preview/mobile",
            quick_win_url=f"/api/audits/{audit_id}/quick-win",
            sales_pack_zip_url=f"/api/audits/{audit_id}/sales-pack",
            image_pack_urls=[f"/api/audits/{audit_id}/images/{i+1}" for i in range(2)],
            image_pack_zip_url=f"/api/audits/{audit_id}/image-pack-zip",
            digital_pack_zip_url=f"/api/audits/{audit_id}/image-pack-zip",
            contact_sheet_url=f"/api/audits/{audit_id}/contact-sheet",
            status="COMPLETED",
            is_demo=is_demo,
            business_type=scores.business_type,
            maturity_band=scores.maturity_band,
            commercial_tier=scores.commercial_tier
        )
