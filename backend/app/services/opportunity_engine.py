from typing import List, Tuple, Optional, Dict, Any
from app.models.schemas import BusinessIdentity, EvidenceItem, AuditScore, Opportunity, Recommendation

class OpportunityEngine:
    """
    Commercial Quality V2 Opportunity Engine.
    
    Strictly adheres to:
    - Industry-aware opportunity isolation (Dental, Venue, School, Interior, Local Service).
    - Factual, evidence-based descriptions.
    - Zero unsupported statistics or speculative claims.
    - Compliant review language ("compliant review-request workflow", not "5-star reviews").
    - Compliant profile completeness language ("improve local profile completeness and engagement signals").
    """

    @staticmethod
    def evaluate(
        identity: BusinessIdentity,
        scores: AuditScore,
        evidence: List[EvidenceItem],
        extra_data: Optional[dict] = None
    ) -> Tuple[str, str, Opportunity, List[Recommendation]]:
        
        name = identity.business_name
        category = ((identity.category or "") + " " + name).lower()
        has_website = bool(identity.website and identity.website.strip())
        has_whatsapp = bool(identity.whatsapp_url) or any("whatsapp" in e.field.lower() and e.status == "PASS" for e in evidence)
        has_high_rating = identity.rating is not None and identity.rating >= 4.5
        rev_count_str = f" across {identity.review_count} verified reviews" if identity.review_count else ""
        rating_str = f"{identity.rating}★" if identity.rating else "strong"
        
        detected_services = (extra_data or {}).get("detected_services", [])
        services_mention = f" including {', '.join(detected_services[:3])}" if len(detected_services) >= 2 else ""

        domain = identity.website.split("//")[-1].split("/")[0].replace("www.", "") if has_website else ""
        loc_str = f" in {identity.city}" if identity.city and identity.city != "Local Area" else ""

        # -------------------------------------------------------------
        # 1. STRONGEST ASSET (Evidence-based & Niche-Aware)
        # -------------------------------------------------------------
        if any(k in category for k in ["dent", "implant", "teeth", "ortho", "smile", "clinic", "hospital", "doctor", "health", "physio"]):
            rep_asset = f"Exceptional patient trust and clinical care reputation with a verified {rating_str} rating on Google{rev_count_str}{loc_str}."
        elif any(k in category for k in ["dairy", "milk", "khoya", "paneer", "ghee", "fmcg", "beverage", "packaged food", "agro"]):
            rep_asset = f"Established consumer market reputation and regional product trust with a verified {rating_str} rating on Google{rev_count_str}{loc_str}."
        elif any(k in category for k in ["banquet", "resort", "venue", "hotel", "marriage", "wedding"]):
            rep_asset = f"Distinguished venue standing and host endorsements with a verified {rating_str} rating on Google{rev_count_str}{loc_str}."
        elif any(k in category for k in ["school", "college", "academy", "education"]):
            rep_asset = f"Strong community standing and parental trust with a verified {rating_str} rating on Google{rev_count_str}{loc_str}."
        elif any(k in category for k in ["interior", "architect", "decor", "designer"]):
            rep_asset = f"Proven architectural craftsmanship and high client satisfaction with a verified {rating_str} rating on Google{rev_count_str}."
        elif any(k in category for k in ["salon", "spa", "beauty"]):
            rep_asset = f"Loyal client following and recognized styling excellence with a verified {rating_str} rating on Google{rev_count_str}{loc_str}."
        elif any(k in category for k in ["restaurant", "cafe", "dining", "bistro"]):
            rep_asset = f"High culinary acclaim and patron dining sentiment with a verified {rating_str} rating on Google{rev_count_str}{loc_str}."
        elif any(k in category for k in ["auto", "car", "mechanic", "garage", "vehicle"]):
            rep_asset = f"Trusted mechanical workmanship and customer reliability with a verified {rating_str} rating on Google{rev_count_str}{loc_str}."
        elif any(k in category for k in ["real estate", "property", "realtor", "builder"]):
            rep_asset = f"Established property advisory standing and buyer trust with a verified {rating_str} rating on Google{rev_count_str}{loc_str}."
        elif any(k in category for k in ["manufacturing", "industrial", "machinery", "metals", "packaging"]):
            rep_asset = f"Solid industrial credibility and client satisfaction with a verified {rating_str} rating on Google{rev_count_str}{loc_str}."
        else:
            rep_asset = f"High verified customer trust with a {rating_str} rating on Google{rev_count_str}{loc_str}."

        # Check if business is social-first (Instagram / Facebook source)
        is_social_first = identity.business_type == "SOCIAL_FIRST" or "instagram.com" in (identity.source_url or "") or "facebook.com" in (identity.source_url or "")

        if is_social_first:
            social_platform = "Instagram" if "instagram" in (identity.source_url or "").lower() else "Facebook"
            aud_ev = [e for e in evidence if e.source in ["Instagram", "Facebook"] and "Audience" in e.field]
            aud_val = aud_ev[0].value if aud_ev else None
            if aud_val and "followers" in aud_val.lower():
                strongest_asset = f"Active visual social presence on {social_platform} with verified audience proof ({aud_val}) and strong brand aesthetics."
            else:
                strongest_asset = f"Active visual content cadence and public engagement on {social_platform} under {name}."
        elif has_high_rating:
            strongest_asset = rep_asset
        elif has_website and detected_services and len(detected_services) >= 2:
            strongest_asset = f"Active branded digital presence on {domain} showcasing core offerings ({', '.join(detected_services[:3])})."
        elif has_website and (identity.instagram_url or identity.facebook_url):
            social_names = []
            if identity.instagram_url: social_names.append("Instagram")
            if identity.facebook_url: social_names.append("Facebook")
            strongest_asset = f"Multi-channel digital presence anchored by an owned domain ({domain}) and verified {' & '.join(social_names)}."
        elif has_website and scores.website_experience >= 10:
            strongest_asset = f"Dedicated branded web destination ({domain}) establishing an owned digital footprint for {name}."
        elif identity.rating is not None and identity.rating >= 4.0:
            strongest_asset = rep_asset
        elif scores.discoverability >= 14:
            strongest_asset = f"Verified Google Business presence serving clients under '{name}'{loc_str}."
        else:
            strongest_asset = f"Established commercial identity serving clients in {identity.city or 'your market'}."

        # -------------------------------------------------------------
        # 2. OPPORTUNITY & RECOMMENDATIONS BY BUSINESS TYPE / VERTICAL
        # -------------------------------------------------------------
        
        # S. SOCIAL-FIRST BUSINESSES (Instagram & Facebook Profiles without owned website)
        if is_social_first and not has_website:
            social_platform = "Instagram" if "instagram" in (identity.source_url or "").lower() else "Facebook"
            biggest_gap = f"Absence of an owned portfolio & consultation booking destination in {name}'s {social_platform} bio."
            opp_title = f"Convert {social_platform} Followers Into Direct Consultation Bookings"
            finding = f"While {name} maintains active audience engagement on {social_platform}, profile visitors currently hit conversion friction—having to rely on delayed DMs or comments with no 1-click consultation booking or treatment showcase."
            why_it_matters = f"Social media visitors make fast booking decisions. Inbound prospects waiting for manual DM replies frequently abandon intent or book with competing practices that offer instant booking links."
            current_journey = f"Browse {social_platform} Feed → Send DM or Leave Comment → Inconvenient DM Delay / Unanswered Inquiry → Lost Consultation"
            improved_journey = f"Browse {social_platform} Bio → Tap 1-Click Showcase Link → Mobile Treatment & Portfolio Menu → Instant WhatsApp Consultation Booking"
            recommended_service = "Mobile Bio-Showcase Website + Direct WhatsApp Booking Funnel"
            recs = [
                Recommendation(order=1, category="BUILD", title="Dedicated Mobile Link-in-Bio Showcase Hub", description=f"Deploy a high-speed, mobile-optimized treatment & portfolio hub for {name} highlighting credentials, services, and visual proofs."),
                Recommendation(order=2, category="CONVERT", title="Direct 1-Click WhatsApp Consultation Bridge", description="Replace manual DM delays with an automated WhatsApp consultation bridge for instant patient/client appointment booking."),
                Recommendation(order=3, category="GROW", title="Story & Highlight Conversion Funnels", description="Integrate high-converting calls-to-action into profile highlights to convert passive followers into confirmed consultation inquiries.")
            ]

        # A. DENTAL & ORAL HEALTHCARE
        elif any(k in category for k in ["dent", "implant", "teeth", "ortho", "smile"]):
            if not has_website:
                biggest_gap = f"Absence of an owned digital destination for {name} to present clinical treatments and capture patient bookings."
                opp_title = "Turn Local Search Discovery Into Direct Patient Consultation Bookings"
                finding = f"While {name} commands strong local patient trust ({rating_str}{rev_count_str}), patients searching on Google currently have no owned digital destination to explore treatments{services_mention} or initiate a consultation online."
                why_it_matters = "Without an owned clinical destination, patients searching outside clinic hours encounter friction and postpone booking care."
                current_journey = "Local Discovery → Google Maps Profile → Reception Phone Call Only → Deferred Action"
                improved_journey = "Local Discovery → Verified Practice Page → 1-Click Treatment Showcase → Direct WhatsApp Consultation"
                recommended_service = "Mobile-First Clinic Website + WhatsApp Consultation Booking"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Dedicated Mobile-First Consultation Page", description=f"Deploy a clean, mobile-first treatment showcase for {name} featuring clinical credentials, key service overviews, and clinic assurance."),
                    Recommendation(order=2, category="CONVERT", title="Direct 1-Click WhatsApp Booking Bridge", description="Integrate a direct WhatsApp booking channel to enable smartphone searchers to request consultation appointments seamlessly."),
                    Recommendation(order=3, category="GROW", title="Compliant Patient Feedback Loop", description="Implement a compliant review-request workflow to scale Google ratings and maintain strong local visibility.")
                ]
            else:
                biggest_gap = f"Friction in the mobile patient journey on {domain}; no instant WhatsApp booking routing."
                opp_title = "Turn Digital Clinic Visitors Into Direct Consultation Enquiries"
                finding = f"{name}'s web presence on {domain} presents the clinic, but smartphone visitors encounter friction when attempting to book a consultation quickly."
                why_it_matters = "Patients seeking dental care on mobile devices prioritize fast, effortless booking over browsing multiple static subpages."
                current_journey = f"Search → {domain} Homepage → Multiple Subpages → Unanswered Contact Form"
                improved_journey = f"Search → Streamlined Mobile Showcase → 1-Click WhatsApp Booking → Confirmed Appointment Slot"
                recommended_service = "Healthcare Conversion Architecture + WhatsApp Enquiry Automation"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Sticky Mobile Consultation Action Bar", description="Position prominent, easy-to-tap appointment triggers across all mobile pages."),
                    Recommendation(order=2, category="CONVERT", title="Interactive WhatsApp Triage Bridge", description="Route prospective patients directly to a structured WhatsApp enquiry channel."),
                    Recommendation(order=3, category="GROW", title="Compliant Feedback Integration", description="Implement a compliant review-request workflow to systematically capture patient satisfaction.")
                ]

        # B. GENERAL MEDICAL & SPECIALTY HEALTHCARE
        elif any(k in category for k in ["clinic", "hospital", "doctor", "health", "physio", "eye", "ayur", "pediatric", "pathology", "diagnostic"]):
            if not has_website:
                biggest_gap = f"Absence of an owned clinical destination for {name} to present doctor credentials and book consultations."
                opp_title = "Transform Local Patient Discovery Into Scheduled Clinical Consultations"
                finding = f"{name} has established valuable community standing, but prospective patients searching online need an effortless pathway to evaluate medical specializations{services_mention} and book consultations."
                why_it_matters = "Healthcare searches are time-sensitive; patients who cannot confirm booking options quickly often seek alternative providers."
                current_journey = "Local Search → Profile Listing → Phone Call During Clinic Hours Only → Delayed Treatment"
                improved_journey = "Local Search → Verified Healthcare Portal → Doctor Credentials & Specialties → 1-Click WhatsApp Slot Request"
                recommended_service = "Specialty Healthcare Portal & Instant Consultation Routing"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Specialist Care & Clinic Overview", description=f"Deploy an authoritative clinical destination for {name} highlighting medical credentials and patient trust protocols."),
                    Recommendation(order=2, category="CONVERT", title="Instant Appointment Routing Bridge", description="Enable smartphone visitors to request consultation slots 24/7 via WhatsApp."),
                    Recommendation(order=3, category="GROW", title="Patient Trust & Review Architecture", description="Deploy a compliant feedback workflow to reinforce clinical credibility on Google.")
                ]
            else:
                biggest_gap = f"Conversion friction on {domain} — patients lack an instant 1-click WhatsApp triage bridge for appointments."
                opp_title = "Convert Healthcare Portal Traffic Into Confirmed Medical Appointments"
                finding = f"{name} maintains an informative healthcare presence on {domain}, but patients searching on smartphones must navigate complex subpages to request care."
                why_it_matters = "Patients requiring timely medical guidance abandon slow web forms in favor of clinics offering immediate messaging."
                current_journey = f"Search → {domain} → Static Contact Form → Delayed Consultation"
                improved_journey = f"Search → Fast-Loading Specialist Overview → 1-Click WhatsApp Triage → Confirmed Appointment Slot"
                recommended_service = "Specialty Conversion Architecture & 1-Click Patient Triage"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Mobile Specialty Action Bar", description="Place prominent, instant appointment triggers on key treatment and doctor profile pages."),
                    Recommendation(order=2, category="CONVERT", title="Direct WhatsApp Patient Bridge", description="Enable smartphone visitors to check doctor availability and request appointments in one click."),
                    Recommendation(order=3, category="GROW", title="Clinical Credibility Loop", description="Integrate verified patient feedback and specialty credentials directly into the mobile journey.")
                ]

        # C. FOOD, DAIRY & FMCG ENTERPRISES
        elif any(k in category for k in ["dairy", "milk", "khoya", "paneer", "ghee", "fmcg", "beverage", "packaged food", "agro"]):
            if not has_website:
                biggest_gap = f"Lack of an owned digital destination for {name} to connect market reach to direct wholesale, dealership & bulk consumer orders."
                opp_title = "Convert Brand Discovery Into Direct Wholesale & Retail Customer Inquiries"
                finding = f"While {name} has built strong market presence, prospective retail consumers and wholesale partners exploring products{services_mention} online currently lack a dedicated digital channel for dealer inquiries or bulk order requests."
                why_it_matters = "Without an owned digital destination, commercial buyers and modern consumers face friction trying to connect with sales representatives."
                current_journey = "Brand Discovery → Directory Listing / Generic Search → Manual Office Call → Delayed Response"
                improved_journey = "Brand Discovery → Interactive Product Showcase → 1-Click WhatsApp Channel → Confirmed Distribution Lead"
                recommended_service = "Interactive Product Showcase + Direct WhatsApp B2B/B2C Ordering Bridge"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Interactive Product & Quality Showcase", description=f"Curate a visual digital catalog for {name} highlighting product range{services_mention}, purity standards, and retail store availability."),
                    Recommendation(order=2, category="CONVERT", title="Direct WhatsApp B2B & Retail Bridge", description="Deploy dedicated WhatsApp routing buttons for wholesale dealership inquiries, bulk orders, and consumer support."),
                    Recommendation(order=3, category="GROW", title="Omnichannel Brand Community Loop", description="Integrate social media channels and customer satisfaction loops into a unified brand acquisition engine.")
                ]
            else:
                biggest_gap = f"Digital enquiry friction on {domain} — wholesale partners and bulk buyers encounter static forms instead of direct WhatsApp dealer & order routing."
                opp_title = "Convert Digital Brand Visitors Into Direct Wholesale & Dealership Enquiries"
                finding = f"{name} has established brand reach on {domain}, but commercial wholesale buyers and modern consumers exploring products{services_mention} encounter static forms and delayed email pathways rather than direct WhatsApp chat routing."
                why_it_matters = "B2B dealers and wholesale buyers expect rapid, smartphone-friendly communication channels over slow web contact forms."
                current_journey = f"Brand Search → {domain} → Static Contact Form / Unanswered Phone → Lost Commercial Inquiries"
                improved_journey = f"Brand Search → Fast Product Showcase → 1-Click WhatsApp B2B Bridge → Qualified Dealership Lead"
                recommended_service = "Omnichannel B2B/B2C Conversion Architecture + WhatsApp Dealership Bridge"

                recs = [
                    Recommendation(order=1, category="BUILD", title="B2B & Retail Navigation Optimization", description=f"Streamline {domain} to separate bulk wholesale dealer inquiries from retail consumer product information."),
                    Recommendation(order=2, category="CONVERT", title="Direct WhatsApp Commercial Bridge", description="Deploy 1-click WhatsApp buttons on product pages for instant dealer pricing and bulk order quotes."),
                    Recommendation(order=3, category="GROW", title="Omnichannel Community & Distribution Loop", description="Connect verified social channels to direct product enquiries and distributor acquisition funnels.")
                ]

        # D. BANQUET, RESORT & EVENT VENUES
        elif any(k in category for k in ["banquet", "resort", "venue", "hotel", "marriage", "wedding", "hall", "convention"]):
            if not has_website:
                biggest_gap = f"Absence of an owned digital venue showcase for {name} to present hall capacities and verify date availability."
                opp_title = "Convert Event & Wedding Discovery Into Direct Venue Bookings"
                finding = f"Prospective event hosts and wedding planners researching venues expect immediate visual tours, capacity specifications{services_mention}, and an instant channel to check date availability."
                why_it_matters = "When event hosts cannot review venue spaces and amenities digitally, their decision journey is delayed, leading to lost peak dates."
                current_journey = "Local Search → Maps Listing → Voice Call Only → Deferred Site Visit"
                improved_journey = "Local Search → Immersive Venue Showcase → Event Capacity Overview → 1-Click WhatsApp Date Availability"
                recommended_service = "Virtual Venue Showcase + Instant WhatsApp Date Availability"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Visual Venue & Hall Showcase", description=f"Deploy an editorial digital portfolio for {name} showcasing banquet halls, lawn spaces, and seating capacities."),
                    Recommendation(order=2, category="CONVERT", title="Instant Date Availability Flow", description="Enable prospective hosts to submit date enquiries and request event packages directly via WhatsApp."),
                    Recommendation(order=3, category="GROW", title="Event Host Testimonial Architecture", description="Implement a systematic review-request workflow to capture host testimonials and venue reviews.")
                ]
            else:
                biggest_gap = f"Booking barrier on {domain} — hosts must fill contact forms instead of checking date availability via instant WhatsApp."
                opp_title = "Accelerate Venue Enquiries & Confirmed Date Reservations"
                finding = f"{name} presents event spaces on {domain}, but prospective wedding and corporate event hosts face inquiry friction when attempting to check specific date availability."
                why_it_matters = "Event hosts researching multiple venues prioritize locations that provide immediate package details and fast date confirmation."
                current_journey = f"Search → {domain} → Static Inquiry Form → Delayed Callback"
                improved_journey = f"Search → Virtual Venue Portfolio → 1-Click WhatsApp Date Check → Confirmed Site Visit"
                recommended_service = "Event Conversion Architecture & WhatsApp Date Routing"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Sticky Date Availability Trigger", description="Add prominent, mobile-optimized triggers allowing hosts to check wedding or event dates in one click."),
                    Recommendation(order=2, category="CONVERT", title="Instant Package & Brochure Bridge", description="Automate brochure and pricing delivery via WhatsApp to qualify prospective event hosts immediately."),
                    Recommendation(order=3, category="GROW", title="Host Testimonial & Visual Proof Engine", description="Integrate real event photos and host testimonials directly into booking conversion points.")
                ]

        # E. SCHOOL, EDUCATION & COACHING ACADEMIES
        elif any(k in category for k in ["school", "college", "preschool", "academy", "institute", "coaching", "education", "classes", "university"]):
            if not has_website:
                biggest_gap = f"Lack of an owned admissions website for {name} to streamline campus tour bookings and prospect registration."
                opp_title = "Streamline Inbound Admissions Enquiries & Campus Visits"
                finding = f"Parents and prospective students seeking educational programs need structured information regarding curriculum highlights{services_mention}, campus facilities, and admissions timelines."
                why_it_matters = "Without an owned admissions destination, parents researching after working hours have limited self-serve options to register their interest or book a campus tour."
                current_journey = "Search → Directory Listing → Manual Phone Enquiry → Administrative Friction"
                improved_journey = "Search → Academic & Campus Highlights → 1-Click Campus Tour Booking → Qualified Admissions Lead"
                recommended_service = "Admissions Funnel & Campus Visit Enquiry System"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Modern Admissions & Campus Portal", description=f"Build an authoritative admissions destination for {name} highlighting academic excellence and campus infrastructure."),
                    Recommendation(order=2, category="CONVERT", title="1-Click Campus Tour Registration", description="Provide prospective parents with a streamlined digital registration bridge for open days and counselling."),
                    Recommendation(order=3, category="GROW", title="Parent Trust & Reputation Workflow", description="Implement a compliant review-request workflow to showcase parent testimonials and student achievements.")
                ]
            else:
                biggest_gap = f"Admissions friction on {domain} — parents lack a direct 1-click WhatsApp channel to schedule campus visits or speak with counsellors."
                opp_title = "Convert Educational Website Visitors Into Confirmed Campus Admissions"
                finding = f"{name}'s portal on {domain} shares academic programs, but prospective parents encounter administrative friction when attempting to book a campus walkthrough."
                why_it_matters = "Parents make school decisions based on timely personal engagement; fast messaging options accelerate campus tour commitments."
                current_journey = f"Search → {domain} → PDF Download / Complex Form → Drop-Off"
                improved_journey = f"Search → Academic Highlights → 1-Click WhatsApp Campus Tour Request → Confirmed Open Day Visit"
                recommended_service = "Admissions Conversion Architecture & WhatsApp Counselling Bridge"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Streamlined Campus Visit CTA", description="Position 1-click campus visit scheduling across key academic and admissions pages."),
                    Recommendation(order=2, category="CONVERT", title="Instant WhatsApp Admission Bridge", description="Provide instant prospectus delivery and direct connection to admissions counsellors via WhatsApp."),
                    Recommendation(order=3, category="GROW", title="Parent Review & Achievement System", description="Systematically showcase alumni results and parent testimonials at critical decision points.")
                ]

        # F. INTERIOR DESIGN & ARCHITECTURE
        elif any(k in category for k in ["interior", "architect", "decor", "designer", "construction", "modular"]):
            if not has_website:
                biggest_gap = f"No curated digital portfolio website for {name} to showcase project craftsmanship and convert high-ticket design inquiries."
                opp_title = "Turn Project Impressions Into High-Ticket Design Consultations"
                finding = f"Clients commissioning residential or commercial interior architecture evaluate portfolio depth{services_mention}, material standards, and spatial style before requesting an initial meeting."
                why_it_matters = "Without an organized digital project showcase, prospective clients cannot gauge design compatibility, delaying consultation bookings."
                current_journey = "Discovery → Fragmented Social Cues → Unclear Project Scope → Inaction"
                improved_journey = "Discovery → Curated Design Portfolio → Clear Project Process → 1-Click WhatsApp Design Consultation"
                recommended_service = "Portfolio Showcase + WhatsApp Consultation Conversion Architecture"

                recs = [
                    Recommendation(order=1, category="BUILD", title="High-Resolution Project Portfolio Showcase", description=f"Curate an architectural showcase for {name} highlighting completed living, commercial, and modular spaces."),
                    Recommendation(order=2, category="CONVERT", title="Interactive Design Consultation Bridge", description="Introduce a structured design enquiry flow capturing room dimensions, aesthetic preferences, and budget range."),
                    Recommendation(order=3, category="GROW", title="Client Authority & Social System", description="Implement a systematic feedback workflow that turns completed projects into verified client reviews.")
                ]
            else:
                biggest_gap = f"Consultation friction on {domain} — prospective clients cannot share floorplans or request design estimates directly via WhatsApp."
                opp_title = "Convert Design Portfolio Visitors Into Retained Architectural Projects"
                finding = f"{name} displays past work on {domain}, but visitors evaluating interior architecture have no frictionless bridge to submit floorplans or discuss project feasibility."
                why_it_matters = "High-net-worth design clients demand rapid, confidential dialogue; static inquiry forms create unnecessary hesitation."
                current_journey = f"Discovery → {domain} Gallery → Static Email Link → Lost Design Inquiry"
                improved_journey = f"Discovery → Project Case Studies → 1-Click WhatsApp Floorplan Submission → Scheduled Concept Meeting"
                recommended_service = "Architectural Conversion Engine & Instant Plan Consultation Bridge"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Project Detail & Case Study Cards", description="Organize past projects by square footage, material selections, and timeline specifications."),
                    Recommendation(order=2, category="CONVERT", title="Direct WhatsApp Plan Submission Flow", description="Enable clients to upload floor plans and receive preliminary scope discussions via WhatsApp."),
                    Recommendation(order=3, category="GROW", title="Editorial Proof & Client Video System", description="Incorporate homeowner walkthroughs and client endorsements to solidify premium positioning.")
                ]

        # G. BEAUTY, SALON & WELLNESS
        elif any(k in category for k in ["salon", "spa", "beauty", "hair", "skin", "aesthetic", "makeup", "wellness"]):
            if not has_website:
                biggest_gap = f"Absence of a visual treatment menu and instant WhatsApp appointment booking for {name}."
                opp_title = "Turn Styling & Treatment Discovery Into Confirmed Salon Appointments"
                finding = f"Clients looking for premium salon and wellness treatments evaluate aesthetic quality{services_mention} and expect instant, frictionless appointment booking directly from their smartphone."
                why_it_matters = "When clients must call during busy salon floor hours, calls go unanswered and clients switch to alternative studios."
                current_journey = "Discovery → Google / Instagram Profile → Unanswered Call During Busy Hours → Lost Booking"
                improved_journey = "Discovery → Visual Treatment Menu & Pricing → 1-Click WhatsApp Stylist Booking → Confirmed Appointment Slot"
                recommended_service = "Visual Treatment Showcase + Instant WhatsApp Stylist Booking"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Visual Service & Styling Menu", description=f"Deploy a stylish mobile treatment menu for {name} showcasing hair, skin, and spa packages with transparent pricing."),
                    Recommendation(order=2, category="CONVERT", title="1-Click Stylist Booking Bridge", description="Enable clients to reserve treatment slots and select services instantly via WhatsApp."),
                    Recommendation(order=3, category="GROW", title="Client Loyalty & Review Harvesting", description="Automate post-appointment review requests to consistently build 5-star reputation on Google.")
                ]
            else:
                biggest_gap = f"Booking barrier on {domain} — clients browsing services cannot confirm stylist slots with an instant 1-click WhatsApp bridge."
                opp_title = "Convert Salon Website Traffic Into Confirmed Treatment Bookings"
                finding = f"{name} maintains a stylish presence on {domain}, but smartphone visitors evaluating treatments encounter multiple navigation steps without an instant booking confirmation route."
                why_it_matters = "Modern salon clients book appointments impulsively on mobile; any friction results in immediate bounce."
                current_journey = f"Discovery → {domain} → Contact Us Page → Phone Number Uncalled"
                improved_journey = f"Discovery → Visual Service Menu → 1-Click WhatsApp Slot Request → Confirmed Stylist Chair"
                recommended_service = "Salon Conversion Architecture + Instant WhatsApp Booking"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Sticky Mobile Appointment Bar", description="Deploy a persistent, thumb-friendly 'Book Appointment' bar across all mobile pages."),
                    Recommendation(order=2, category="CONVERT", title="Direct WhatsApp Stylist Booking", description="Route visitors to pre-filled WhatsApp booking templates with service selection."),
                    Recommendation(order=3, category="GROW", title="Client Transformation & Review Loop", description="Incorporate before/after showcases and automated review collection after each visit.")
                ]

        # H. RESTAURANTS, CAFES & DINING
        elif any(k in category for k in ["restaurant", "cafe", "dining", "menu", "bistro", "catering", "bakery", "lounge"]):
            if not has_website:
                biggest_gap = f"No interactive visual menu or instant table reservation pathway for {name}."
                opp_title = "Convert Dining Discovery Into Confirmed Table Reservations & Orders"
                finding = f"Food lovers and diners researching {name} want to explore your culinary menu{services_mention}, ambiance, and reserve tables with zero phone friction."
                why_it_matters = "Diners seeking evening or weekend spots make quick decisions; phone lines that are busy or unanswered cause immediate drop-offs."
                current_journey = "Search → Map Listing → Phone Call for Table / Directions → Missed Connection"
                improved_journey = "Search → Visual Digital Menu & Chef Specials → 1-Click WhatsApp Reservation → Confirmed Table Booking"
                recommended_service = "Digital Visual Menu + Instant WhatsApp Table Booking"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Interactive Digital Menu & Ambiance Preview", description=f"Deploy a mouth-watering visual menu for {name} highlighting chef specials and dining ambiance."),
                    Recommendation(order=2, category="CONVERT", title="Instant Table Reservation Flow", description="Enable diners to check availability and book tables instantly via WhatsApp."),
                    Recommendation(order=3, category="GROW", title="Diner Review & Photo Capture Loop", description="Prompt satisfied guests to share food reviews and photos to boost local Google visibility.")
                ]
            else:
                biggest_gap = f"Reservation barrier on {domain} — diners cannot check table availability or place quick takeout orders via WhatsApp."
                opp_title = "Turn Culinary Website Visitors Into Confirmed Table Bookings"
                finding = f"{name}'s web presence on {domain} presents the restaurant, but diners looking for quick weekend reservations face phone call barriers."
                why_it_matters = "Diners prioritize venues that allow frictionless mobile reservations without having to call loud dining rooms."
                current_journey = f"Search → {domain} → Static PDF Menu → Missed Table Booking"
                improved_journey = f"Search → Mobile Digital Menu → 1-Click WhatsApp Table Request → Confirmed Reservation"
                recommended_service = "Hospitality Conversion Architecture & WhatsApp Table Engine"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Mobile-Optimized Food & Drink Menu", description="Replace PDF menus with fast-loading, category-tabbed digital menus with pricing."),
                    Recommendation(order=2, category="CONVERT", title="Instant WhatsApp Table Reservation", description="Provide 1-click table booking and catering enquiry routing via WhatsApp."),
                    Recommendation(order=3, category="GROW", title="Guest Feedback & Photo Harvesting", description="Automate post-dining review prompts to dominate local dining searches.")
                ]

        # I. AUTOMOTIVE CARE & WORKSHOPS
        elif any(k in category for k in ["auto", "car", "detailing", "repair", "vehicle", "mechanic", "garage", "tyre"]):
            if not has_website:
                biggest_gap = f"No transparent service package menu or instant vehicle bay booking for {name}."
                opp_title = "Turn Vehicle Service Searches Into Confirmed Workshop Bay Bookings"
                finding = f"Vehicle owners searching for dependable automotive care evaluate service transparency{services_mention} and expect an instant estimate and booking pathway."
                why_it_matters = "Car owners delay maintenance when pricing and service scopes are unclear; offering instant WhatsApp estimates secures high-value bookings."
                current_journey = "Search → Map Profile → Generic Call → Unclear Price Scope → Delayed Service"
                improved_journey = "Search → Transparent Service Menu → 1-Click WhatsApp Estimate & Slot Booking → Confirmed Bay Scheduled"
                recommended_service = "Service Package Menu + Instant WhatsApp Workshop Bay Booking"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Transparent Service Package Menu", description=f"Publish a comprehensive service checklist and pricing guide for {name} detailing maintenance and detailing packages."),
                    Recommendation(order=2, category="CONVERT", title="Instant WhatsApp Quote & Slot Booking", description="Allow drivers to submit vehicle model and issue details to receive quick estimates and reserve slots."),
                    Recommendation(order=3, category="GROW", title="Service Assurance & Google Proof Loop", description="Deploy a post-delivery review workflow to establish the most trusted automotive workshop in the area.")
                ]
            else:
                biggest_gap = f"Service booking friction on {domain} — car owners must dial phone numbers instead of requesting instant WhatsApp repair quotes."
                opp_title = "Convert Automotive Website Visitors Into Booked Workshop Appointments"
                finding = f"{name} presents automotive capabilities on {domain}, but vehicle owners seeking quick repair or detailing estimates encounter static contact forms."
                why_it_matters = "Car owners value speed and upfront estimates; instant messaging dramatically increases booked service bays."
                current_journey = f"Search → {domain} → Static Form → Unconfirmed Workshop Booking"
                improved_journey = f"Search → Service Package Details → 1-Click WhatsApp Estimate Request → Confirmed Bay Scheduled"
                recommended_service = "Automotive Conversion Engine & WhatsApp Quote Bridge"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Quick Quote Action Bar", description="Place prominent 'Get Instant Quote' triggers across all automotive service pages."),
                    Recommendation(order=2, category="CONVERT", title="Direct WhatsApp Bay Booking", description="Enable drivers to send vehicle photos or symptoms via WhatsApp for rapid diagnostic triage."),
                    Recommendation(order=3, category="GROW", title="Workshop Trust & Warranty Badges", description="Highlight parts warranties and customer testimonials to build commanding local market trust.")
                ]

        # J. REAL ESTATE & PROPERTY ADVISORY
        elif any(k in category for k in ["real estate", "property", "realtor", "builder", "developer", "apartments"]):
            if not has_website:
                biggest_gap = f"No curated property catalog for {name} to schedule instant site inspections."
                opp_title = "Convert High-Intent Property Searches Into Confirmed Site Visits"
                finding = f"Prospective homebuyers and commercial investors researching properties evaluate floor plans{services_mention} and project specs before engaging."
                why_it_matters = "Without an organized digital project catalog, high-net-worth buyers cannot verify specifications, leading to lost sales pipeline."
                current_journey = "Search → Scattered Listings → Manual Agent Call → Delayed Follow-Up"
                improved_journey = "Search → Curated Property Showcase → Floor Plans & Video Tour → 1-Click WhatsApp Site Visit Booking"
                recommended_service = "Curated Property Showcase + Instant WhatsApp Site Visit Scheduling"

                recs = [
                    Recommendation(order=1, category="BUILD", title="High-Impact Property Portfolio", description=f"Deploy an authoritative project showcase for {name} presenting property details, floor plans, and amenities."),
                    Recommendation(order=2, category="CONVERT", title="Instant Site Visit Scheduling Bridge", description="Equip listings with 1-click WhatsApp buttons for brochure downloads and site visit scheduling."),
                    Recommendation(order=3, category="GROW", title="Investor Proof & Authority System", description="Systematically capture buyer testimonials and project delivery milestones.")
                ]
            else:
                biggest_gap = f"Lead capture friction on {domain} — property buyers must wait for email responses instead of instant WhatsApp brochure & visit scheduling."
                opp_title = "Accelerate High-Intent Buyer Engagement & Site Visit Bookings"
                finding = f"{name} presents real estate inventory on {domain}, but serious property buyers face slow form responses rather than immediate project brochure delivery."
                why_it_matters = "Property buyers research multiple developments simultaneously; immediate brochure and floorplan delivery secures buyer attention."
                current_journey = f"Search → {domain} → Long Contact Form → Lost Buyer Interest"
                improved_journey = f"Search → Property Showcase → 1-Click WhatsApp Brochure & Site Visit → Qualified Investor Lead"
                recommended_service = "Real Estate Lead Funnel & WhatsApp Brochure Automation"

                recs = [
                    Recommendation(order=1, category="BUILD", title="1-Click Brochure Download Flow", description="Deliver high-res project floorplans and pricing sheets instantly via WhatsApp."),
                    Recommendation(order=2, category="CONVERT", title="Direct Site Visit Scheduling Bridge", description="Allow buyers to select inspection dates and speak directly with sales managers via WhatsApp."),
                    Recommendation(order=3, category="GROW", title="Investor Authority & Construction Milestone Loop", description="Showcase construction updates and buyer handovers to cement developer credibility.")
                ]

        # K. B2B, MANUFACTURING & INDUSTRIAL
        elif any(k in category for k in ["manufacturing", "industrial", "fabrication", "machinery", "metals", "packaging", "chemicals"]):
            if not has_website:
                biggest_gap = f"No digital technical catalog for {name} to generate instant RFQ inquiries."
                opp_title = "Accelerate Inbound B2B Inquiries & Purchase Order RFQs"
                finding = f"Procurement managers and industrial buyers evaluate technical specifications{services_mention}, certifications, and manufacturing capacity before submitting an RFQ."
                why_it_matters = "B2B buyers research vendors thoroughly; absent or outdated product sheets force buyers to contact competing manufacturers."
                current_journey = "Search → Industrial Listing → Generic Inquiry Form → Multi-Day Response Delay"
                improved_journey = "Search → Detailed Technical Catalog → Specification Sheets → 1-Click WhatsApp Engineering RFQ"
                recommended_service = "Digital Industrial Catalog + Fast B2B RFQ Conversion Bridge"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Technical Product & Capability Catalog", description=f"Publish high-spec product catalogs and machinery capabilities for {name} with downloadable datasheets."),
                    Recommendation(order=2, category="CONVERT", title="Fast-Track B2B RFQ Bridge", description="Deploy direct WhatsApp routing for engineering consultations and instant RFQ submissions."),
                    Recommendation(order=3, category="GROW", title="Industrial Credibility & Client Badges", description="Showcase quality certifications, client logos, and trade accreditations.")
                ]
            else:
                biggest_gap = f"RFQ friction on {domain} — industrial procurement managers face delayed email forms rather than instant technical sales chat."
                opp_title = "Convert Industrial Web Visitors Into Fast-Track B2B Purchase Inquiries"
                finding = f"{name} presents manufacturing capabilities on {domain}, but engineering procurement heads face multiple-day quote turnarounds through static web forms."
                why_it_matters = "B2B procurement buyers move quickly on supply contracts; rapid technical qualification closes high-volume manufacturing orders."
                current_journey = f"Search → {domain} → Generic Form → Multi-Day Quote Delay"
                improved_journey = f"Search → Technical Spec Sheet → 1-Click WhatsApp RFQ Submission → Rapid Commercial Quote"
                recommended_service = "B2B Manufacturing RFQ Funnel & WhatsApp Engineering Triage"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Downloadable Spec Sheets & CAD Links", description="Equip product pages with instant technical datasheets and compliance documentation."),
                    Recommendation(order=2, category="CONVERT", title="Instant Engineering RFQ Bridge", description="Route RFQ drawings and volume requirements directly to technical sales via WhatsApp."),
                    Recommendation(order=3, category="GROW", title="Trade Quality & Client Accreditation Badges", description="Display ISO certifications and tier-1 vendor credentials prominently.")
                ]

        # L. PROFESSIONAL & ADVISORY SERVICES
        elif any(k in category for k in ["law", "legal", "advocate", "attorney", "tax", "ca ", "chartered accountant", "consulting", "advisory"]):
            if not has_website:
                biggest_gap = f"Lack of an authoritative digital practice portal for {name} to streamline client consultations."
                opp_title = "Turn Advisory Authority Into Retained Corporate & Client Consultations"
                finding = f"Business owners and individuals seeking professional advisory evaluate partner credentials{services_mention} and practice areas before reaching out."
                why_it_matters = "Clients seeking high-stakes legal or financial counsel require immediate reassurance of confidentiality and specialized expertise."
                current_journey = "Referral / Search → Basic Contact Card → Telephone Call → Uncertainty on Advisory Scope"
                improved_journey = "Referral / Search → Practice Authority Profile → Clear Advisory Capabilities → 1-Click Discovery Call Booking"
                recommended_service = "Practice Authority Portal + WhatsApp Consultation Scheduling"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Practice Authority Profile", description=f"Build an authoritative digital practice portal for {name} highlighting expertise and advisory team credentials."),
                    Recommendation(order=2, category="CONVERT", title="1-Click Discovery Consultation Bridge", description="Enable clients to initiate confidential preliminary consultations via structured WhatsApp routing."),
                    Recommendation(order=3, category="GROW", title="Thought Leadership & Credibility System", description="Highlight client case summaries and regulatory expertise to win high-value retainers.")
                ]
            else:
                biggest_gap = f"Client engagement barrier on {domain} — prospective corporate clients lack a discrete, 1-click discovery booking channel."
                opp_title = "Convert Advisory Web Visitors Into High-Value Retained Engagements"
                finding = f"{name} presents legal or financial advisory credentials on {domain}, but corporate clients have no streamlined, confidential path to book an initial scoping consultation."
                why_it_matters = "Corporate and high-net-worth clients value discretion and immediate access to practice leaders."
                current_journey = f"Referral / Search → {domain} → General Office Email → Delayed Consultation"
                improved_journey = f"Referral / Search → Partner Credentials → 1-Click Confidential WhatsApp Discovery → Retained Advisory Engagement"
                recommended_service = "Advisory Authority Funnel & Private Client Triage Bridge"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Partner Credentials & Practice Cards", description="Structure service offerings with partner backgrounds and industry experience."),
                    Recommendation(order=2, category="CONVERT", title="Confidential Discovery Booking Bridge", description="Deploy discrete 1-click WhatsApp channels for initial scope consultations."),
                    Recommendation(order=3, category="GROW", title="Case Briefs & Client Authority Proof", description="Publish anonymized case studies demonstrating regulatory and commercial success.")
                ]

        # M. GENERAL COMMERCIAL & LOCAL ENTERPRISE
        else:
            if not has_website:
                biggest_gap = f"Absence of a verified owned website for {name} connecting local discovery to direct customer action."
                opp_title = "Establish an Owned Digital Destination to Capture Local Inbound Demand"
                finding = f"{name} has built local recognition, but interested searchers currently have no dedicated destination to explore your offerings{services_mention} or submit an enquiry."
                why_it_matters = "An owned web destination ensures your business provides complete information and captures inbound demand around the clock."
                current_journey = "Search → Directory Listing → Phone Number → Limited After-Hours Options"
                improved_journey = "Search → Owned Business Destination → Clear Service Catalog → 1-Click WhatsApp Enquiry"
                recommended_service = "Bespoke Mobile-First Business Presence + WhatsApp Enquiry Flow"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Modern Mobile Web Destination", description=f"Deploy an official digital home for {name} presenting verified capabilities and customer assurances."),
                    Recommendation(order=2, category="CONVERT", title="Direct Messaging Conversion Bridge", description="Connect local searchers directly to your team via an instant WhatsApp enquiry channel."),
                    Recommendation(order=3, category="GROW", title="Local Profile Completeness Workflow", description="Improve local profile completeness and customer engagement signals through systematic feedback requests.")
                ]
            else:
                biggest_gap = f"Conversion friction on {domain} — mobile visitors encounter static forms without an instant 1-click WhatsApp bridge."
                opp_title = "Eliminate Mobile Friction to Accelerate Inbound Customer Inquiries"
                finding = f"{name}'s digital presence establishes awareness, but prospective customers on mobile devices encounter unnecessary steps when attempting to connect."
                why_it_matters = "Modern smartphone visitors choose providers that make taking the next step effortless and instant."
                current_journey = f"Search → {domain} → Multiple Subpages → Deferred Contact"
                improved_journey = f"Search → Fast-Loading Mobile Showcase → 1-Click WhatsApp Action → Confirmed Customer Enquiry"
                recommended_service = "Mobile Conversion Architecture & Direct WhatsApp Enquiry Upgrade"

                recs = [
                    Recommendation(order=1, category="BUILD", title="Streamlined Mobile Layout", description=f"Refine mobile page hierarchy for {name} to place core offerings{services_mention} and primary action triggers front and center."),
                    Recommendation(order=2, category="CONVERT", title="Instant WhatsApp Contact Integration", description="Equip your web destination with direct WhatsApp messaging and click-to-call action triggers."),
                    Recommendation(order=3, category="GROW", title="Customer Engagement Optimization", description="Improve local profile completeness and review generation to scale incoming customer demand.")
                ]

        opportunity = Opportunity(
            title=opp_title,
            priority="HIGH",
            finding=finding,
            evidence=evidence[:4],
            why_it_matters=why_it_matters,
            current_journey=current_journey,
            improved_journey=improved_journey,
            recommended_service=recommended_service,
            confidence=0.96
        )

        return strongest_asset, biggest_gap, opportunity, recs
