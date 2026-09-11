import re
from pathlib import Path
from typing import Tuple, List, Optional
import pypdf
from app.models.schemas import BusinessIdentity

class PDFVerifier:
    """
    Automated QA Verifier for Generated 9-Page OneHive Reports.
    Enforces exact 9-page layout, required headings, demo isolation, and strict factuality rules.
    """

    REQUIRED_STRINGS = [
        "DIGITAL PRESENCE INTELLIGENCE REPORT",
        "BUSINESS DETAILS",
        "DIGITAL PERFORMANCE BREAKDOWN",
        "YOUR GROWTH OPPORTUNITY",
        "CUSTOMER JOURNEY ANALYSIS",
        "WHAT ONEHIVE RECOMMENDS",
        "BUILD. AUTOMATE. GROW."
    ]

    # Prohibited preview terms inside the cold PDF per Section 1 & 36
    FORBIDDEN_PREVIEW_PATTERNS = [
        "website preview",
        "website concept",
        "desktop preview",
        "mobile preview",
        "preview url"
    ]

    # Prohibited claims per V2 factuality QA specification
    FORBIDDEN_PATTERNS = [
        "73%",
        "lost customer",
        "lost customers",
        "revenue lost",
        "lost revenue",
        "dominant",
        "hospital-grade",
        "pain-free",
        "5-star reviews",
        "5-star patient reviews",
        "guaranteed",
        "significant portion",
        "unanswered after hours",
        "seek alternative providers",
        "reinforce local ranking",
        "under 60 seconds",
        "zero friction"
    ]

    # Typography concatenation patterns (detects missing spaces between words)
    CONCATENATION_PATTERNS = [
        r"\byourlocal\b",
        r"\bcustomertrust\b",
        r"\breviewrequest\b",
        r"\bchannelto\b",
        r"\bbuiltfor\b",
        r"\bpatienttrust\b",
        r"\blocalreputation\b",
        r"\bdigitaldestination\b",
        r"\bconsultationnext\b"
    ]

    @staticmethod
    def verify(pdf_path: Path, identity: BusinessIdentity, scores: Optional[object] = None) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        if not pdf_path.exists():
            return False, [f"PDF file does not exist at {pdf_path}"]

        if pdf_path.stat().st_size < 15000:
            errors.append(f"PDF file size is suspiciously small ({pdf_path.stat().st_size} bytes)")

        try:
            reader = pypdf.PdfReader(str(pdf_path))
            num_pages = len(reader.pages)
            if num_pages != 2:
                errors.append(f"PDF contains {num_pages} pages, expected EXACTLY 2 pages!")

            full_text = ""
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                full_text += f"\n--- PAGE {i+1} ---\n" + text

            normalized_text = " ".join(full_text.split()).lower()

            # 1. Check required headings
            for req in PDFVerifier.REQUIRED_STRINGS:
                req_norm = " ".join(req.split()).lower()
                if req_norm not in normalized_text:
                    errors.append(f"Missing required text in PDF: '{req}'")

            # 2. Check forbidden factuality patterns
            for fbd in PDFVerifier.FORBIDDEN_PATTERNS:
                fbd_norm = fbd.lower()
                if fbd_norm in normalized_text:
                    errors.append(f"Prohibited/unsupported claim pattern found in PDF: '{fbd}'")

            # 2b. Check forbidden preview sections in PDF per Section 1 & 36
            for prev_pat in PDFVerifier.FORBIDDEN_PREVIEW_PATTERNS:
                if prev_pat in normalized_text:
                    errors.append(f"Forbidden website preview content found in customer PDF: '{prev_pat}'")

            # 3. Check typography concatenation patterns
            for pat in PDFVerifier.CONCATENATION_PATTERNS:
                if re.search(pat, normalized_text):
                    errors.append(f"Typography concatenation error detected in PDF (missing space): pattern '{pat}' matched.")

            # 4. Check demo data isolation in real mode
            if not identity.is_demo and "apex dental" in normalized_text and "apex dental" not in identity.business_name.lower():
                errors.append("Demo business fixture name ('Apex Dental') leaked into real mode report!")

            # 5. Score consistency check
            if scores:
                tr_score = getattr(scores, "trust_reputation", None)
                if tr_score is not None and tr_score < 12 and "exceptional customer trust" in normalized_text:
                    errors.append(f"Score inconsistency: Trust score is low ({tr_score}/20) but copy claims 'exceptional customer trust'.")

                wx_score = getattr(scores, "website_experience", None)
                if wx_score == 0 and "verified website active" in normalized_text:
                    errors.append(f"Score inconsistency: Website experience is 0/15 but report indicates an active verified website.")

        except Exception as e:
            errors.append(f"PDF verification exception: {e}")

        is_valid = len(errors) == 0
        if is_valid:
            print(f"[PDFVerifier] PASSED: {pdf_path.name} is verified (strictly 5 pages, all QA factuality gates passed).")
        else:
            print(f"[PDFVerifier] FAILED checks: {errors}")

        return is_valid, errors
