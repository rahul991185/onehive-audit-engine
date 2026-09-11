import asyncio
import pytest
import os
import json
from pathlib import Path
from pypdf import PdfReader

from app.services.classifier import URLClassifier
from app.services.identity_resolver import IdentityResolver
from app.services.scoring_engine import ScoringEngine
from app.services.opportunity_engine import OpportunityEngine
from app.models.schemas import SourceType, BusinessIdentity, EvidenceItem, AuditScore
from app.pdf.renderer import PDFRenderer
from app.pdf.verifier import PDFVerifier
from app.services.audit_orchestrator import AuditOrchestrator
from app.config import DEMO_FIXTURE_PATH

@pytest.mark.asyncio
async def test_classification_matrix():
    """
    TESTS 1, 2, 3, 4, 5, 6, 7, 8:
    Verify URL classification for Maps place, CID, short URL, search, Website, Instagram, Facebook, and Invalid.
    """
    # TEST 1: Maps place
    t1 = URLClassifier.classify("https://www.google.com/maps/place/Some+Dentist/@12.97,77.59,15z")
    assert t1 == SourceType.GOOGLE_MAPS

    # TEST 2: Maps CID
    t2 = URLClassifier.classify("https://maps.google.com/?cid=8429486214490638391&g_mp=Cidnb29nbGUubWFwcy")
    assert t2 == SourceType.GOOGLE_MAPS

    # TEST 3: maps.app.goo.gl
    t3 = URLClassifier.classify("https://maps.app.goo.gl/abcdef123456")
    assert t3 == SourceType.GOOGLE_MAPS

    # TEST 4: Maps search
    t4 = URLClassifier.classify("https://www.google.com/maps/search/dental+clinic+near+me")
    assert t4 == SourceType.GOOGLE_MAPS

    # TEST 5: Website
    t5 = URLClassifier.classify("https://drbudhiraja.com")
    assert t5 == SourceType.WEBSITE

    # TEST 6: Instagram
    t6 = URLClassifier.classify("https://instagram.com/drbudhiraja_dental")
    assert t6 == SourceType.INSTAGRAM

    # TEST 7: Facebook
    t7 = URLClassifier.classify("https://facebook.com/drbudhirajaclinic")
    assert t7 == SourceType.FACEBOOK

    # TEST 8: Invalid
    t8 = URLClassifier.classify("not_a_valid_url_string")
    assert t8 == SourceType.UNKNOWN


@pytest.mark.asyncio
async def test_demo_mode_isolation():
    """
    TEST 15 & 16:
    Demo mode explicitly loads Apex Dental fixture.
    Real mode must NEVER fall back to Apex Dental or fixture data.
    """
    # Demo mode test
    demo_identity, demo_evidence, _ = await IdentityResolver.resolve("https://demo.mode", is_demo=True)
    assert demo_identity.is_demo is True
    assert "Apex Dental" in demo_identity.business_name
    assert demo_identity.verified is True

    # Real mode with unresolvable URL test (TEST 9, 10, 16)
    unresolvable_url = "https://www.google.com/maps/place/TotallyFakeNonExistentPlaceXYZ987654321"
    try:
        identity, evidence, _ = await IdentityResolver.resolve(unresolvable_url, is_demo=False)
        # If it returned an identity, it MUST NOT be Apex Dental
        assert "Apex Dental" not in identity.business_name
    except Exception as e:
        # Failing safely is also expected
        assert "Apex Dental" not in str(e)


@pytest.mark.asyncio
async def test_deterministic_scoring_and_weights():
    """
    TEST: Deterministic scoring strictly totals 100 max across 6 dimensions.
    """
    dummy_identity = BusinessIdentity(
        business_name="Test Clinic",
        category="Healthcare",
        address="Test Road, City",
        source_url="https://test.com",
        identity_confidence=0.9,
        verified=True,
        rating=4.8,
        review_count=120
    )
    dummy_evidence = [
        EvidenceItem(source="GOOGLE_MAPS", field="rating", value="4.8", confidence=0.95),
        EvidenceItem(source="WEBSITE", field="whatsapp", value="not_detected", confidence=0.9, status="FAIL")
    ]
    scores = ScoringEngine.calculate(dummy_identity, dummy_evidence)

    assert 0 <= scores.overall_score <= 100
    assert 0 <= scores.discoverability <= 20
    assert 0 <= scores.brand_identity <= 15
    assert 0 <= scores.trust_reputation <= 20
    assert 0 <= scores.website_experience <= 15
    assert 0 <= scores.lead_conversion <= 20
    assert 0 <= scores.social_presence <= 10


@pytest.mark.asyncio
async def test_no_hallucination_and_pdf_two_pages():
    """
    TEST 14: PDF report is strictly 2 pages and contains zero forbidden phrases.
    """
    # Run pipeline in demo mode to get complete deterministic pack
    result = await AuditOrchestrator.run("https://demo.mode", is_demo=True)
    assert result is not None
    assert result.audit_id is not None
    assert result.is_demo is True

    # PDF verification using centralized REPORTS_DIR
    from app.config import REPORTS_DIR, SALESPACKS_DIR
    matches = list(REPORTS_DIR.glob("*apex_dental*.pdf"))
    assert len(matches) > 0, f"Expected PDF in {REPORTS_DIR}"
    pdf_path = matches[0]

    reader = PdfReader(str(pdf_path))
    # Strict 2 pages assertion
    assert len(reader.pages) == 2, f"Expected exactly 2 pages, found {len(reader.pages)}"

    # Strict content assertion
    all_text = ""
    for page in reader.pages:
        all_text += " " + (page.extract_text() or "")

    normalized_text = " ".join(all_text.split())

    normalized_upper = normalized_text.upper()

    # Required section titles per 2-page specification
    assert "DIGITAL PRESENCE INTELLIGENCE REPORT" in normalized_upper
    assert "BUSINESS DETAILS" in normalized_upper
    assert "DIGITAL PERFORMANCE BREAKDOWN" in normalized_upper
    assert "YOUR GROWTH OPPORTUNITY" in normalized_upper
    assert "CUSTOMER JOURNEY ANALYSIS" in normalized_upper
    assert "WHAT ONEHIVE RECOMMENDS" in normalized_upper
    assert "BUILD. AUTOMATE. GROW." in normalized_upper

    # Forbidden text assertions
    assert "CONFIDENTIAL INTELLIGENCE" not in normalized_text
    assert "EXECUTIVE STRATEGIC BRIEF" not in normalized_text
    assert "73%" not in normalized_text
    assert "dominant #1" not in normalized_text
    assert "lost customer" not in normalized_text
    assert "lost customers" not in normalized_text
    assert "revenue lost" not in normalized_text


@pytest.mark.asyncio
async def test_sales_pack_zip_contents():
    """
    TEST 17: Complete Sales Pack ZIP bundle verification.
    """
    import zipfile
    from app.config import SALESPACKS_DIR
    result = await AuditOrchestrator.run("https://demo.mode", is_demo=True)
    zip_matches = list(SALESPACKS_DIR.glob("*apex_dental*.zip"))
    assert len(zip_matches) > 0, f"Expected ZIP in {SALESPACKS_DIR}"
    zip_file = zip_matches[0]

    with zipfile.ZipFile(str(zip_file), "r") as z:
        names = z.namelist()
        # Verify required bundle structure
        assert any("report" in n and n.endswith(".pdf") for n in names)
        assert any("website-preview" in n and "desktop" in n for n in names)
        assert any("website-preview" in n and "mobile" in n for n in names)
        assert any("quick-win" in n for n in names)
        assert any("whatsapp-message.txt" in n for n in names)
        assert any("sales-intelligence-brief.txt" in n for n in names)
        assert any("audit.json" in n for n in names)

