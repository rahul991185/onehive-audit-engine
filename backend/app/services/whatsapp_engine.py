from app.models.schemas import BusinessIdentity, Opportunity

class WhatsAppEngine:
    """
    Generates concise, consultative, human WhatsApp outreach copy.
    Strictly avoids referencing 'Page 3' or demanding report reading; goal is to spark curiosity and GET A RESPONSE.
    """

    @staticmethod
    def generate(identity: BusinessIdentity, opp: Opportunity) -> str:
        name = identity.business_name
        strength = f"{identity.rating}★ Google reputation ({identity.review_count} reviews)" if identity.rating and identity.review_count else "local profile presence"

        message = (
            f"Hi {name}, I came across your digital presence in {identity.city or 'your area'} and noticed one opportunity that stood out.\n\n"
            f"Your {strength} is already strong, but there is a clear gap between that visibility and the next step for an interested customer.\n\n"
            f"We created a short personalized Digital Presence Report for you, including a visual concept of how this could be improved.\n\n"
            f"Happy to share it with you if useful."
        )
        return message
