import asyncio
import json
from app.services.audit_orchestrator import AuditOrchestrator

async def main():
    test_cases = [
        ("Apex Dental", "https://demo.onehive.io/apex-dental", True),
        ("Gyan Dairy", "https://gyandairy.com", False)
    ]
    
    results = {}
    for name, url, is_demo in test_cases:
        print(f"\n==================================================")
        print(f"Running audit for: {name} ({url})")
        print(f"==================================================")
        resp = await AuditOrchestrator.run(url, is_demo=is_demo)
        
        print(f"Business Name: {resp.business.business_name}")
        print(f"Category: {resp.business.category}")
        print(f"Website: {resp.business.website}")
        print(f"Phone: {resp.business.phone}")
        print(f"Overall Score: {resp.overall_score}")
        print(f"Strongest Asset: {resp.strongest_asset}")
        print(f"Biggest Gap: {resp.biggest_gap}")
        print(f"Top Opportunity: {resp.top_opportunity.title}")
        print(f"Current Journey: {resp.top_opportunity.current_journey}")
        print(f"Improved Journey: {resp.top_opportunity.improved_journey}")
        print(f"Dimension Explanations: {json.dumps(resp.scores.dimension_explanations, indent=2)}")
        
        results[name] = {
            "business_name": resp.business.business_name,
            "category": resp.business.category,
            "strongest_asset": resp.strongest_asset,
            "biggest_gap": resp.biggest_gap,
            "current_journey": resp.top_opportunity.current_journey,
            "improved_journey": resp.top_opportunity.improved_journey,
            "explanations": resp.scores.dimension_explanations
        }
    
    # Assert that strongest_asset and biggest_gap are NOT equal between the two businesses
    assert results["Apex Dental"]["strongest_asset"] != results["Gyan Dairy"]["strongest_asset"], "Strongest assets must be distinct!"
    assert results["Apex Dental"]["biggest_gap"] != results["Gyan Dairy"]["biggest_gap"], "Biggest gaps must be distinct!"
    assert results["Apex Dental"]["current_journey"] != results["Gyan Dairy"]["current_journey"], "Current journeys must be distinct!"
    print("\nSUCCESS: All business outputs are highly personalized and distinct!")

if __name__ == "__main__":
    asyncio.run(main())
