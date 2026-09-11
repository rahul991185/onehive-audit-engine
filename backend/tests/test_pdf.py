import asyncio
import pytest
from app.services.classifier import classify_url
from app.services.research.mock_data import generate_mock_audit
from app.services.pdf_generator import generate_5page_pdf

@pytest.mark.asyncio
async def test_generation():
    test_url = "https://www.google.com/maps/place/Apex+Dental+Clinic+Indiranagar"
    source = classify_url(test_url)
    print(f"Classified '{test_url}' as {source}")
    
    audit = generate_mock_audit(test_url, source)
    print(f"Generated audit for {audit.business.name} (Score: {audit.overall_score}/100)")
    
    pdf_path, num_pages = await generate_5page_pdf(audit)
    print(f"PDF Output: {pdf_path}")
    print(f"Page Count: {num_pages}")
    
    assert pdf_path.exists(), "PDF file does not exist!"
    assert pdf_path.stat().st_size > 10000, "PDF file too small!"
    assert num_pages == 5, f"Expected 5 pages, got {num_pages}!"
    print("ALL TESTS PASSED: Exactly 5 pages verified!")

if __name__ == "__main__":
    asyncio.run(test_generation())
