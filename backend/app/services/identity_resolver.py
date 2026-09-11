import json
from typing import Tuple, Optional, List, Dict, Any
from app.models.schemas import SourceType, BusinessIdentity, EvidenceItem
from app.services.classifier import classify_url
from app.research.google_maps_adapter import GoogleMapsAdapter
from app.research.website_adapter import WebsiteAdapter
from app.research.social_adapters import SocialAdapters
from app.config import GOOGLE_MAPS_API_KEY, APP_DIR

class IdentityResolver:
    """
    Master Identity Resolver & Multi-Source Research Coordinator.
    Ensures REAL research for REAL URLs, with explicit fixture separation for demo mode.
    """

    @staticmethod
    def load_demo_business() -> Tuple[BusinessIdentity, List[EvidenceItem], Dict[str, Any]]:
        fixture_path = APP_DIR / "fixtures" / "demo_business.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        bus_dict = dict(data["business"])
        if not bus_dict.get("instagram_url"):
            bus_dict["instagram_url"] = "https://instagram.com/apexdentalcare_in"
        if not bus_dict.get("facebook_url"):
            bus_dict["facebook_url"] = "https://facebook.com/apexdentalcare"
        if not bus_dict.get("whatsapp_url"):
            bus_dict["whatsapp_url"] = "https://wa.me/918041234567"
        if not bus_dict.get("email"):
            bus_dict["email"] = "care@apexdentalcare.in"

        identity = BusinessIdentity(**bus_dict)
        evidence = [EvidenceItem(**ev) for ev in data["top_opportunity"]["evidence"]]
        data["detected_services"] = ["Precision Dental Implants", "Invisalign & Clear Aligners", "Microscopic Endodontics", "Smile Makeovers"]
        return identity, evidence, data

    @staticmethod
    async def resolve(url: str, is_demo: bool = False) -> Tuple[Optional[BusinessIdentity], List[EvidenceItem], Dict[str, Any]]:
        # Explicit Demo Mode Check
        if is_demo:
            return IdentityResolver.load_demo_business()

        source_type = classify_url(url)
        all_evidence: List[EvidenceItem] = []
        extra_data: Dict[str, Any] = {}

        if source_type == SourceType.GOOGLE_MAPS:
            identity, maps_evidence = await GoogleMapsAdapter.resolve(url, api_key=GOOGLE_MAPS_API_KEY)
            all_evidence.extend(maps_evidence)

            # If a website was discovered on the Google profile, cross-analyze the website too!
            if identity and identity.website:
                try:
                    web_identity, web_evidence, web_extra = WebsiteAdapter.resolve(identity.website)
                    all_evidence.extend(web_evidence)
                    extra_data.update(web_extra)

                    # Merge discovered digital footprint directly onto identity
                    if web_identity:
                        if not identity.instagram_url and web_identity.instagram_url:
                            identity.instagram_url = web_identity.instagram_url
                        if not identity.facebook_url and web_identity.facebook_url:
                            identity.facebook_url = web_identity.facebook_url
                        if not identity.whatsapp_url and web_identity.whatsapp_url:
                            identity.whatsapp_url = web_identity.whatsapp_url
                        if not identity.email and web_identity.email:
                            identity.email = web_identity.email
                        if not identity.phone and web_identity.phone:
                            identity.phone = web_identity.phone
                        if not identity.tagline and web_identity.tagline:
                            identity.tagline = web_identity.tagline
                        if (not identity.category or identity.category in ["Local Business", "Establishment", "Point of interest"]) and web_identity.category != "Local Business":
                            identity.category = web_identity.category
                except Exception as e:
                    print(f"[IdentityResolver] Secondary website cross-reference note: {e}")

            return identity, all_evidence, extra_data

        elif source_type == SourceType.WEBSITE:
            identity, web_evidence, web_extra = WebsiteAdapter.resolve(url)
            all_evidence.extend(web_evidence)
            extra_data.update(web_extra)
            return identity, all_evidence, extra_data

        elif source_type == SourceType.INSTAGRAM:
            identity, insta_evidence = SocialAdapters.resolve_instagram(url)
            all_evidence.extend(insta_evidence)
            return identity, all_evidence, extra_data

        elif source_type == SourceType.FACEBOOK:
            identity, fb_evidence = SocialAdapters.resolve_facebook(url)
            all_evidence.extend(fb_evidence)
            return identity, all_evidence, extra_data

        else:
            return None, [
                EvidenceItem(
                    source="URL Classifier",
                    field="Input Format",
                    value=url,
                    confidence=0.99,
                    status="FAIL",
                    observation="Supplied link does not match a recognized Google Maps, Website, Instagram, or Facebook profile structure."
                )
            ], extra_data
