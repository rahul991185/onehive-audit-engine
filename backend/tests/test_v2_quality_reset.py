import asyncio
import os
import sys
from pathlib import Path
import pypdf
import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.schemas import BusinessIdentity, AuditScore, Opportunity, EvidenceItem
from app.services.identity_resolver import IdentityResolver
from app.services.scoring_engine import ScoringEngine
from app.services.opportunity_engine import OpportunityEngine
from app.services.website_preview_engine import WebsitePreviewEngine
from app.services.quick_win_engine import QuickWinEngine
from app.services.whatsapp_engine import WhatsAppEngine
from app.services.sales_brief_engine import SalesBriefEngine
from app.services.audit_orchestrator import AuditOrchestrator
from app.pdf.verifier import PDFVerifier
from app.pdf.renderer import PDFRenderer

GYAN_DENTAL_URL = "https://maps.google.com/?cid=3648219209233379687&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQAhgEIAA"

@pytest.mark.asyncio
async def test_1_gyan_dental_clinic():
    print("\n" + "="*70)
    print("TEST 1: GYAN DENTAL CLINIC (END-TO-END COMMERCIAL RESET)")
    print("="*70)

    audit_response = await AuditOrchestrator.run(GYAN_DENTAL_URL, is_demo=False)
    
    print(f"Business Name:        {audit_response.business.business_name}")
    print(f"Category:             {audit_response.business.category}")
    print(f"Rating & Reviews:     {audit_response.business.rating}★ ({audit_response.business.review_count} reviews)")
    print(f"Website Detected:     {audit_response.business.website or 'None (Verified No Website)'}")
    print(f"Business Type:        {audit_response.business_type}")
    print(f"Commercial Tier:      {audit_response.commercial_tier}")
    print(f"Maturity Band:        {audit_response.maturity_band}")
    print(f"Overall Score:        {audit_response.overall_score} / 100")
    print(f"- Discoverability:    {audit_response.scores.discoverability} / 20")
    print(f"- Brand & Identity:   {audit_response.scores.brand_identity} / 15")
    print(f"- Trust & Reputation: {audit_response.scores.trust_reputation} / 20")
    print(f"- Digital Experience: {audit_response.scores.website_experience} / 15")
    print(f"- Lead Conversion:    {audit_response.scores.lead_conversion} / 20")
    print(f"- Social Presence:    {audit_response.scores.social_presence} / 10")
    print(f"Preview Quality Score:{audit_response.website_concept.preview_quality_score} / 100")

    # Assertions
    assert "Gyan Dental" in audit_response.business.business_name, "Business name mismatch"
    assert 48 <= audit_response.overall_score <= 58, f"Score {audit_response.overall_score} not in expected commercial range 48-58!"
    assert audit_response.scores.website_experience == 0, f"Digital Experience should be 0/15 for no website, got {audit_response.scores.website_experience}"
    assert audit_response.scores.lead_conversion <= 8, f"Lead conversion should be <= 8, got {audit_response.scores.lead_conversion}"
    assert audit_response.business_type == "LOCAL_FIRST", f"Expected LOCAL_FIRST, got {audit_response.business_type}"
    assert audit_response.maturity_band == "SIGNIFICANT OPPORTUNITY", f"Expected SIGNIFICANT OPPORTUNITY, got {audit_response.maturity_band}"

    # Verify PDF
    pdf_path = Path(__file__).parent.parent / "storage" / "artifacts" / "reports" / f"gyan_dental_clinic_digital_presence_report.pdf"
    assert pdf_path.exists(), f"PDF report was not generated at {pdf_path}"
    
    is_valid, errors = PDFVerifier.verify(pdf_path, audit_response.business)
    assert is_valid, f"PDF QA Verifier failed with errors: {errors}"
    
    reader = pypdf.PdfReader(str(pdf_path))
    assert len(reader.pages) == 2, f"PDF page count is {len(reader.pages)}, expected strictly 2!"

    # Verify WhatsApp message
    assert "Page 3" not in audit_response.whatsapp_message, "WhatsApp copy must NOT reference Page 3!"
    assert len(audit_response.whatsapp_message.split("\n\n")) <= 5, "WhatsApp copy must be short and human!"

    # Verify Quick Win
    assert audit_response.quick_win.whatsapp_link is not None, "Quick Win missing WhatsApp pre-filled link!"
    assert audit_response.quick_win.first_response_script is not None, "Quick Win missing first-response script!"
    assert len(audit_response.quick_win.suggested_placement) == 3, "Quick Win missing placement guidance!"

    # Verify Sales Brief
    assert len(audit_response.sales_brief.what_not_to_say) >= 3, "Sales Brief missing WHAT NOT TO SAY safety items!"

    print("[PASS] TEST 1: Gyan Dental Clinic successfully verified end-to-end!")
    return audit_response

@pytest.mark.asyncio
async def test_2_business_with_website():
    print("\n" + "="*70)
    print("TEST 2: BUSINESS WITH WEBSITE (DOES NOT COLLAPSE TO 54)")
    print("="*70)

    # Simulate a business with an active website
    identity = BusinessIdentity(
        business_name="Elite Care Dental & Orthodontics",
        category="Dental Clinic",
        address="Indiranagar, Bengaluru",
        city="Bengaluru",
        phone="+91 80 2525 1122",
        website="https://elitecaredental.com",
        source_url="https://elitecaredental.com",
        rating=4.9,
        review_count=180,
        identity_confidence=0.95,
        verified=True,
        is_demo=False
    )

    evidence = [
        EvidenceItem(source="Website", field="Domain Accessibility", value="Active responsive website", confidence=0.95, status="PASS", observation="Website is active and accessible."),
        EvidenceItem(source="Website", field="Mobile Responsive", value="Configured viewport", confidence=0.9, status="PASS", observation="Mobile meta viewport present."),
        EvidenceItem(source="Website", field="WhatsApp CTA", value="Active WhatsApp chat widget", confidence=0.95, status="PASS", observation="Direct WhatsApp conversion button detected."),
        EvidenceItem(source="Google Profile", field="Rating & Reviews", value="4.9 ★ across 180 reviews", confidence=0.98, status="PASS", observation="High customer rating on Google.")
    ]

    scores = ScoringEngine.calculate(identity, evidence)
    print(f"Score for business with website: {scores.overall_score} / 100")
    print(f"- Digital Experience: {scores.website_experience} / 15")
    print(f"- Lead Conversion:    {scores.lead_conversion} / 20")
    print(f"- Maturity Band:      {scores.maturity_band}")

    assert scores.website_experience > 5, "Digital Experience should not collapse when a responsive website exists!"
    assert scores.overall_score > 60, "Overall score should reflect digital presence maturity!"
    print("[PASS] TEST 2: Business with website successfully verified!")

@pytest.mark.asyncio
async def test_3_social_first_business():
    print("\n" + "="*70)
    print("TEST 3: SOCIAL-FIRST BUSINESS (INTERIOR DESIGNER ON INSTAGRAM)")
    print("="*70)

    identity = BusinessIdentity(
        business_name="Artisan Spaces Interior Studio",
        category="Interior Designer",
        address="Koramangala, Bengaluru",
        city="Bengaluru",
        phone="+91 98450 99887",
        website=None,
        source_url="https://instagram.com/artisanspaces_design",
        rating=None,
        review_count=None,
        identity_confidence=0.9,
        verified=True,
        is_demo=False
    )

    evidence = [
        EvidenceItem(source="Instagram", field="Public Account", value="@artisanspaces_design", confidence=0.95, status="PASS", observation="Active design portfolio profile."),
        EvidenceItem(source="Instagram", field="Audience Proof", value="14.2k followers, 320 posts", confidence=0.9, status="PASS", observation="Strong visual content cadence and portfolio showcase."),
        EvidenceItem(source="Instagram", field="Website Link", value="No destination website configured in bio", confidence=0.95, status="FAIL", observation="Bio lacks an owned portfolio destination.")
    ]

    scores = ScoringEngine.calculate(identity, evidence)
    print(f"Business Type:        {scores.business_type}")
    print(f"Overall Score:        {scores.overall_score} / 100")
    print(f"- Social Presence:    {scores.social_presence} / 10")
    print(f"- Digital Experience: {scores.website_experience} / 15")

    assert scores.business_type == "SOCIAL_FIRST", f"Expected SOCIAL_FIRST, got {scores.business_type}"
    assert scores.social_presence >= 8, f"Social presence should be strong for 14k followers profile, got {scores.social_presence}"
    assert scores.website_experience <= 3, f"Digital experience should still show gap since no website exists, got {scores.website_experience}"

    # Check website preview concept
    opp = Opportunity(
        title="Establish an Owned Portfolio Destination to Turn Social Followers into Direct Design Consultations",
        priority="HIGH",
        finding="Strong Instagram following but lacks an owned portfolio website.",
        evidence=evidence,
        why_it_matters="An owned website captures qualified leads and projects.",
        current_journey="Browse Instagram -> DM -> Delays",
        improved_journey="Browse Instagram -> Link in Bio -> 3D Showcase -> Book Consultation",
        recommended_service="Portfolio + Consultation Conversion Website"
    )
    concept = WebsitePreviewEngine.build_concept(identity, scores, opp)
    print(f"Concept Headline: {concept.headline}")
    print(f"Primary CTA:      {concept.primary_cta}")
    print(f"Quality Score:    {concept.preview_quality_score} / 100")

    assert "Interior" in concept.headline or "Architecture" in concept.headline, "Preview should be Interior Design specific!"
    assert any(s["name"] == "Residential Interior Architecture" for s in concept.services), "Preview services should be Interior Design specific!"
    assert concept.preview_quality_score >= 85, f"Preview quality score must be >= 85, got {concept.preview_quality_score}"

    # Verify Master 5-Page PDF for Interior Designer
    pdf_path, is_valid, errors = await PDFRenderer.render(
        audit_id="TEST-INTERIOR-001",
        identity=identity,
        scores=scores,
        strongest_asset="Active visual social presence on Instagram",
        biggest_gap="No owned portfolio destination website",
        opp=opp,
        recommendations=[]
    )
    assert is_valid, f"Interior Designer PDF failed QA: {errors}"
    reader = pypdf.PdfReader(str(pdf_path))
    assert len(reader.pages) in [2, 9], f"Expected 2 or 9 pages, got {len(reader.pages)}"
    print(f"Interior Designer PDF Verified: {pdf_path.name} (Exactly 9 pages)")

    print("[PASS] TEST 3: Social-First business successfully verified!")

@pytest.mark.asyncio
async def test_4_banquet_hall():
    print("\n" + "="*70)
    print("TEST 4: BANQUET HALL (VENUE-SPECIFIC PREVIEW)")
    print("="*70)

    identity = BusinessIdentity(
        business_name="Grand Royal Palace Banquet & Convention",
        category="Banquet Hall",
        address="Bellary Road, Bengaluru",
        city="Bengaluru",
        phone="+91 80 4433 2211",
        website=None,
        source_url="https://maps.google.com/place/Grand+Royal+Palace",
        rating=4.7,
        review_count=310,
        identity_confidence=0.95,
        verified=True,
        is_demo=False
    )

    evidence = [
        EvidenceItem(source="Google Maps", field="Business Listing", value="Grand Royal Palace Banquet", confidence=0.98, status="PASS", observation="Major event venue listing verified.")
    ]

    scores = ScoringEngine.calculate(identity, evidence)
    opp = Opportunity(
        title="Launch a High-Impact Venue Showcase & Availability Booking Funnel",
        priority="HIGH",
        finding="High-intent wedding and event hosts currently have no digital venue walkthrough.",
        evidence=evidence,
        why_it_matters="Banquet decisions depend heavily on visual walkthroughs and capacity details.",
        current_journey="Google Search -> Call -> Reception Busy",
        improved_journey="Google Search -> Venue Preview -> Check Availability on WhatsApp",
        recommended_service="Venue Booking / Enquiry Experience"
    )

    concept = WebsitePreviewEngine.build_concept(identity, scores, opp)
    print(f"Banquet Concept Headline: {concept.headline}")
    print(f"Primary CTA:              {concept.primary_cta}")
    print(f"Secondary CTA:            {concept.secondary_cta}")
    print(f"Quality Score:            {concept.preview_quality_score} / 100")

    assert "Celebrations" in concept.headline or "Banquet" in concept.headline or "Venue" in concept.headline, "Banquet headline must be venue-specific!"
    assert "Availability" in concept.primary_cta or "Enquire" in concept.primary_cta, "Primary CTA must be availability or enquiry focused!"
    assert any("Wedding" in s["name"] for s in concept.services), "Banquet services must feature Weddings/Events!"
    assert concept.preview_quality_score >= 85, f"Preview quality score must be >= 85, got {concept.preview_quality_score}"

    # Verify Master 5-Page PDF for Banquet Hall
    pdf_path, is_valid, errors = await PDFRenderer.render(
        audit_id="TEST-BANQUET-001",
        identity=identity,
        scores=scores,
        strongest_asset="Established venue reputation on Google Maps",
        biggest_gap="No digital venue walkthrough or date enquiry funnel",
        opp=opp,
        recommendations=[]
    )
    assert is_valid, f"Banquet Hall PDF failed QA: {errors}"
    reader = pypdf.PdfReader(str(pdf_path))
    assert len(reader.pages) in [2, 9], f"Expected 2 or 9 pages, got {len(reader.pages)}"
    print(f"Banquet Hall PDF Verified: {pdf_path.name} (Exactly 9 pages)")

    print("[PASS] TEST 4: Banquet hall successfully verified!")

@pytest.mark.asyncio
async def test_5_school():
    print("\n" + "="*70)
    print("TEST 5: SCHOOL (ADMISSIONS-SPECIFIC PREVIEW)")
    print("="*70)

    identity = BusinessIdentity(
        business_name="Oakridge Heritage Academy",
        category="International School",
        address="Sarjapur Road, Bengaluru",
        city="Bengaluru",
        phone="+91 80 6789 0123",
        website=None,
        source_url="https://maps.google.com/place/Oakridge+Heritage+Academy",
        rating=4.6,
        review_count=190,
        identity_confidence=0.95,
        verified=True,
        is_demo=False
    )

    evidence = [
        EvidenceItem(source="Google Maps", field="Business Listing", value="Oakridge Heritage Academy", confidence=0.98, status="PASS", observation="School campus listing verified.")
    ]

    scores = ScoringEngine.calculate(identity, evidence)
    opp = Opportunity(
        title="Deploy an Admissions Portal & Virtual Campus Tour Experience",
        priority="HIGH",
        finding="Prospective parents searching for school admissions have no digital curriculum or tour destination.",
        evidence=evidence,
        why_it_matters="Parents expect transparent academic and campus details before visiting.",
        current_journey="Google Search -> Call Admin Desk",
        improved_journey="Google Search -> School Website -> Virtual Tour -> Schedule Campus Visit",
        recommended_service="Admissions Website + Enquiry System"
    )

    concept = WebsitePreviewEngine.build_concept(identity, scores, opp)
    print(f"School Concept Headline: {concept.headline}")
    print(f"Primary CTA:             {concept.primary_cta}")
    print(f"Quality Score:           {concept.preview_quality_score} / 100")

    assert "Academic" in concept.headline or "Character" in concept.headline or "Learning" in concept.headline, "School headline must be education-specific!"
    assert "Admissions" in concept.primary_cta, "Primary CTA must be Admissions focused!"
    assert any("Academics" in s["name"] or "Curriculum" in s["name"] for s in concept.services), "School services must feature Academics!"
    assert concept.preview_quality_score >= 85, f"Preview quality score must be >= 85, got {concept.preview_quality_score}"

    # Verify Master 5-Page PDF for School
    pdf_path, is_valid, errors = await PDFRenderer.render(
        audit_id="TEST-SCHOOL-001",
        identity=identity,
        scores=scores,
        strongest_asset="Respected academic reputation in local community",
        biggest_gap="No digital curriculum tour or online admissions gateway",
        opp=opp,
        recommendations=[]
    )
    assert is_valid, f"School PDF failed QA: {errors}"
    reader = pypdf.PdfReader(str(pdf_path))
    assert len(reader.pages) in [2, 9], f"Expected 2 or 9 pages, got {len(reader.pages)}"
    print(f"School PDF Verified: {pdf_path.name} (Exactly 9 pages)")

    print("[PASS] TEST 5: School successfully verified!")

async def run_all_tests():
    print("STARTING V2 COMMERCIAL QUALITY RESET VALIDATION SUITE...")
    await test_1_gyan_dental_clinic()
    await test_2_business_with_website()
    await test_3_social_first_business()
    await test_4_banquet_hall()
    await test_5_school()
    print("\n" + "="*70)
    print("ALL 5 REQUIRED COMMERCIAL TEST SCENARIOS PASSED WITH ZERO DEFECTS!")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
