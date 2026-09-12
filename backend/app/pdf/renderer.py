import base64
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional
from jinja2 import Environment, FileSystemLoader
from playwright.async_api import async_playwright
from app.config import TEMPLATES_DIR, ONEHIVE_LOGO_PATH, REPORTS_DIR, ONEHIVE_WEBSITE, ONEHIVE_EMAIL, ONEHIVE_PHONE, ONEHIVE_ADDRESS
from app.models.schemas import BusinessIdentity, AuditScore, Opportunity, Recommendation
from app.pdf.verifier import PDFVerifier

class PDFRenderer:
    """
    Chromium-powered fixed HTML/CSS PDF rendering engine.
    Embeds actual website concept teaser and verifies strict 5-page output.
    """

    @staticmethod
    def get_base64_image(file_path: Path) -> str:
        if file_path and file_path.exists():
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                mime = "image/png" if file_path.suffix == ".png" else "image/jpeg"
                return f"data:{mime};base64,{encoded}"
        return ""

    @staticmethod
    def get_vertical_details(identity: BusinessIdentity, scores: AuditScore) -> Tuple[List[dict], str, str, str]:
        name = identity.business_name
        cat_lower = ((identity.category or "") + " " + name).lower()
        
        if any(k in cat_lower for k in ["dent", "implant", "teeth", "ortho", "smile", "clinic"]):
            services = [
                {"icon_name": "tooth", "name": "Dental Consultations", "desc": "Oral diagnostic assessments"},
                {"icon_name": "shield", "name": "Preventive Care", "desc": "Routine cleanings and hygiene"},
                {"icon_name": "wrench", "name": "Restorative Dentistry", "desc": "Cavity care & restoration"},
                {"icon_name": "sparkles", "name": "Cosmetic Aesthetics", "desc": "Functional smile care"},
                {"icon_name": "clock", "name": "Emergency Relief", "desc": "Direct acute discomfort care"}
            ]
            positioning = "Established local clinical practice with visible patient trust and an opportunity to create a structured digital consultation bridge."
            first_move = "Mobile-First Clinical Destination + Direct WhatsApp Enquiry Routing"
            first_move_desc = "A dedicated digital presence to showcase clinic credibility, verified treatments, and direct consultation scheduling."
            
        elif any(k in cat_lower for k in ["interior", "decor", "design", "architect"]):
            services = [
                {"icon_name": "home", "name": "Residential Interiors", "desc": "Tailored living spaces & villas"},
                {"icon_name": "building", "name": "Commercial Interiors", "desc": "Modern workplaces & retail"},
                {"icon_name": "kitchen", "name": "Modular Kitchens", "desc": "Precision joinery & cabinetry"},
                {"icon_name": "renovation", "name": "Home Renovation", "desc": "Remodelling and upgrades"},
                {"icon_name": "turnkey", "name": "Turnkey Projects", "desc": "End-to-end project execution"}
            ]
            positioning = "Creative interior design studio with high-quality visual portfolio and an opportunity to convert attention into structured project enquiries."
            first_move = "Visual Portfolio Showcase + WhatsApp Consultation Routing"
            first_move_desc = "An editorial digital portfolio showcasing completed projects with direct WhatsApp design consultation booking."

        elif any(k in cat_lower for k in ["banquet", "venue", "lawn", "marriage", "wedding", "resort"]):
            services = [
                {"icon_name": "wedding", "name": "Weddings & Receptions", "desc": "Grand celebrations & staging"},
                {"icon_name": "briefcase", "name": "Corporate Conclaves", "desc": "Conferences & seminars"},
                {"icon_name": "celebration", "name": "Social Celebrations", "desc": "Anniversaries & parties"},
                {"icon_name": "catering", "name": "Gourmet Catering", "desc": "Curated multi-cuisine dining"},
                {"icon_name": "building", "name": "Lawn & Banquet Halls", "desc": "Flexible indoor & outdoor spaces"}
            ]
            positioning = "Premier hospitality venue with proven event hosting and an opportunity to capture high-intent dates through instant digital booking."
            first_move = "Virtual Venue Showcase + Instant WhatsApp Date Availability"
            first_move_desc = "An interactive venue exploration experience allowing event hosts to check availability and request package quotes instantly."

        elif any(k in cat_lower for k in ["school", "academy", "education", "vidya", "institute"]):
            services = [
                {"icon_name": "academic", "name": "Academic Curriculum", "desc": "Structured modern syllabus"},
                {"icon_name": "stem", "name": "STEM & Science Labs", "desc": "Experiential technology learning"},
                {"icon_name": "athletics", "name": "Sports & Athletics", "desc": "Physical education facilities"},
                {"icon_name": "art", "name": "Arts & Culture", "desc": "Creative arts development"},
                {"icon_name": "check", "name": "Admissions Guidance", "desc": "Enrollment and counselling"}
            ]
            positioning = "Respected educational institution with active community reputation and an opportunity to streamline admissions enquiries."
            first_move = "Interactive Admissions Experience + Campus Tour Booking"
            first_move_desc = "A modern parent-facing digital destination providing curriculum clarity, fee overviews, and direct admission counselling routing."

        else:
            services = [
                {"icon_name": "briefcase", "name": "Professional Services", "desc": "Core specialized service offerings"},
                {"icon_name": "users", "name": "Client Consultations", "desc": "One-on-one advisory sessions"},
                {"icon_name": "shield", "name": "Quality Assurance", "desc": "Structured service delivery"},
                {"icon_name": "zap", "name": "Direct Communication", "desc": "Accessible customer assistance"},
                {"icon_name": "map_pin", "name": "Local Service Delivery", "desc": f"Serving clients across {identity.city or 'the region'}"}
            ]
            positioning = "Established local business with visible customer trust and an opportunity to strengthen its digital enquiry journey."
            first_move = "Owned Digital Destination + Structured Enquiry System"
            first_move_desc = "A professional, mobile-first web presence connecting prospective clients directly with your team."

        return services, positioning, first_move, first_move_desc

    @staticmethod
    async def render(
        audit_id: str,
        identity: BusinessIdentity,
        scores: AuditScore,
        strongest_asset: str,
        biggest_gap: str,
        opp: Opportunity,
        recommendations: List[Recommendation],
        desktop_preview_path: Optional[Path] = None,
        mobile_preview_path: Optional[Path] = None
    ) -> Tuple[Path, bool, List[str]]:
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR / "report")))
        template = env.get_template("report.html")

        css_path = TEMPLATES_DIR / "report" / "report.css"
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()

        logo_base64 = PDFRenderer.get_base64_image(ONEHIVE_LOGO_PATH)

        config_data = {
            "ONEHIVE_WEBSITE": ONEHIVE_WEBSITE,
            "ONEHIVE_EMAIL": ONEHIVE_EMAIL,
            "ONEHIVE_PHONE": ONEHIVE_PHONE,
            "ONEHIVE_ADDRESS": ONEHIVE_ADDRESS
        }

        norm_scores = {
            "discoverability": int(round((scores.discoverability / 20) * 100)),
            "brand_identity": int(round((scores.brand_identity / 15) * 100)),
            "trust_reputation": int(round((scores.trust_reputation / 20) * 100)),
            "website_experience": int(round((scores.website_experience / 15) * 100)),
            "lead_conversion": int(round((scores.lead_conversion / 20) * 100)),
            "social_presence": int(round((scores.social_presence / 10) * 100)),
        }

        services, positioning_statement, first_move, first_move_desc = PDFRenderer.get_vertical_details(identity, scores)
        
        from app.services.report_v2_adapter import ReportV2Adapter
        page_data = ReportV2Adapter.build_page_data(
            audit_id=audit_id,
            identity=identity,
            scores=scores,
            strongest_asset=strongest_asset,
            biggest_gap=biggest_gap,
            opp=opp,
            recommendations=recommendations
        )

        rendered_html = template.render(
            p=page_data,
            identity=identity,
            scores=scores,
            norm_scores=norm_scores,
            strongest_asset=strongest_asset,
            biggest_gap=biggest_gap,
            opportunity=opp,
            recommendations=recommendations,
            services=services,
            positioning_statement=positioning_statement,
            first_move=first_move,
            first_move_desc=first_move_desc,
            css_content=css_content,
            logo_base64=logo_base64,
            date_str=datetime.now().strftime("%B %d, %Y"),
            config=config_data
        )

        safe_slug = "".join(c if c.isalnum() else "_" for c in identity.business_name.lower())[:30]
        output_pdf_path = REPORTS_DIR / f"{safe_slug}_digital_presence_report.pdf"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            context = await browser.new_context(
                viewport={"width": 794, "height": 1123},
                device_scale_factor=2
            )
            page = await context.new_page()
            await page.set_content(rendered_html, wait_until="networkidle")
            await page.emulate_media(media="print")

            await page.pdf(
                path=str(output_pdf_path),
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
            )
            await browser.close()

        # Run automated QA verifier
        is_valid, errors = PDFVerifier.verify(output_pdf_path, identity, scores)
        return output_pdf_path, is_valid, errors
