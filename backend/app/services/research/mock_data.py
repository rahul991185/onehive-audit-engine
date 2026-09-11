import uuid
import datetime
import re
from urllib.parse import urlparse, unquote
from app.schemas.audit import (
    SourceType, BusinessInfo, Scores, EvidenceItem, 
    TopOpportunity, Recommendation, StructuredAudit
)

def infer_business_details(url: str, source_type: SourceType) -> tuple[str, str, str, str]:
    """
    Extracts high-fidelity business name, industry, location, and website from URL patterns.
    """
    parsed = urlparse(url if url.startswith("http") else f"https://{url}")
    path = unquote(parsed.path)
    netloc = parsed.netloc.lower()

    # Default fallbacks
    business_name = "Apex Prime Services"
    industry = "Professional Services"
    location = "Indiranagar, Bangalore"
    website = url if source_type == SourceType.WEBSITE else "https://apexservices.in"

    # Google Maps pattern
    if source_type == SourceType.GOOGLE_MAPS:
        match = re.search(r"/place/([^/@]+)", path)
        if match:
            raw_name = match.group(1).replace("+", " ")
            parts = [p.strip() for p in raw_name.split(",") if p.strip()]
            business_name = parts[0]
            if len(parts) > 1:
                location = ", ".join(parts[1:3])
        else:
            business_name = "Apex Dental & Implant Centre"
            industry = "Healthcare & Dental"
            location = "Indiranagar, Bangalore"
            website = "https://apexdentalcare.in"

    # Instagram pattern
    elif source_type == SourceType.INSTAGRAM:
        parts = [p for p in path.split("/") if p]
        if parts:
            username = parts[0].replace(".", " ").replace("_", " ").title()
            business_name = username
        else:
            business_name = "Velvet Glow Luxury Salon"
        industry = "Beauty, Wellness & Salon"
        location = "Koramangala, Bangalore"
        website = f"https://instagram.com/{parts[0] if parts else 'velvetglow'}"

    # Facebook pattern
    elif source_type == SourceType.FACEBOOK:
        parts = [p for p in path.split("/") if p and p not in ["pages", "profile.php"]]
        if parts:
            business_name = parts[0].replace(".", " ").replace("-", " ").title()
        else:
            business_name = "Sterling Automotive Studio"
        industry = "Automotive Care & Detailing"
        location = "Whitefield, Bangalore"
        website = f"https://facebook.com/{parts[0] if parts else 'sterlingauto'}"

    # General Website pattern
    elif source_type == SourceType.WEBSITE:
        clean_netloc = netloc.replace("www.", "")
        domain_name = clean_netloc.split(".")[0]
        business_name = domain_name.replace("-", " ").replace("_", " ").title()
        website = f"https://{clean_netloc}"
        
        # Industry inferences based on domain cues
        name_lower = business_name.lower()
        if any(k in name_lower for k in ["dental", "clinic", "health", "care", "doctor"]):
            industry = "Healthcare & Clinic"
            location = "HSR Layout, Bangalore"
        elif any(k in name_lower for k in ["design", "interior", "decor", "architect"]):
            industry = "Interior Architecture & Living"
            location = "Jubilee Hills, Hyderabad"
        elif any(k in name_lower for k in ["cafe", "bake", "dine", "kitchen", "food", "rest"]):
            industry = "Hospitality & Dining"
            location = "Bandra West, Mumbai"
        elif any(k in name_lower for k in ["tech", "sol", "soft", "corp", "ind", "metal", "eng"]):
            industry = "Engineering & Manufacturing"
            location = "Peenya Industrial Area, Bangalore"
        else:
            industry = "Premium Retail & Design"
            location = "Indiranagar, Bangalore"

    # Industry refinement based on name keywords
    n = business_name.lower()
    if "dental" in n or "implant" in n or "clinic" in n:
        industry = "Dental & Specialty Healthcare"
    elif "salon" in n or "glow" in n or "spa" in n or "beauty" in n:
        industry = "Luxury Wellness & Aesthetics"
    elif "interior" in n or "wood" in n or "decor" in n or "studio" in n:
        industry = "Interior Architecture & Design"
    elif "auto" in n or "motor" in n or "detailing" in n:
        industry = "Automotive Detailing & Services"

    return business_name, industry, location, website


def generate_mock_audit(url: str, source_type: SourceType) -> StructuredAudit:
    """
    Generates deterministic, high-fidelity audit data reflecting OneHive intelligence standards.
    Uses evidence-first metrics and non-aggressive, commercially compelling sales insights.
    """
    business_name, industry, location, website = infer_business_details(url, source_type)
    audit_id = f"aud_{uuid.uuid4().hex[:10]}"
    timestamp = datetime.datetime.now().strftime("%B %d, %Y")

    # Tailor evidence and scores based on the primary source type and industry
    if source_type == SourceType.GOOGLE_MAPS:
        scores = Scores(
            discoverability=17,
            brand_identity=11,
            trust_reputation=18,
            website_experience=9,
            lead_conversion=8,
            social_presence=7
        )
        overall_score = sum([
            scores.discoverability, scores.brand_identity, scores.trust_reputation,
            scores.website_experience, scores.lead_conversion, scores.social_presence
        ])

        evidence_items = [
            EvidenceItem(
                source="Google Business Profile",
                field="Customer Rating & Reviews",
                value="4.8 ★ (142 reviews verified)",
                confidence=0.98,
                observation="High consumer trust and strong local reputation established."
            ),
            EvidenceItem(
                source="Local Search Journey",
                field="Direct Enquiry Routing",
                value="Standard phone number only; no instant WhatsApp or booking link",
                confidence=0.94,
                observation="Prospects seeking quick appointments must dial manually during business hours."
            ),
            EvidenceItem(
                source="Digital Foundation",
                field="Destination Experience",
                value="Landing page lacks mobile-responsive lead capture",
                confidence=0.91,
                observation="High volume of mobile searchers encounter friction when attempting to enquire."
            )
        ]

        strongest_asset = f"Outstanding local reputation with 4.8★ rating across 140+ genuine patient reviews."
        biggest_gap = "Absence of a frictionless instant enquiry / WhatsApp bridge for high-intent search traffic."

        top_opp = TopOpportunity(
            title="Convert High-Intent Local Searches into Instant Direct Consultations",
            priority="HIGH",
            finding="While your business commands strong local visibility and excellent Google ratings, there appears to be no frictionless bridge converting these discovery visits into immediate enquiries.",
            evidence=evidence_items,
            why_it_matters="Over 73% of local high-intent customers search on mobile devices outside standard reception hours. When the only available action is a traditional phone call, a substantial portion of interested prospects may delay or seek alternative practices that offer instant messaging.",
            current_journey="Google Search → Maps Profile → Phone Call (Missed / Deferred) → Lost Interest",
            improved_journey="Google Search → Verified Profile → 1-Click WhatsApp Enquiry → Automated Consultation Booking",
            confidence=0.95
        )

        recommendations = [
            Recommendation(
                order=1,
                category="BUILD",
                title="Dedicated High-Converting Mobile Consultation Page",
                description="Deploy a lightning-fast, mobile-first booking landing page designed specifically to convert local search traffic with verified service highlights and doctor credentials."
            ),
            Recommendation(
                order=2,
                category="CONVERT",
                title="Direct 1-Click WhatsApp Concierge Integration",
                description="Embed automated WhatsApp consultation routing directly on your Google profile and website to capture enquiries 24/7 with instant acknowledgment."
            ),
            Recommendation(
                order=3,
                category="GROW",
                title="Automated Post-Treatment Review Harvesting",
                description="Implement a systematic digital review capture workflow to cross the 250+ review threshold and solidify dominant #1 local map pack ranking."
            )
        ]

    elif source_type == SourceType.INSTAGRAM:
        scores = Scores(
            discoverability=12,
            brand_identity=14,
            trust_reputation=13,
            website_experience=6,
            lead_conversion=7,
            social_presence=10
        )
        overall_score = sum([
            scores.discoverability, scores.brand_identity, scores.trust_reputation,
            scores.website_experience, scores.lead_conversion, scores.social_presence
        ])

        evidence_items = [
            EvidenceItem(
                source="Instagram Profile",
                field="Visual Brand & Engagement",
                value="Consistent aesthetic, 8.4k+ engaged followers",
                confidence=0.96,
                observation="Strong visual storytelling and authentic community appeal."
            ),
            EvidenceItem(
                source="Bio Link Architecture",
                field="Primary Call-to-Action",
                value="Generic link aggregator / unoptimized page",
                confidence=0.93,
                observation="Profile visitors are redirected into multiple confusing choices rather than a clear booking journey."
            ),
            EvidenceItem(
                source="Enquiry Conversion",
                field="DM Lead Capture",
                value="Manual DM responses with noticeable delays",
                confidence=0.89,
                observation="High-intent enquiries arriving via stories and reels experience response lag."
            )
        ]

        strongest_asset = "Exceptional visual brand identity with an engaged, loyal social audience."
        biggest_gap = "Friction-heavy link-in-bio journey causing loss of high-intent social followers before appointment booking."

        top_opp = TopOpportunity(
            title="Turn Profile Views & Reel Engagement into Direct Bookings",
            priority="HIGH",
            finding="Your visual content attracts consistent attention, but the journey from viewing a post to securing a confirmed booking contains multiple points of friction.",
            evidence=evidence_items,
            why_it_matters="Social attention has an extremely brief half-life. Interested clients who click your profile link expect an instant, frictionless way to view services and secure a spot within 60 seconds without back-and-forth DM messaging.",
            current_journey="Viral Reel → Profile Visit → Bio Link Click → Cluttered Page → Abandoned Session",
            improved_journey="Viral Reel → Profile Visit → 1-Click VIP Booking / WhatsApp → Instant Slot Secured",
            confidence=0.94
        )

        recommendations = [
            Recommendation(
                order=1,
                category="BUILD",
                title="Custom Branded VIP Experience Portal",
                description="Replace generic bio-links with a bespoke luxury digital menu highlighting signature services, visual portfolio, and transparent service packages."
            ),
            Recommendation(
                order=2,
                category="CONVERT",
                title="Automated Instant Booking & WhatsApp Confirmation",
                description="Allow clients to select services and confirm appointments directly on WhatsApp with zero waiting time and automated calendar reminders."
            ),
            Recommendation(
                order=3,
                category="GROW",
                title="High-Converting Reel-to-Enquiry Social Funnels",
                description="Structure upcoming visual content with dedicated keyword triggers (e.g., 'Comment GLOW for pricing') linked to automated direct message delivery."
            )
        ]

    else:  # WEBSITE or FACEBOOK
        scores = Scores(
            discoverability=13,
            brand_identity=12,
            trust_reputation=14,
            website_experience=9,
            lead_conversion=8,
            social_presence=6
        )
        overall_score = sum([
            scores.discoverability, scores.brand_identity, scores.trust_reputation,
            scores.website_experience, scores.lead_conversion, scores.social_presence
        ])

        evidence_items = [
            EvidenceItem(
                source="Website Experience",
                field="Mobile Responsiveness & Speed",
                value="Mobile load time 3.8s; desktop layout scaled to mobile",
                confidence=0.92,
                observation="Mobile visitors must pinch/zoom or navigate dense menus to find key offerings."
            ),
            EvidenceItem(
                source="Conversion Journey",
                field="Primary Action Hierarchy",
                value="Static contact form tucked on secondary page; no persistent CTA",
                confidence=0.95,
                observation="Visitors who are convinced by your work have to search for how to start an enquiry."
            ),
            EvidenceItem(
                source="Trust Proof",
                field="Social Proof Integration",
                value="Project showcase present, but verified reviews and timeline guarantees are absent",
                confidence=0.90,
                observation="Commercial confidence can be significantly magnified with structured trust signals."
            )
        ]

        strongest_asset = "Well-established market reputation with high caliber of completed projects."
        biggest_gap = "Absence of a clear, persistent mobile conversion journey turning visits into qualified enquiries."

        top_opp = TopOpportunity(
            title="Modernize Digital Conversion Journey to Capture High-Value Inbound Enquiries",
            priority="HIGH",
            finding="While your portfolio showcases exceptional capability, the website currently acts as a passive brochure rather than an active client acquisition engine.",
            evidence=evidence_items,
            why_it_matters="Premium clients evaluate digital polish as an indicator of service quality. A modern, instant-enquiry experience reassures prospective clients immediately and positions your business as the premium market leader.",
            current_journey="Website Visit → Browse Portfolio → Search for Contact Page → Long Form → Deferred Action",
            improved_journey="Website Visit → Clear Value Promise → Instant WhatsApp / Project Estimator → Qualified Consultation",
            confidence=0.93
        )

        recommendations = [
            Recommendation(
                order=1,
                category="BUILD",
                title="High-Performance Modern Digital Showcase",
                description="Redesign the digital experience with an ultra-clean, mobile-first showcase featuring instant project filters, clear service packages, and client proof."
            ),
            Recommendation(
                order=2,
                category="CONVERT",
                title="Frictionless Enquiry Architecture & WhatsApp Concierge",
                description="Deploy persistent 1-click WhatsApp enquiry routing and a simple 3-question project brief estimator to capture leads at peak intent."
            ),
            Recommendation(
                order=3,
                category="GROW",
                title="Local Authority & Targeted Digital Acquisition",
                description="Synchronize Google Business Profile, client case studies, and local search SEO to dominate search results for high-intent queries in your area."
            )
        ]

    business_info = BusinessInfo(
        name=business_name,
        industry=industry,
        location=location,
        website=website,
        input_url=url,
        source_type=source_type
    )

    return StructuredAudit(
        audit_id=audit_id,
        created_at=timestamp,
        business=business_info,
        overall_score=overall_score,
        scores=scores,
        strongest_asset=strongest_asset,
        biggest_gap=biggest_gap,
        attention_callout="We've identified one area we believe deserves immediate attention.",
        top_opportunity=top_opp,
        recommendations=recommendations,
        report_pdf_url=f"/api/reports/{audit_id}/pdf",
        report_download_url=f"/api/reports/{audit_id}/download"
    )
