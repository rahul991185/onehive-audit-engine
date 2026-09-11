from pathlib import Path
from typing import Tuple
from app.config import QUICKWINS_DIR
from app.models.schemas import BusinessIdentity, Opportunity, QuickWin

class QuickWinEngine:
    """
    Generates a polished, human-readable Quick Win deliverable tailored to the #1 growth opportunity.
    Provides structured link, first-response greeting script, and placement guidance without ugly raw dump.
    """

    @staticmethod
    def generate(audit_id: str, identity: BusinessIdentity, opp: Opportunity) -> Tuple[QuickWin, Path]:
        name = identity.business_name
        category = identity.category or "Local Business"
        location = identity.city or "Local Area"
        phone = identity.phone or "+91 98450 12345"
        clean_phone = "".join(filter(str.isdigit, phone))
        if len(clean_phone) < 10:
            clean_phone = "919845012345"

        cat_lower = (category + " " + name).lower()
        if any(k in cat_lower for k in ["dent", "clinic", "doctor", "health"]):
            inquiry_topic = "a consultation"
            service_question = "Which specific treatment or consultation are you looking for?"
            confirm_phrase = "confirm your consultation appointment shortly"
        elif any(k in cat_lower for k in ["dairy", "milk", "food", "fmcg"]):
            inquiry_topic = "products and dealership / distribution options"
            service_question = "Are you inquiring for retail purchase or wholesale / dealership distribution?"
            confirm_phrase = "connect you with our sales and distribution team shortly"
        elif any(k in cat_lower for k in ["interior", "decor", "architect", "design"]):
            inquiry_topic = "an interior design consultation"
            service_question = "What type of project (residential, modular kitchen, commercial) are you planning?"
            confirm_phrase = "schedule your design consultation shortly"
        elif any(k in cat_lower for k in ["banquet", "venue", "lawn", "wedding"]):
            inquiry_topic = "venue date availability and packages"
            service_question = "What event date and estimated guest count are you planning for?"
            confirm_phrase = "check date availability and share our package brochure shortly"
        elif any(k in cat_lower for k in ["school", "academy", "education"]):
            inquiry_topic = "admissions and campus visit details"
            service_question = "Which grade/course are you seeking admissions for?"
            confirm_phrase = "connect you with our admissions counsellor shortly"
        elif any(k in cat_lower for k in ["salon", "spa", "beauty"]):
            inquiry_topic = "services and appointment availability"
            service_question = "Which hair, skin, or beauty services would you like to book?"
            confirm_phrase = "confirm your stylist appointment slot shortly"
        elif any(k in cat_lower for k in ["restaurant", "cafe", "dining"]):
            inquiry_topic = "table reservations"
            service_question = "For what date, time, and how many guests would you like to reserve a table?"
            confirm_phrase = "confirm your table reservation shortly"
        elif any(k in cat_lower for k in ["auto", "car", "repair"]):
            inquiry_topic = "vehicle service packages"
            service_question = "What is your vehicle make/model and required service or repair?"
            confirm_phrase = "confirm your workshop bay appointment shortly"
        else:
            inquiry_topic = "your services"
            service_question = "Which specific service or inquiry can we help you with?"
            confirm_phrase = "assist you with your inquiry shortly"

        # Pre-filled link
        prefilled_msg = f"Hi {name}, I found your listing online and would like to enquire about {inquiry_topic} in {location}."
        encoded_text = prefilled_msg.replace(" ", "%20")
        whatsapp_link = f"https://wa.me/{clean_phone}?text={encoded_text}"

        first_response_script = (
            f"Hello! Thank you for contacting {name}, {location}.\n\n"
            f"We have received your enquiry. To assist you promptly:\n"
            f"1. {service_question}\n"
            f"2. What date or time slot works best for you?\n\n"
            f"Our team will {confirm_phrase}. Thank you for reaching out to {name}!"
        )

        suggested_placement = [
            "Add as the primary Action Link on Google Business Profile ('Book Online' or 'Message Us').",
            "Configure as the automated Greeting Message in WhatsApp Business (Settings → Business Tools → Greeting Message).",
            "Place as the primary contact link in your Instagram bio or social profiles."
        ]

        title = "Instant WhatsApp Enquiry Routing & Triage Workflow"
        why_chosen = (
            f"Because high-intent prospects discovering {name} currently have no interactive digital bridge, "
            f"this ready-to-deploy routing setup converts mobile visitors into direct conversations in seconds."
        )

        asset = f"""============================================================
ONEHIVE QUICK WIN DELIVERABLE
INSTANT WHATSAPP ENQUIRY ROUTING SETUP
Prepared exclusively for: {name} ({location})
============================================================

1. DIRECT PRE-FILLED WHATSAPP ROUTING LINK:
{whatsapp_link}

2. FIRST-RESPONSE RECEPTION SCRIPT (WhatsApp Business):
------------------------------------------------------------
{first_response_script}
------------------------------------------------------------

3. SUGGESTED PLACEMENT GUIDANCE:
• {suggested_placement[0]}
• {suggested_placement[1]}
• {suggested_placement[2]}

============================================================
Delivered by OneHive Technologies • Build. Automate. Grow.
============================================================"""

        quick_win = QuickWin(
            title=title,
            category="Lead Conversion & Inbound Routing",
            why_chosen=why_chosen,
            ready_to_use_asset=asset,
            instructions="Add the routing link to your Google Business Profile and set up the automated first response in WhatsApp Business.",
            asset_format="text",
            whatsapp_link=whatsapp_link,
            first_response_script=first_response_script,
            suggested_placement=suggested_placement
        )

        out_path = QUICKWINS_DIR / f"{audit_id}_quick_win.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(asset)

        return quick_win, out_path
