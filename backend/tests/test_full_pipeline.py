import asyncio
from app.services.audit_orchestrator import AuditOrchestrator

async def main():
    test_url = "https://maps.google.com/?cid=8429486214490638391&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQAhgEIAA"
    print("Testing real URL pipeline with:", test_url)

    resp = await AuditOrchestrator.run(test_url, is_demo=False)
    
    print("\n--- PIPELINE EXECUTION SUCCESS ---")
    print(f"Audit ID:           {resp.audit_id}")
    print(f"Resolved Business:  {resp.business.business_name}")
    print(f"Category:           {resp.business.category}")
    print(f"Location:           {resp.business.city}")
    print(f"Rating:             {resp.business.rating}★ ({resp.business.review_count} reviews)")
    print(f"Overall Score:      {resp.overall_score}/100")
    print(f"#1 Opportunity:     {resp.top_opportunity.title}")
    print(f"Recommended:        {resp.top_opportunity.recommended_service}")
    print(f"PDF URL:            {resp.report_pdf_url}")
    print(f"Desktop Preview:    {resp.desktop_preview_url}")
    print(f"Mobile Preview:     {resp.mobile_preview_url}")
    print(f"ZIP Pack URL:       {resp.sales_pack_zip_url}")

    # Assertions
    assert resp.business.business_name == "Dr. Budhiraja", f"Expected Dr. Budhiraja, got {resp.business.business_name}!"
    assert "Apex Dental" not in resp.business.business_name, "Error: Demo business leaked into real mode!"
    assert resp.overall_score > 0, "Score should be positive!"
    assert resp.report_pdf_url, "Report PDF URL must exist!"
    assert resp.sales_pack_zip_url, "Sales pack ZIP URL must exist!"
    print("\nALL ASSERTIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
