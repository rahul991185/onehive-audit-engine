from pathlib import Path
from typing import Tuple, List, Dict
from app.models.schemas import BusinessIdentity, AuditScore, Opportunity, SalesBrief
from app.config import SALESPACKS_DIR

class SalesBriefEngine:
    """
    Generates internal-only commercial intelligence briefs for OneHive sales executives.
    Includes account profile, prospect type, commercial tier, and a strict 'WHAT NOT TO SAY' vs 'SAY INSTEAD' table.
    """

    @staticmethod
    def generate(
        audit_id: str,
        identity: BusinessIdentity,
        scores: AuditScore,
        strongest_asset: str,
        biggest_gap: str,
        opp: Opportunity
    ) -> Tuple[SalesBrief, Path]:
        name = identity.business_name
        industry = identity.category or "Local Business"
        location = identity.city or "Local Area"
        b_type = scores.business_type or "LOCAL_FIRST"
        tier = scores.commercial_tier or "FOUNDATION"

        confidence_str = f"HIGH ({int(identity.identity_confidence * 100)}% verified)" if identity.identity_confidence >= 0.8 else f"MEDIUM ({int(identity.identity_confidence * 100)}% verified)"

        evidence_bullets = [f"• [{e.source}] {e.field}: {e.value}" for e in opp.evidence]

        has_website = bool(identity.website and identity.website.strip())
        domain_label = identity.website.split("//")[-1].split("/")[0].replace("www.", "") if has_website else ""

        cat_low = ((identity.category or "") + " " + name).lower()
        if any(k in cat_low for k in ["dent", "implant", "clinic", "hospital", "doctor", "health", "physio"]):
            prospect_noun = "patients"
            action_noun = "consultations"
        elif any(k in cat_low for k in ["banquet", "resort", "venue", "hotel", "wedding"]):
            prospect_noun = "event hosts"
            action_noun = "venue bookings"
        elif any(k in cat_low for k in ["school", "college", "academy", "education"]):
            prospect_noun = "parents and students"
            action_noun = "campus visits"
        elif any(k in cat_low for k in ["dairy", "fmcg", "food"]):
            prospect_noun = "wholesale dealers and consumers"
            action_noun = "bulk orders"
        elif any(k in cat_low for k in ["interior", "architect"]):
            prospect_noun = "homeowners and commercial clients"
            action_noun = "design consultations"
        elif any(k in cat_low for k in ["salon", "spa", "beauty"]):
            prospect_noun = "clients"
            action_noun = "salon appointments"
        elif any(k in cat_low for k in ["restaurant", "cafe", "dining"]):
            prospect_noun = "diners"
            action_noun = "table reservations"
        else:
            prospect_noun = "clients and customers"
            action_noun = "enquiries"

        # Strategic rationale
        if has_website:
            why_this_account = f"{name} has already built an established digital destination on {domain_label}, but lacks a frictionless WhatsApp conversion bridge, creating drop-off between website visits and confirmed {action_noun}."
            current_state = f"Active branded web presence on {domain_label}, but inbound smartphone visitors face static contact forms without instant 1-click WhatsApp conversion routing."
            objection = f"'We already have a website on {domain_label} and receive calls.'"
            objection_resp = f"'Your website establishes strong brand credibility. However, mobile visitors seeking fast answers often abandon static contact forms. Adding a 1-click WhatsApp bridge converts smartphone traffic into direct, qualified {action_noun} immediately.'"
            next_step = f"Send the 2-Page Digital Presence Intelligence Report and demonstrate how adding a 1-click WhatsApp bridge to {domain_label} increases qualified inbound {action_noun}."
        else:
            why_this_account = f"{name} possesses strong local reputation and review volume, but lacks an owned digital funnel, making them a prime candidate for a high-converting presence build."
            current_state = f"High local discoverability backed by {identity.rating or 4.8}★ rating, but completely dependent on Google Maps phone clicks with zero owned web or online enquiry infrastructure."
            objection = f"'We already receive {prospect_noun} calls from Google Maps / We don't need a website.'"
            objection_resp = f"'Phone calls are valuable when your team is available to answer. However, having a dedicated mobile destination and 1-click WhatsApp bridge allows interested {prospect_noun} to review your offerings and initiate enquiries 24/7 at their own convenience.'"
            next_step = f"Send the 2-Page Digital Presence Intelligence Report (Page 2 Opportunity Roadmap) and walk through the 1-click WhatsApp enquiry routing flow."

        # Sales safety table: WHAT NOT TO SAY vs SAY INSTEAD
        what_not_to_say = [
            {
                "do_not_say": "You are losing customers every day without a website.",
                "say_instead": "Your current journey has fewer digital next-step options for interested prospects who want to explore services online."
            },
            {
                "do_not_say": "Your digital setup is costing you revenue.",
                "say_instead": "Your current journey creates friction between local discovery and confirmed consultations."
            },
            {
                "do_not_say": "Most of your customers search outside standard office hours.",
                "say_instead": "An owned digital destination provides prospects 24/7 service exploration and pre-filled inquiry routing."
            },
            {
                "do_not_say": "We will guarantee 5-star reviews and top Google rankings.",
                "say_instead": "We deploy compliant review-request workflows that make it simple for satisfied clients to share genuine feedback."
            }
        ]

        likely_trigger = f"Desire to capture more direct high-intent {industry.lower()} enquiries and present services professionally without recurring ad spend."
        sales_angle = f"Validate their verified local reputation first ({strongest_asset}). Position OneHive as the engineering team that builds the missing bridge from that discovery to direct WhatsApp consultations."
        opening_msg = f"'{name}, your local presence in {location} has established excellent trust. We noticed interested visitors have no instant digital path to explore services or book a consultation. We created a personalized concept showing what this could look like. Would you like to review it?'"

        sales_brief = SalesBrief(
            business_name=name,
            industry=industry,
            location=location,
            website=identity.website,
            identity_confidence=confidence_str,
            overall_score=scores.overall_score,
            scores=scores,
            strongest_asset=strongest_asset,
            biggest_gap=biggest_gap,
            top_opportunity=opp.title,
            why_it_matters=opp.why_it_matters,
            evidence_highlights=evidence_bullets,
            recommended_service=opp.recommended_service,
            likely_buying_trigger=likely_trigger,
            sales_angle=sales_angle,
            opening_message=opening_msg,
            objection_to_expect=objection,
            objection_response=objection_resp,
            recommended_next_step=next_step,
            business_type=b_type,
            commercial_tier=tier,
            what_not_to_say=what_not_to_say
        )

        # Write text version for sales pack
        out_path = SALESPACKS_DIR / f"{audit_id}_sales_brief.txt"
        safety_text = "\n".join([f"• DO NOT SAY: \"{s['do_not_say']}\"\n  SAY INSTEAD: \"{s['say_instead']}\"" for s in what_not_to_say])

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(f"""============================================================
ONEHIVE INTERNAL SALES INTELLIGENCE BRIEF
STRICTLY INTERNAL — NOT FOR PROSPECT DISTRIBUTION
============================================================

PROSPECT PROFILE:
Business:        {name}
Industry:        {industry}
Location:        {location}
Prospect Type:   {b_type}
Commercial Tier: {tier}
Website:         {identity.website or 'None configured'}
Identity Conf:   {confidence_str}

ACCOUNT CONTEXT:
Why This Account: {why_this_account}
Current State:    {current_state}

DIAGNOSTIC BENCHMARK:
Overall Score:       {scores.overall_score} / 100 ({scores.maturity_band})
- Discoverability:   {scores.discoverability} / 20 ({scores.dimension_explanations.get('discoverability', '')})
- Brand & Identity:  {scores.brand_identity} / 15 ({scores.dimension_explanations.get('brand_positioning', '')})
- Trust & Reputation:{scores.trust_reputation} / 20 ({scores.dimension_explanations.get('trust_reputation', '')})
- Digital Experience:{scores.website_experience} / 15 ({scores.dimension_explanations.get('digital_experience', '')})
- Lead Conversion:   {scores.lead_conversion} / 20 ({scores.dimension_explanations.get('lead_conversion', '')})
- Social Presence:   {scores.social_presence} / 10 ({scores.dimension_explanations.get('social_presence', '')})

KEY OBSERVATIONS:
Strongest Asset: {strongest_asset}
Primary Gap:     {biggest_gap}

THE #1 GROWTH OPPORTUNITY:
{opp.title}

WHY THIS MATTERS:
{opp.why_it_matters}

EVIDENCE BASE:
{chr(10).join(evidence_bullets)}

COMMERCIAL STRATEGY:
Recommended Package:   {opp.recommended_service}
Likely Buying Trigger: {likely_trigger}
Sales Angle:           {sales_angle}

SALES SAFETY: WHAT NOT TO SAY vs SAY INSTEAD:
------------------------------------------------------------
{safety_text}
------------------------------------------------------------

OPENING SCRIPT:
{opening_msg}

ANTICIPATED OBJECTION & RESPONSE:
Objection: {objection}
Response:  {objection_resp}

RECOMMENDED NEXT ACTION:
{next_step}
============================================================""")

        return sales_brief, out_path
