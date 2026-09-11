from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from app.models.schemas import BusinessIdentity, AuditScore, Opportunity, Recommendation
from app.config import ONEHIVE_PHONE, ONEHIVE_EMAIL, ONEHIVE_WEBSITE

class ReportV2Adapter:
    """
    Transforms audit data into exact visual data structures required by the
    2-Page OneHive Digital Presence Intelligence Report.
    """

    @staticmethod
    def get_tagline(identity: BusinessIdentity) -> str:
        if identity.tagline:
            return identity.tagline
        cat_lower = ((identity.category or "") + " " + identity.business_name).lower()
        if any(k in cat_lower for k in ["dent", "teeth", "ortho", "implant", "clinic", "doctor"]):
            return "Your Smile. Our Priority."
        if any(k in cat_lower for k in ["interior", "decor", "architect", "design"]):
            return "Transforming Spaces. Elevating Living."
        if any(k in cat_lower for k in ["school", "academy", "education", "vidya", "institute"]):
            return "Nurturing Potential. Building Futures."
        if any(k in cat_lower for k in ["banquet", "venue", "lawn", "marriage", "wedding", "resort"]):
            return "Memorable Celebrations. Grand Hospitality."
        if any(k in cat_lower for k in ["dairy", "milk", "khoya", "paneer", "ghee", "fmcg", "beverage", "food"]):
            return "Pure Quality. Fresh Every Day."
        if any(k in cat_lower for k in ["restaurant", "cafe", "dining", "bistro", "bakery"]):
            return "Exceptional Flavors. Unforgettable Moments."
        if any(k in cat_lower for k in ["salon", "beauty", "spa", "wellness", "hair", "skin"]):
            return "Elevating Beauty. Inspiring Confidence."
        if any(k in cat_lower for k in ["auto", "car", "motor", "repair", "detailing"]):
            return "Precision Engineering. Reliable Care."
        if any(k in cat_lower for k in ["real estate", "property", "realtor", "builder"]):
            return "Exceptional Properties. Trusted Investments."
        if any(k in cat_lower for k in ["manufacturing", "industrial", "fabrication", "machinery"]):
            return "Engineered Precision. Industrial Excellence."
        if any(k in cat_lower for k in ["law", "legal", "tax", "ca ", "consulting", "advisory"]):
            return "Strategic Insight. Trusted Counsel."
        if any(k in cat_lower for k in ["plumbing", "electrical", "hvac", "contractor", "cleaning"]):
            return "Fast Response. Dependable Craftsmanship."
        return "Delivering Quality. Building Customer Trust."

    @staticmethod
    def get_business_model(identity: BusinessIdentity) -> Dict[str, str]:
        btype = identity.business_type or "LOCAL_FIRST"
        cat_lower = ((identity.category or "") + " " + identity.business_name).lower()

        if any(k in cat_lower for k in ["dairy", "milk", "khoya", "paneer", "ghee", "fmcg", "food"]):
            return {
                "title": "Product & Distribution First",
                "desc": "Builds brand equity through retail distribution networks, quality assurance, and direct wholesale inquiries."
            }
        elif btype == "ADMISSION_FIRST" or any(k in cat_lower for k in ["school", "college", "academy", "education"]):
            return {
                "title": "Admission-First",
                "desc": "Engages prospective students and families through local reputation and admissions counseling."
            }
        elif btype == "BOOKING_FIRST" or any(k in cat_lower for k in ["banquet", "resort", "venue", "wedding"]):
            return {
                "title": "Booking-First",
                "desc": "Captures event and hospitality bookings through direct date inquiries and venue tours."
            }
        elif btype == "PROJECT_FIRST" or any(k in cat_lower for k in ["interior", "architect", "decor", "design"]):
            return {
                "title": "Project-First",
                "desc": "Converts visual portfolio attention into customized design and architecture consultations."
            }
        elif any(k in cat_lower for k in ["manufacturing", "industrial", "fabrication", "machinery"]):
            return {
                "title": "B2B & Specification-First",
                "desc": "Engages procurement managers and B2B buyers through technical specifications and direct RFQ inquiries."
            }
        elif any(k in cat_lower for k in ["dent", "clinic", "doctor", "health", "salon", "spa", "auto", "repair"]):
            return {
                "title": "Appointment-First",
                "desc": "Converts local customer interest directly into confirmed service appointments and consultations."
            }
        elif btype == "WEBSITE_FIRST":
            return {
                "title": "Website-First",
                "desc": "Drives customer engagement through an owned web destination and multi-channel marketing."
            }
        elif btype == "SOCIAL_FIRST":
            return {
                "title": "Social-First",
                "desc": "Connects with audience primarily through social channels and direct messaging."
            }
        else:
            return {
                "title": "Local-First",
                "desc": "Primarily serves local customers through Google Maps and direct enquiries."
            }

    @staticmethod
    def get_score_tier(score: int) -> Dict[str, str]:
        if score >= 80:
            return {
                "label": "STRONG DIGITAL PRESENCE",
                "class": "strong",
                "color": "#15803D",
                "bg": "#DCFCE7",
                "border": "#86EFAC"
            }
        elif score >= 65:
            return {
                "label": "GOOD FOUNDATION",
                "class": "good",
                "color": "#854D0E",
                "bg": "#FEF08A",
                "border": "#FDE047"
            }
        elif score >= 50:
            return {
                "label": "DEVELOPING",
                "class": "developing",
                "color": "#C2410C",
                "bg": "#FFEDD5",
                "border": "#FDBA74"
            }
        else:
            return {
                "label": "NEEDS ATTENTION",
                "class": "attention",
                "color": "#B91C1C",
                "bg": "#FEE2E2",
                "border": "#FCA5A5"
            }

    @staticmethod
    def build_page_data(
        audit_id: str,
        identity: BusinessIdentity,
        scores: AuditScore,
        strongest_asset: str,
        biggest_gap: str,
        opp: Opportunity,
        recommendations: List[Recommendation],
        evidence: Optional[List[Any]] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        has_website = bool(identity.website and identity.website.strip())
        has_rating = bool(identity.rating)
        rating_val = f"{identity.rating:.1f}" if has_rating else "N/A"
        rev_count = identity.review_count or 0
        extra = extra_data or {}
        ev_list = evidence or []

        rating_display = f"{rating_val} ★ ({rev_count}+ verified reviews)" if has_rating else "Not Detected"
        tagline = ReportV2Adapter.get_tagline(identity)
        model_info = ReportV2Adapter.get_business_model(identity)
        tier_info = ReportV2Adapter.get_score_tier(scores.overall_score)

        cat_lower = ((identity.category or "") + " " + identity.business_name).lower()
        detected_services = extra.get("detected_services", [])
        has_whatsapp = bool(identity.whatsapp_url) or any("whatsapp" in getattr(e, "field", "").lower() and getattr(e, "status", "") == "PASS" for e in ev_list)

        # -------------------------------------------------------------
        # 1. Industry Domain Mapping
        # -------------------------------------------------------------
        if any(k in cat_lower for k in ["dent", "teeth", "ortho", "implant"]):
            entity_noun = "your dental clinic"
            customer_noun = "patients"
            customer_noun_single = "patient"
            service_noun = "dental treatments & doctor credentials"
            enquiry_noun = "consultation appointments"
            enquiry_action_noun = "consultation booking request"
            confirmed_title = "Consultation Booked"
            subheading_p2 = "Turn your strong reputation into more consultation enquiries."
            opp_title = opp.title or "Turn Digital Clinic Visitors into Direct Consultation Enquiries"
            opp_desc = opp.finding or "You have excellent patient trust and local visibility. The next step is to create a strong digital booking system that converts search interest into scheduled visits."
            first_move = "Mobile-First Clinic Website + WhatsApp Booking System"
            first_move_desc = "A dedicated digital presence to showcase your clinic, treatments, and patient trust with instant enquiry options like WhatsApp and online booking."
            cta_text = "We'd love to walk you through a personalized demo of how we can help you generate more patient bookings and grow your practice."
            add_opp_1 = {"title": "Local Dental SEO", "desc": "Strengthen local high-intent search visibility", "icon": "map_pin", "color": "#2563EB", "bg_class": "blue-bg"}
            add_opp_2 = {"title": "Patient Social Proof", "desc": "Build active Instagram clinical portfolio", "icon": "instagram", "color": "#9333EA", "bg_class": "purple-bg"}
            add_opp_3 = {"title": "AI Appointment Assistant", "desc": "Automate after-hours patient enquiry triage", "icon": "bot", "color": "#D97706", "bg_class": "yellow-bg"}

        elif any(k in cat_lower for k in ["clinic", "hospital", "doctor", "health", "physio", "eye", "ayur"]):
            entity_noun = "your healthcare practice"
            customer_noun = "patients"
            customer_noun_single = "patient"
            service_noun = "specialist medical services & care protocols"
            enquiry_noun = "consultation appointments"
            enquiry_action_noun = "appointment request"
            confirmed_title = "Appointment Confirmed"
            subheading_p2 = "Turn patient discovery into confirmed medical consultations."
            opp_title = opp.title or "Turn Patient Discovery Into Direct Scheduled Consultations"
            opp_desc = opp.finding or "Patients researching medical care evaluate doctor credentials and care options. A dedicated healthcare portal accelerates confirmed bookings."
            first_move = "Specialty Healthcare Portal + Instant WhatsApp Triage"
            first_move_desc = "A dedicated digital destination presenting medical specializations, credentials, and transparent consultation booking."
            cta_text = "We'd love to walk you through a personalized demo of how we can help you streamline patient appointments and grow your healthcare practice."
            add_opp_1 = {"title": "Medical Authority SEO", "desc": "Rank for high-intent local healthcare searches", "icon": "map_pin", "color": "#2563EB", "bg_class": "blue-bg"}
            add_opp_2 = {"title": "Patient Care Stories", "desc": "Highlight treatment outcomes and patient reviews", "icon": "shield", "color": "#16A34A", "bg_class": "green-bg"}
            add_opp_3 = {"title": "WhatsApp Clinic Concierge", "desc": "Automate 24/7 patient enquiry handling", "icon": "bot", "color": "#D97706", "bg_class": "yellow-bg"}

        elif any(k in cat_lower for k in ["dairy", "milk", "khoya", "paneer", "ghee", "fmcg", "beverage", "packaged food", "agro"]):
            entity_noun = "your brand & products"
            customer_noun = "retail consumers & wholesale partners"
            customer_noun_single = "customer & distributor"
            service_noun = "product range, purity assurance & retail outlets"
            enquiry_noun = "wholesale & consumer orders"
            enquiry_action_noun = "dealership or bulk order inquiry"
            confirmed_title = "Distribution Lead Secured"
            subheading_p2 = "Turn brand discovery into direct wholesale & retail orders."
            opp_title = opp.title or "Convert Brand Discovery Into Direct Wholesale & Retail Inquiries"
            opp_desc = opp.finding or "Consumers and commercial partners explore product purity and retail availability. An interactive digital catalog connects interest to direct orders."
            first_move = "Interactive Product Showcase + WhatsApp Wholesale Ordering"
            first_move_desc = "A visual digital destination showcasing product quality, nutritional assurance, and instant WhatsApp dealership and bulk order routing."
            cta_text = "We'd love to walk you through a personalized demo of how we can help you expand wholesale distribution and connect directly with consumers."
            add_opp_1 = {"title": "Store Locator & Retail SEO", "desc": "Help consumers find nearby retail stockists", "icon": "map_pin", "color": "#2563EB", "bg_class": "blue-bg"}
            add_opp_2 = {"title": "Social Brand Community", "desc": "Engage modern consumers across Instagram & YouTube", "icon": "instagram", "color": "#9333EA", "bg_class": "purple-bg"}
            add_opp_3 = {"title": "Wholesale Ordering Bot", "desc": "Automate dealer and bulk order inquiries via WhatsApp", "icon": "bot", "color": "#D97706", "bg_class": "yellow-bg"}

        elif any(k in cat_lower for k in ["interior", "decor", "architect", "design", "modular"]):
            entity_noun = "your design studio"
            customer_noun = "homeowners & commercial clients"
            customer_noun_single = "design client"
            service_noun = "portfolio craftsmanship & project process"
            enquiry_noun = "project design consultations"
            enquiry_action_noun = "project consultation request"
            confirmed_title = "Consultation Scheduled"
            subheading_p2 = "Turn your design portfolio into high-ticket project enquiries."
            opp_title = opp.title or "Turn Project Impressions Into High-Ticket Design Consultations"
            opp_desc = opp.finding or "Prospective clients evaluate visual portfolio depth before enquiring. A curated showcase accelerates decision-making."
            first_move = "Visual Portfolio Showcase + WhatsApp Consultation Routing"
            first_move_desc = "An editorial digital portfolio showcasing completed projects with direct WhatsApp design consultation booking."
            cta_text = "We'd love to walk you through a personalized demo of how we can help you showcase your projects and attract high-value design clients."
            add_opp_1 = {"title": "Architectural SEO", "desc": "Capture high-budget residential searchers", "icon": "map_pin", "color": "#2563EB", "bg_class": "blue-bg"}
            add_opp_2 = {"title": "Visual Storytelling", "desc": "Scale Instagram portfolio and site walkthroughs", "icon": "instagram", "color": "#9333EA", "bg_class": "purple-bg"}
            add_opp_3 = {"title": "Design Estimate Bot", "desc": "Qualify budget and room scope on WhatsApp", "icon": "bot", "color": "#D97706", "bg_class": "yellow-bg"}

        elif any(k in cat_lower for k in ["banquet", "venue", "lawn", "marriage", "wedding", "resort", "hotel", "convention"]):
            entity_noun = "your event venue"
            customer_noun = "event hosts & wedding planners"
            customer_noun_single = "confirmed event host"
            service_noun = "banquet spaces, capacities & catering packages"
            enquiry_noun = "venue date enquiries"
            enquiry_action_noun = "date availability check"
            confirmed_title = "Venue Tour Booked"
            subheading_p2 = "Turn event discovery into instant date availability enquiries."
            opp_title = opp.title or "Convert Event & Wedding Discovery Into Direct Venue Enquiries"
            opp_desc = opp.finding or "Prospective event hosts expect immediate visual tours and package details. A dedicated venue portal accelerates bookings."
            first_move = "Virtual Venue Showcase + Instant WhatsApp Date Availability"
            first_move_desc = "An interactive venue exploration experience allowing event hosts to check availability and request package quotes instantly."
            cta_text = "We'd love to walk you through a personalized demo of how we can help you showcase your venue and book more prime dates."
            add_opp_1 = {"title": "Wedding & Event SEO", "desc": "Rank for prime wedding venue searches in your city", "icon": "map_pin", "color": "#2563EB", "bg_class": "blue-bg"}
            add_opp_2 = {"title": "Event Gallery & Reels", "desc": "Highlight live decor and celebration highlights", "icon": "instagram", "color": "#9333EA", "bg_class": "purple-bg"}
            add_opp_3 = {"title": "Date Availability Bot", "desc": "Instant automated date availability check via WhatsApp", "icon": "bot", "color": "#D97706", "bg_class": "yellow-bg"}

        elif any(k in cat_lower for k in ["school", "academy", "education", "vidya", "institute", "coaching"]):
            entity_noun = "your educational institution"
            customer_noun = "parents & students"
            customer_noun_single = "enrolled student"
            service_noun = "academic curriculum, faculty & campus facilities"
            enquiry_noun = "admission enquiries"
            enquiry_action_noun = "campus tour & admissions request"
            confirmed_title = "Campus Visit Scheduled"
            subheading_p2 = "Turn local discovery into direct admission enquiries."
            opp_title = opp.title or "Streamline Inbound Admissions Enquiries & Campus Visits"
            opp_desc = opp.finding or "Parents researching programs need clear curriculum highlights and direct campus visit booking pathways."
            first_move = "Interactive Admissions Experience + Campus Tour Booking"
            first_move_desc = "A modern parent-facing digital destination providing curriculum clarity, fee overviews, and direct admission counselling routing."
            cta_text = "We'd love to walk you through a personalized demo of how we can help you streamline parent admissions and campus tour bookings."
            add_opp_1 = {"title": "Admissions Search SEO", "desc": "Capture parents researching local schools & academies", "icon": "map_pin", "color": "#2563EB", "bg_class": "blue-bg"}
            add_opp_2 = {"title": "Campus Life Socials", "desc": "Showcase student achievements and academic culture", "icon": "instagram", "color": "#9333EA", "bg_class": "purple-bg"}
            add_opp_3 = {"title": "Admissions Counselling Bot", "desc": "Automate syllabus and fee queries via WhatsApp", "icon": "bot", "color": "#D97706", "bg_class": "yellow-bg"}

        elif any(k in cat_lower for k in ["salon", "beauty", "spa", "wellness", "hair", "skin", "makeup"]):
            entity_noun = "your salon & wellness studio"
            customer_noun = "clients & guests"
            customer_noun_single = "salon client"
            service_noun = "treatment menu, hair styling & wellness packages"
            enquiry_noun = "salon appointment bookings"
            enquiry_action_noun = "stylist appointment booking"
            confirmed_title = "Appointment Confirmed"
            subheading_p2 = "Turn treatment discovery into confirmed salon appointments."
            opp_title = opp.title or "Turn Styling & Treatment Discovery Into Confirmed Appointments"
            opp_desc = opp.finding or "Clients evaluate styling work and price menus on their smartphones. A digital treatment menu with 1-click booking fills appointment books."
            first_move = "Visual Treatment Menu + WhatsApp Stylist Booking"
            first_move_desc = "A stylish mobile menu showcasing hair, skin, and wellness treatments with direct WhatsApp appointment scheduling."
            cta_text = "We'd love to walk you through a personalized demo of how we can help you attract more clients and fill your appointment calendar."
            add_opp_1 = {"title": "Beauty & Salon SEO", "desc": "Capture local searches for hair & skin treatments", "icon": "map_pin", "color": "#2563EB", "bg_class": "blue-bg"}
            add_opp_2 = {"title": "Styling Portfolio & Reels", "desc": "Showcase client transformations on Instagram", "icon": "instagram", "color": "#9333EA", "bg_class": "purple-bg"}
            add_opp_3 = {"title": "Automated Booking Concierge", "desc": "Instant slot reservation and confirmation on WhatsApp", "icon": "bot", "color": "#D97706", "bg_class": "yellow-bg"}

        elif any(k in cat_lower for k in ["restaurant", "cafe", "dining", "menu", "bistro", "bakery", "lounge"]):
            entity_noun = "your dining venue"
            customer_noun = "diners & food lovers"
            customer_noun_single = "diner"
            service_noun = "culinary menu, chef specials & ambiance"
            enquiry_noun = "table reservations & orders"
            enquiry_action_noun = "table reservation request"
            confirmed_title = "Table Reserved"
            subheading_p2 = "Turn food discovery into direct table reservations."
            opp_title = opp.title or "Convert Dining Discovery Into Confirmed Table Reservations"
            opp_desc = opp.finding or "Guests explore visual menus and guest reviews before dining out. An interactive digital menu secures reservations instantly."
            first_move = "Digital Visual Menu + WhatsApp Table Booking"
            first_move_desc = "A mobile-first visual menu showcasing culinary specialties and ambiance with direct 1-click WhatsApp reservations."
            cta_text = "We'd love to walk you through a personalized demo of how we can help you increase table bookings and orders."
            add_opp_1 = {"title": "Local Dining SEO", "desc": "Top rankings for dining and restaurant searches", "icon": "map_pin", "color": "#2563EB", "bg_class": "blue-bg"}
            add_opp_2 = {"title": "Foodie Instagram Engine", "desc": "Turn mouth-watering food photos into regular diners", "icon": "instagram", "color": "#9333EA", "bg_class": "purple-bg"}
            add_opp_3 = {"title": "Table & Takeaway Bot", "desc": "Automate table booking and takeaway orders on WhatsApp", "icon": "bot", "color": "#D97706", "bg_class": "yellow-bg"}

        elif any(k in cat_lower for k in ["auto", "car", "motor", "repair", "detailing", "garage", "tyre"]):
            entity_noun = "your automotive workshop"
            customer_noun = "vehicle owners"
            customer_noun_single = "customer"
            service_noun = "transparent service packages & maintenance scopes"
            enquiry_noun = "service bay bookings"
            enquiry_action_noun = "service slot booking request"
            confirmed_title = "Service Slot Booked"
            subheading_p2 = "Turn vehicle service searches into scheduled workshop bays."
            opp_title = opp.title or "Turn Vehicle Service Searches Into Confirmed Workshop Bookings"
            opp_desc = opp.finding or "Vehicle owners look for pricing clarity and dependable care. A transparent package menu with instant WhatsApp booking secures bookings."
            first_move = "Transparent Service Menu + Instant Workshop Bay Booking"
            first_move_desc = "A mobile service portal presenting transparent maintenance packages with instant WhatsApp slot scheduling."
            cta_text = "We'd love to walk you through a personalized demo of how we can help you fill workshop bays and grow customer retention."
            add_opp_1 = {"title": "Automotive Local SEO", "desc": "Capture urgent car repair and service searches", "icon": "map_pin", "color": "#2563EB", "bg_class": "blue-bg"}
            add_opp_2 = {"title": "Workshop Craftsmanship Proof", "desc": "Showcase detailing and maintenance work on Instagram", "icon": "instagram", "color": "#9333EA", "bg_class": "purple-bg"}
            add_opp_3 = {"title": "Instant Estimate Bot", "desc": "Generate instant repair estimates via WhatsApp", "icon": "bot", "color": "#D97706", "bg_class": "yellow-bg"}

        else:
            entity_noun = "your business"
            customer_noun = "prospective customers"
            customer_noun_single = "active customer"
            service_noun = "core services & customer guarantees"
            enquiry_noun = "customer enquiries"
            enquiry_action_noun = "direct service enquiry"
            confirmed_title = "Client Confirmed"
            subheading_p2 = "Turn customer awareness into direct business enquiries."
            opp_title = opp.title or "Establish an Owned Digital Destination to Capture Local Inbound Demand"
            opp_desc = opp.finding or "You have built customer trust locally. The next step is to create a seamless digital pathway that turns interest into enquiries."
            first_move = "Mobile-First Business Website + Direct WhatsApp Routing"
            first_move_desc = "A professional, mobile-first web presence connecting prospective clients directly with your team."
            cta_text = "We'd love to walk you through a personalized demo of how we can help you generate more customer enquiries and grow your business."
            add_opp_1 = {"title": "Local SEO Enhancement", "desc": "Strengthen high-intent local search visibility", "icon": "map_pin", "color": "#2563EB", "bg_class": "blue-bg"}
            add_opp_2 = {"title": "Social Media Growth", "desc": "Build an active, engaging brand presence", "icon": "instagram", "color": "#9333EA", "bg_class": "purple-bg"}
            add_opp_3 = {"title": "AI Appointment Assistant", "desc": "Automate after-hours enquiry triage and routing", "icon": "bot", "color": "#D97706", "bg_class": "yellow-bg"}

        # -------------------------------------------------------------
        # 2. Dynamic Narrative for Overall Score
        # -------------------------------------------------------------
        if scores.overall_score >= 75:
            score_narrative = f"Your business has a strong digital footprint with verified trust signals. Streamlining direct conversion pathways will turn more interested searchers into active {enquiry_noun}."
        elif scores.overall_score >= 60:
            score_narrative = f"Your business has built valuable local trust and recognition. Creating a direct, conversion-focused enquiry path will help convert more interested {customer_noun}."
        elif not has_website:
            score_narrative = f"Your local reputation is strong, but the absence of an owned website limits your ability to capture and convert prospective {customer_noun} searching online."
        else:
            score_narrative = f"Your online presence establishes awareness, but friction across the discovery and conversion path represents an immediate growth opportunity."

        # -------------------------------------------------------------
        # 3. Observations: What's Already Working (3 personalized points)
        # -------------------------------------------------------------
        working_bullets = []
        domain_label = identity.website.split("//")[-1].split("/")[0].replace("www.", "") if has_website else ""
        loc_suffix = f" in {identity.city}" if identity.city and identity.city != "Local Area" else ""
        
        # Point 1: Trust & Reputation
        if has_rating and identity.rating >= 4.5 and rev_count >= 50:
            working_bullets.append(f"High {customer_noun_single} trust with a {rating_val}★ rating on Google across {rev_count}+ verified reviews{loc_suffix}.")
        elif has_rating and identity.rating >= 4.0:
            working_bullets.append(f"Positive {customer_noun_single} sentiment with a verified {rating_val}★ rating on Google Maps ({rev_count} reviews).")
        elif has_website:
            working_bullets.append(f"Established digital brand destination under '{identity.business_name}' accessible on {domain_label}.")
        elif identity.address:
            working_bullets.append(f"Verified physical business presence on Google Maps at {identity.address}.")
        else:
            working_bullets.append(f"Recognized commercial standing under '{identity.business_name}'{loc_suffix}.")

        # Point 2: Core Offerings & Digital Assets
        if detected_services and len(detected_services) >= 2:
            working_bullets.append(f"Visible product and service portfolio showcasing core offerings ({', '.join(detected_services[:3])}).")
        elif has_website:
            working_bullets.append(f"Dedicated branded website ({domain_label}) establishing an owned digital footprint.")
        elif identity.phone:
            working_bullets.append(f"Direct voice contact line ({identity.phone}) accessible to local searchers.")
        else:
            working_bullets.append(f"Established local presence serving {customer_noun}{loc_suffix}.")

        # Point 3: Channel Engagement & Verification
        if has_whatsapp:
            working_bullets.append(f"Active WhatsApp messaging bridge configured for direct {customer_noun_single} communications.")
        elif identity.instagram_url or identity.facebook_url:
            social_channels = []
            if identity.instagram_url: social_channels.append("Instagram")
            if identity.facebook_url: social_channels.append("Facebook")
            working_bullets.append(f"Connected multi-channel footprint with verified {' & '.join(social_channels)} integration.")
        elif any("ssl" in getattr(e, "field", "").lower() and getattr(e, "status", "") == "PASS" for e in ev_list):
            working_bullets.append(f"Secure SSL encrypted web protocol verified on {domain_label} for customer protection.")
        else:
            working_bullets.append(f"Active commercial profile with verified details{loc_suffix}.")

        # -------------------------------------------------------------
        # 4. Observations: What Needs Attention (3 personalized points)
        # -------------------------------------------------------------
        attention_bullets = []

        # Gap 1: Digital Destination / Primary Conversion Asset
        if not has_website:
            attention_bullets.append(f"No owned website — prospective {customer_noun} searching on Google cannot review your full {service_noun} or book after reception hours.")
        elif not has_whatsapp:
            attention_bullets.append(f"Missing direct WhatsApp conversion bridge on {domain_label} — mobile visitors must navigate manual contact forms or dial phone numbers, leading to enquiry drop-off.")
        else:
            attention_bullets.append(f"Mobile conversion funnel on {domain_label} lacks sticky action bars and structured triage to capture impulse enquiries from smartphone visitors.")

        # Gap 2: Mobile & Conversion Friction
        if not has_website:
            attention_bullets.append(f"Enquiry pathway relies strictly on telephone calls during working hours, causing lead drop-off during peak evening search times.")
        elif any("viewport" in getattr(e, "field", "").lower() and getattr(e, "status", "") != "PASS" for e in ev_list):
            attention_bullets.append(f"Website layout on {domain_label} is not optimized for modern smartphone viewports, creating zoom friction for mobile visitors.")
        else:
            attention_bullets.append(f"Absence of an automated after-hours response workflow on {domain_label} to qualify inbound {enquiry_noun} and capture buyer contact details instantly.")

        # Gap 3: Social Proof & Acquisition Engine
        if not identity.instagram_url and not identity.facebook_url:
            attention_bullets.append(f"Unclaimed or unverified presence on Instagram & Facebook, leaving visual brand storytelling and {customer_noun} engagement untapped.")
        elif not rev_count or rev_count < 30:
            attention_bullets.append(f"Review volume ({rev_count} reviews) is under-leveraged — lacks an automated, compliant review-generation system to dominate local search.")
        else:
            attention_bullets.append(f"Social channels and website operate independently without an integrated direct-enquiry funnel turning followers into confirmed {enquiry_noun}.")

        # -------------------------------------------------------------
        # 5. Dynamic Quote Card (Tailored to Reputation vs Digital Balance)
        # -------------------------------------------------------------
        if has_rating and identity.rating >= 4.5 and (not has_website or scores.website_experience < 10):
            quote_text = f"'{identity.business_name}' commands exceptional customer trust ({rating_val}★ on Google), but lacks an owned digital funnel to capture inbound demand. Transforming that verified reputation into a frictionless mobile conversion pathway will turn existing local searchers into predictable {enquiry_noun}."
        elif has_website and not has_whatsapp:
            quote_text = f"'{identity.business_name}' has established strong market brand presence on {domain_label}. The highest-leverage opportunity is removing smartphone friction by deploying an instant 1-click WhatsApp conversion architecture for prospective {customer_noun}."
        elif not has_website:
            quote_text = f"'{identity.business_name}' has built solid commercial standing, but without an owned digital destination, interested prospects have no self-serve pathway outside business hours. A mobile-first conversion presence will immediately protect market share and capture after-hours {enquiry_noun}."
        else:
            quote_text = f"'{identity.business_name}' possesses strong digital assets across {domain_label} and verified channels. Streamlining the transition from initial discovery to instant WhatsApp inquiry will maximize customer acquisition and accelerate response times."

        # -------------------------------------------------------------
        # 6. Dynamic Customer Journey Steps (Page 2)
        # -------------------------------------------------------------
        if has_website:
            current_journey_steps = [
                {
                    "icon": "search",
                    "circle_class": "blue-circle",
                    "icon_color": "#2563EB",
                    "title": "Online Search / Discovery",
                    "desc": f"Discovers {identity.business_name} via search or social",
                    "is_alert": False
                },
                {
                    "icon": "globe",
                    "circle_class": "blue-circle",
                    "icon_color": "#2563EB",
                    "title": f"Visits {domain_label}",
                    "desc": f"Browses offerings & company background",
                    "is_alert": False
                },
                {
                    "icon": "phone",
                    "circle_class": "blue-circle",
                    "icon_color": "#2563EB",
                    "title": "Static Form or Voice Call",
                    "desc": "Manual contact form with delayed response",
                    "is_alert": False
                },
                {
                    "icon": "alert_triangle",
                    "circle_class": "red-circle",
                    "icon_color": "#DC2626",
                    "title": "Conversion Drop-off",
                    "desc": f"No instant 1-click messaging bridge to sales",
                    "is_alert": True
                }
            ]

            recommended_journey_steps = [
                {
                    "icon": "search",
                    "circle_class": "green-circle",
                    "icon_color": "#16A34A",
                    "title": "Online Search / Discovery",
                    "desc": f"High-intent prospect finds {identity.business_name}",
                    "is_success": False
                },
                {
                    "icon": "globe",
                    "circle_class": "green-circle",
                    "icon_color": "#16A34A",
                    "title": "High-Conversion Mobile Showcase",
                    "desc": f"Explores {service_noun} seamlessly on mobile",
                    "is_success": False
                },
                {
                    "icon": "whatsapp",
                    "circle_class": "green-circle",
                    "icon_color": "#16A34A",
                    "title": "1-Click WhatsApp Channel",
                    "desc": f"Pre-filled instant {enquiry_action_noun}",
                    "is_success": False
                },
                {
                    "icon": "check_circle",
                    "circle_class": "green-circle",
                    "icon_color": "#16A34A",
                    "title": confirmed_title,
                    "desc": f"Converted into confirmed commercial lead",
                    "is_success": True
                }
            ]
        else:
            current_journey_steps = [
                {
                    "icon": "search",
                    "circle_class": "blue-circle",
                    "icon_color": "#2563EB",
                    "title": "Google Search / Maps",
                    "desc": f"Discovers {entity_noun} on local listing",
                    "is_alert": False
                },
                {
                    "icon": "document",
                    "circle_class": "blue-circle",
                    "icon_color": "#2563EB",
                    "title": "View Profile Details",
                    "desc": f"Reads reviews & limited address details",
                    "is_alert": False
                },
                {
                    "icon": "phone",
                    "circle_class": "blue-circle",
                    "icon_color": "#2563EB",
                    "title": "Direct Phone Call Only",
                    "desc": "Calls during operating hours only",
                    "is_alert": False
                },
                {
                    "icon": "alert_triangle",
                    "circle_class": "red-circle",
                    "icon_color": "#DC2626",
                    "title": "Potential Drop-off",
                    "desc": f"No owned website or 24/7 online enquiry option",
                    "is_alert": True
                }
            ]

            recommended_journey_steps = [
                {
                    "icon": "search",
                    "circle_class": "green-circle",
                    "icon_color": "#16A34A",
                    "title": "Google Search / Maps",
                    "desc": f"Discovers {entity_noun}",
                    "is_success": False
                },
                {
                    "icon": "globe",
                    "circle_class": "green-circle",
                    "icon_color": "#16A34A",
                    "title": "Dedicated Mobile Showcase",
                    "desc": f"Owned portal presenting {service_noun}",
                    "is_success": False
                },
                {
                    "icon": "whatsapp",
                    "circle_class": "green-circle",
                    "icon_color": "#16A34A",
                    "title": "1-Click WhatsApp Bridge",
                    "desc": f"Instant {enquiry_action_noun}",
                    "is_success": False
                },
                {
                    "icon": "check_circle",
                    "circle_class": "green-circle",
                    "icon_color": "#16A34A",
                    "title": confirmed_title,
                    "desc": f"Converted into an active {customer_noun_single}",
                    "is_success": True
                }
            ]

        # Why it matters 3 cards
        rep_text = f"Your {rating_val}★ rating shows high trust—an immediate opportunity to convert more of this trust into {enquiry_noun}." if has_rating else f"Your verified local reputation provides a strong foundation to build direct {enquiry_noun}."

        why_matters = [
            {
                "icon": "users",
                "theme": "green",
                "title": "High Intent Visitors",
                "desc": f"People are already finding {entity_noun} and searching for your offerings."
            },
            {
                "icon": "star",
                "theme": "blue",
                "title": "Strong Reputation",
                "desc": rep_text
            },
            {
                "icon": "barchart",
                "theme": "purple",
                "title": "Untapped Potential",
                "desc": f"A structured digital journey can significantly increase your monthly {enquiry_noun}."
            }
        ]

        # Dimension scores with percentages
        dimensions = [
            {
                "num": "01",
                "name": "Discoverability",
                "icon": "search",
                "score": scores.discoverability,
                "max": 20,
                "pct": int(round((scores.discoverability / 20) * 100)),
                "color": "#16A34A" if scores.discoverability >= 15 else ("#F59E0B" if scores.discoverability >= 10 else "#EF4444")
            },
            {
                "num": "02",
                "name": "Brand & Identity",
                "icon": "tag",
                "score": scores.brand_identity,
                "max": 15,
                "pct": int(round((scores.brand_identity / 15) * 100)),
                "color": "#16A34A" if scores.brand_identity >= 12 else ("#F59E0B" if scores.brand_identity >= 8 else "#EF4444")
            },
            {
                "num": "03",
                "name": "Trust & Reputation",
                "icon": "shield",
                "score": scores.trust_reputation,
                "max": 20,
                "pct": int(round((scores.trust_reputation / 20) * 100)),
                "color": "#16A34A" if scores.trust_reputation >= 15 else ("#F59E0B" if scores.trust_reputation >= 10 else "#EF4444")
            },
            {
                "num": "04",
                "name": "Digital Experience",
                "icon": "laptop",
                "score": scores.website_experience,
                "max": 15,
                "pct": int(round((scores.website_experience / 15) * 100)),
                "color": "#16A34A" if scores.website_experience >= 11 else ("#F59E0B" if scores.website_experience >= 7 else "#EF4444")
            },
            {
                "num": "05",
                "name": "Lead Conversion",
                "icon": "conversion",
                "score": scores.lead_conversion,
                "max": 20,
                "pct": int(round((scores.lead_conversion / 20) * 100)),
                "color": "#16A34A" if scores.lead_conversion >= 14 else ("#F59E0B" if scores.lead_conversion >= 9 else "#EF4444")
            },
            {
                "num": "06",
                "name": "Social Presence",
                "icon": "users",
                "score": scores.social_presence,
                "max": 10,
                "pct": int(round((scores.social_presence / 10) * 100)),
                "color": "#3B82F6" if scores.social_presence >= 6 else ("#F59E0B" if scores.social_presence >= 4 else "#EF4444")
            }
        ]

        # Stroke offset for radial score gauge: circumference = 2 * pi * r (r=62 => C=389.55)
        r = 62
        c = 2 * 3.14159265 * r
        dash_offset = c - (scores.overall_score / 100.0) * c

        # Formatted report ID
        report_id_display = audit_id.replace("OH-AUDIT-", "OH-") if audit_id else "OH-2026-0911-001"
        if len(report_id_display) > 18:
            report_id_display = report_id_display[:18]

        return {
            "report_id": report_id_display,
            "date_str": datetime.now().strftime("%d %B %Y"),
            "business_name": identity.business_name,
            "category": identity.category or "Commercial & Local Enterprise",
            "tagline": tagline,
            "location": identity.address or (identity.city or "Local Area"),
            "rating_display": rating_display,
            "phone": identity.phone or "Not Available",
            "website": identity.website or "",
            "website_display": identity.website if has_website else "Not Verified",
            "maps_url": identity.google_maps_url or (identity.source_url if "maps" in (identity.source_url or "") else ""),
            "maps_display": "Google Maps Listing (Verified)" if (identity.google_maps_url or "maps" in (identity.source_url or "")) else "Not Verified",
            "instagram_url": identity.instagram_url or (identity.source_url if "instagram" in (identity.source_url or "") else ""),
            "instagram_display": "Instagram Profile (Verified)" if (identity.instagram_url or "instagram" in (identity.source_url or "")) else "Not Verified",
            "facebook_url": identity.facebook_url or (identity.source_url if "facebook" in (identity.source_url or "") else ""),
            "facebook_display": "Facebook Profile (Verified)" if (identity.facebook_url or "facebook" in (identity.source_url or "")) else "Not Verified",
            "whatsapp_display": "Chat on WhatsApp" if has_whatsapp else "Not Available",
            "email_display": identity.email or "Not Available",
            "overall_score": scores.overall_score,
            "dash_offset": round(dash_offset, 2),
            "circumference": round(c, 2),
            "tier": tier_info,
            "score_narrative": score_narrative,
            "business_model": model_info,
            "dimensions": dimensions,
            "working_bullets": working_bullets,
            "attention_bullets": attention_bullets,
            "quote_text": quote_text,
            "subheading_p2": subheading_p2,
            "opp_title": opp_title,
            "opp_desc": opp_desc,
            "why_matters": why_matters,
            "first_move": first_move,
            "first_move_desc": first_move_desc,
            "journey_rec_p3": f"Instant {enquiry_action_noun}",
            "journey_rec_p4": confirmed_title,
            "journey_rec_p4_desc": f"Converted into an active {customer_noun_single}",
            "current_journey_steps": current_journey_steps,
            "recommended_journey_steps": recommended_journey_steps,
            "additional_opps": [add_opp_1, add_opp_2, add_opp_3],
            "cta_text": cta_text,
            "onehive_phone": ONEHIVE_PHONE or "+91 98450 12345",
            "onehive_email": ONEHIVE_EMAIL or "hello@onehive.in",
            "onehive_website": ONEHIVE_WEBSITE or "www.onehive.in"
        }
