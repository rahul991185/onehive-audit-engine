import re
from urllib.parse import urlparse
from app.schemas.audit import SourceType

def classify_url(url: str) -> SourceType:
    """
    Classifies an input URL into GOOGLE_MAPS, WEBSITE, INSTAGRAM, FACEBOOK, or UNKNOWN.
    Handles short links, mobile URLs, and query parameters cleanly.
    """
    if not url or not isinstance(url, str):
        return SourceType.UNKNOWN

    cleaned_url = url.strip().lower()

    if not cleaned_url.startswith(("http://", "https://")):
        cleaned_url = "https://" + cleaned_url

    try:
        parsed = urlparse(cleaned_url)
        netloc = parsed.netloc.lower()
        path = parsed.path.lower()
    except Exception:
        return SourceType.UNKNOWN

    # Google Maps / Google Business Profile
    if any(domain in netloc for domain in [
        "maps.google.", "google.com/maps", "goo.gl/maps", 
        "maps.app.goo.gl", "business.google.com"
    ]) or ("google." in netloc and "/maps" in path):
        return SourceType.GOOGLE_MAPS

    # Instagram
    if any(domain in netloc for domain in ["instagram.com", "instagr.am"]):
        return SourceType.INSTAGRAM

    # Facebook
    if any(domain in netloc for domain in ["facebook.com", "fb.com", "fb.me", "m.facebook.com"]):
        return SourceType.FACEBOOK

    # General Business Website
    # Check if domain has a valid format (e.g. domain.tld)
    if "." in netloc and len(netloc.split(".")[-1]) >= 2:
        return SourceType.WEBSITE

    return SourceType.UNKNOWN

class URLClassifier:
    @staticmethod
    def classify(url: str) -> SourceType:
        return classify_url(url)

