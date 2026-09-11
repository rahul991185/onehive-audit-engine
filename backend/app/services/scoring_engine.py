from typing import List, Dict, Tuple
from app.models.schemas import BusinessIdentity, EvidenceItem, AuditScore

class ScoringEngine:
    """
    Commercial Quality V2 Scoring Engine.
    
    Scores answer: 'How complete and commercially effective is this business's digital customer journey?'
    Enforces critical capability rules and mandatory maturity caps:
    - Rule A: No website -> Digital Experience 0 to 3 / 15 (0/15 if no owned destination).
    - Rule B: No website + high-value local business -> Lead Conversion <= 8 / 20.
    - Rule C: No website overall score cap -> Max 59 / 100.
    - Rule D: No website + no direct conversion path cap -> Max 54 / 100.
    - Score Bands: 0-39 (Critical Gap), 40-54 (Significant Opportunity), 55-69 (Developing), 70-84 (Strong), 85-100 (High-Performing).
    """

    @staticmethod
    def detect_business_type(identity: BusinessIdentity) -> str:
        cat_str = (identity.category or "").lower() + " " + (identity.business_name or "").lower()
        src_url = (identity.source_url or "").lower()

        if "instagram.com" in src_url or "facebook.com" in src_url:
            return "SOCIAL_FIRST"
        if any(k in cat_str for k in ["school", "college", "preschool", "academy", "institute", "coaching", "education", "classes"]):
            return "ADMISSION_FIRST"
        if any(k in cat_str for k in ["banquet", "resort", "venue", "hotel", "marriage", "wedding hall", "party hall", "convention"]):
            return "BOOKING_FIRST"
        if any(k in cat_str for k in ["interior", "architect", "decor", "designer", "construction", "builder"]):
            return "PROJECT_FIRST"
        if identity.website and not "maps.google" in src_url:
            return "WEBSITE_FIRST"
        return "LOCAL_FIRST"

    @staticmethod
    def calculate(identity: BusinessIdentity, evidence: List[EvidenceItem]) -> AuditScore:
        business_type = ScoringEngine.detect_business_type(identity)
        identity.business_type = business_type

        # Inspect evidence
        has_verified_listing = any(e.source == "Google Maps" and e.status == "PASS" for e in evidence)
        has_website = bool(identity.website and identity.website.strip())
        has_phone = bool(identity.phone and identity.phone.strip())
        has_whatsapp = any("whatsapp" in e.field.lower() and e.status == "PASS" for e in evidence)
        has_interactive_enquiry = any(k in e.field.lower() for k in ["whatsapp", "booking", "form", "cta"] for e in evidence if e.status == "PASS")
        has_mobile_vp = any("viewport" in e.field.lower() and e.status == "PASS" for e in evidence)
        has_https = any("ssl" in e.field.lower() and e.status == "PASS" for e in evidence)
        has_social = any(e.source in ["Instagram", "Facebook"] or any(k in e.field.lower() for k in ["social profile", "instagram", "facebook"]) for e in evidence if e.status == "PASS")


        explanations: Dict[str, str] = {}

        # -------------------------------------------------------------
        # 1. DISCOVERABILITY (Max 20)
        # -------------------------------------------------------------
        discoverability = 0
        if has_verified_listing:
            discoverability += 8
        if identity.address:
            discoverability += 4
        if has_phone:
            discoverability += 3
        if identity.review_count:
            if identity.review_count >= 100:
                discoverability += 3
            elif identity.review_count >= 30:
                discoverability += 2
            elif identity.review_count >= 5:
                discoverability += 1
        if identity.category and identity.category != "Local Business":
            discoverability += 2

        if not has_website:
            # Missing cross-channel web discoverability
            discoverability = min(16, discoverability)
            explanations["discoverability"] = f"Verified Google Business listing with visible phone and address. Lacks cross-channel web search footprint."
        else:
            discoverability = min(20, discoverability + 2)
            explanations["discoverability"] = f"Multi-channel search visibility established across Google profile and web domain."

        discoverability = max(4, discoverability)

        # -------------------------------------------------------------
        # 2. BRAND & POSITIONING (Max 15)
        # -------------------------------------------------------------
        brand_positioning = 0
        name_words = len(identity.business_name.split())
        if name_words >= 2 and not identity.business_name.startswith("http"):
            brand_positioning += 6
        else:
            brand_positioning += 3

        if identity.category and identity.category != "Local Business":
            brand_positioning += 4
        else:
            brand_positioning += 2

        if has_website:
            brand_positioning += 3  # Owned digital identity
            brand_positioning += 2  # Visible value proposition on domain
            brand_text = f"Clear category positioning under {identity.business_name} with dedicated brand domain."
        else:
            # Without owned website, brand relies solely on directory listing
            brand_text = f"Established local trade name, but absence of an owned digital destination restricts brand positioning."

        explanations["brand_identity"] = brand_text
        explanations["brand_positioning"] = brand_text

        brand_positioning = min(15, max(3, brand_positioning))

        # -------------------------------------------------------------
        # 3. TRUST & REPUTATION (Max 20)
        # -------------------------------------------------------------
        cat_str = ((identity.category or "") + " " + identity.business_name).lower()
        if any(k in cat_str for k in ["dent", "implant", "clinic", "hospital", "doctor", "health", "physio"]):
            cust_term = "patient"
        elif any(k in cat_str for k in ["banquet", "resort", "venue", "hotel", "wedding"]):
            cust_term = "client and host"
        elif any(k in cat_str for k in ["school", "college", "academy", "education"]):
            cust_term = "parent and student"
        elif any(k in cat_str for k in ["salon", "spa", "beauty"]):
            cust_term = "client"
        elif any(k in cat_str for k in ["restaurant", "cafe", "dining", "bistro"]):
            cust_term = "guest"
        elif any(k in cat_str for k in ["dairy", "fmcg", "food"]):
            cust_term = "consumer"
        else:
            cust_term = "customer"

        trust_reputation = 0
        if identity.rating is not None:
            if identity.rating >= 4.7:
                trust_reputation += 14
            elif identity.rating >= 4.3:
                trust_reputation += 11
            elif identity.rating >= 4.0:
                trust_reputation += 8
            else:
                trust_reputation += 4

            if identity.review_count:
                if identity.review_count >= 300:
                    trust_reputation += 5
                elif identity.review_count >= 100:
                    trust_reputation += 4
                elif identity.review_count >= 30:
                    trust_reputation += 2
                else:
                    trust_reputation += 1

            trust_reputation = min(20, trust_reputation)
            rev_text = f" across {identity.review_count} verified reviews" if identity.review_count else ""
            explanations["trust_reputation"] = f"Exceptional {cust_term} trust with a {identity.rating}★ rating on Google{rev_text}."
        else:
            trust_reputation = 10  # neutral unknown
            explanations["trust_reputation"] = f"Insufficient public {cust_term} reviews to establish independent trust metrics."

        # -------------------------------------------------------------
        # 4. DIGITAL EXPERIENCE (Max 15)
        # -------------------------------------------------------------
        if not has_website:
            # RULE A: No website = 0 / 15 (if absolutely no owned destination)
            digital_experience = 0
            web_exp_text = "No verified website or owned digital destination was found during the audit."
        else:
            digital_experience = 5
            if has_https:
                digital_experience += 2
            if has_mobile_vp:
                digital_experience += 3
            if has_phone or has_whatsapp:
                digital_experience += 2
            
            # Check response signals if available
            perf_evidence = [e for e in evidence if "performance" in e.field.lower() or "speed" in e.field.lower()]
            if perf_evidence and perf_evidence[0].status == "FAIL":
                digital_experience = max(3, digital_experience - 3)
                web_exp_text = "Website exists but displays performance delays and mobile friction."
            else:
                digital_experience = min(15, digital_experience + 3)
                web_exp_text = "Active web destination verified with responsive layout and security protocols."

        explanations["website_experience"] = web_exp_text
        explanations["digital_experience"] = web_exp_text

        digital_experience = min(15, max(0, digital_experience))

        # -------------------------------------------------------------
        # 5. LEAD CONVERSION (Max 20)
        # -------------------------------------------------------------
        lead_conversion = 0
        if not has_website:
            # RULE B: Local high-value business without website cannot exceed 8 / 20
            if has_phone:
                lead_conversion = 4
                explanations["lead_conversion"] = "Google Maps provides phone access, but no verified web, enquiry, booking or WhatsApp destination was identified."
            else:
                lead_conversion = 1
                explanations["lead_conversion"] = "No direct digital enquiry, booking, or phone conversion pathway identified."
        else:
            lead_conversion = 6
            if has_phone:
                lead_conversion += 4
            if has_whatsapp:
                lead_conversion += 6
            if has_interactive_enquiry:
                lead_conversion += 4
            lead_conversion = min(20, max(5, lead_conversion))
            if has_whatsapp:
                explanations["lead_conversion"] = "Direct interactive conversion channels available including phone and WhatsApp."
            else:
                explanations["lead_conversion"] = "Standard contact options present; lacks friction-free instant WhatsApp routing."

        # -------------------------------------------------------------
        # 6. SOCIAL PRESENCE (Max 10)
        # -------------------------------------------------------------
        if has_social:
            social_presence = 8
            explanations["social_presence"] = "Verified active social media touchpoints integrated with business identity."
        else:
            social_presence = 5  # neutral unknown, do not penalize excessively
            explanations["social_presence"] = "No verified public Instagram or Facebook connectivity detected on primary listing."

        # -------------------------------------------------------------
        # OVERALL SCORE CALCULATION & CRITICAL MATURITY CAPS
        # -------------------------------------------------------------
        raw_score = (
            discoverability +
            brand_positioning +
            trust_reputation +
            digital_experience +
            lead_conversion +
            social_presence
        )

        overall_score = raw_score

        # RULE C: Cap 1 (NO WEBSITE) -> Maximum 59 / 100
        if not has_website:
            overall_score = min(59, overall_score)

        # RULE D: Cap 2 (NO WEBSITE + NO DIRECT INTERACTIVE CONVERSION) -> Maximum 54 / 100
        if not has_website and not has_whatsapp:
            overall_score = min(54, overall_score)

        overall_score = max(0, min(100, overall_score))

        # -------------------------------------------------------------
        # SCORE BANDS & COMMERCIAL TIER
        # -------------------------------------------------------------
        if overall_score < 40:
            maturity_band = "CRITICAL DIGITAL GAP"
            commercial_tier = "FOUNDATION"
        elif overall_score <= 54:
            maturity_band = "SIGNIFICANT OPPORTUNITY"
            commercial_tier = "FOUNDATION"
        elif overall_score <= 69:
            maturity_band = "DEVELOPING DIGITAL PRESENCE"
            commercial_tier = "GROWTH"
        elif overall_score <= 84:
            maturity_band = "STRONG DIGITAL PRESENCE"
            commercial_tier = "ADVANCED"
        else:
            maturity_band = "HIGH-PERFORMING DIGITAL PRESENCE"
            commercial_tier = "ADVANCED"

        return AuditScore(
            overall_score=overall_score,
            discoverability=discoverability,
            brand_identity=brand_positioning,
            trust_reputation=trust_reputation,
            website_experience=digital_experience,
            lead_conversion=lead_conversion,
            social_presence=social_presence,
            brand_positioning=brand_positioning,
            digital_experience=digital_experience,
            maturity_band=maturity_band,
            business_type=business_type,
            commercial_tier=commercial_tier,
            dimension_explanations=explanations
        )
