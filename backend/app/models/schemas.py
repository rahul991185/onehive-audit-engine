from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SourceType(str, Enum):
    GOOGLE_MAPS = "GOOGLE_MAPS"
    WEBSITE = "WEBSITE"
    INSTAGRAM = "INSTAGRAM"
    FACEBOOK = "FACEBOOK"
    UNKNOWN = "UNKNOWN"

class BusinessIdentity(BaseModel):
    business_name: str
    category: str
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    source_url: str
    resolved_url: Optional[str] = None
    place_id: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    identity_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    verified: bool = True
    is_demo: bool = False
    photos: List[str] = []
    business_type: str = "LOCAL_FIRST"
    google_maps_url: Optional[str] = None
    instagram_url: Optional[str] = None
    facebook_url: Optional[str] = None
    whatsapp_url: Optional[str] = None
    email: Optional[str] = None
    tagline: Optional[str] = None

class EvidenceItem(BaseModel):
    source: str
    field: str
    value: str
    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    observation: Optional[str] = None
    status: str = "PASS"  # PASS | PARTIAL | FAIL | UNKNOWN

class AuditScore(BaseModel):
    overall_score: int = Field(..., ge=0, le=100)
    discoverability: int = Field(..., ge=0, le=20)
    brand_identity: int = Field(..., ge=0, le=15)          # Brand & Positioning
    trust_reputation: int = Field(..., ge=0, le=20)        # Trust & Reputation
    website_experience: int = Field(..., ge=0, le=15)      # Digital Experience
    lead_conversion: int = Field(..., ge=0, le=20)         # Lead Conversion
    social_presence: int = Field(..., ge=0, le=10)         # Social Presence
    
    # V2 Commercial Reset Enhancements
    brand_positioning: Optional[int] = None
    digital_experience: Optional[int] = None
    maturity_band: str = "SIGNIFICANT OPPORTUNITY"
    business_type: str = "LOCAL_FIRST"
    commercial_tier: str = "FOUNDATION"
    dimension_explanations: Dict[str, str] = {}

    def model_post_init(self, __context: Any) -> None:
        if self.brand_positioning is None:
            self.brand_positioning = self.brand_identity
        if self.digital_experience is None:
            self.digital_experience = self.website_experience

class Opportunity(BaseModel):
    title: str
    priority: str = "HIGH"
    finding: str
    evidence: List[EvidenceItem] = []
    why_it_matters: str
    current_journey: str
    improved_journey: str
    recommended_service: str
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)

class Recommendation(BaseModel):
    order: int
    category: str  # BUILD | CONVERT | GROW
    title: str
    description: str

class WebsiteConcept(BaseModel):
    business_name: str
    industry: str
    location: str
    headline: str
    subheadline: str
    primary_cta: str
    secondary_cta: str
    services: List[Dict[str, str]]
    trust_signals: List[str]
    brand_colors: Dict[str, str] = {
        "primary": "#FFC400",
        "dark": "#101828",
        "background": "#F8F9FA",
        "text": "#1D2939"
    }
    whatsapp_cta: str
    final_cta: str
    sections: List[Dict[str, Any]] = []
    hero_image_url: Optional[str] = None
    gallery_images: List[str] = []
    preview_quality_score: int = 90

class QuickWin(BaseModel):
    title: str
    category: str
    why_chosen: str
    ready_to_use_asset: str
    instructions: str
    asset_format: str = "text"
    whatsapp_link: Optional[str] = None
    first_response_script: Optional[str] = None
    suggested_placement: List[str] = []

class SalesBrief(BaseModel):
    business_name: str
    industry: str
    location: str
    website: Optional[str] = None
    identity_confidence: str
    overall_score: int
    scores: AuditScore
    strongest_asset: str
    biggest_gap: str
    top_opportunity: str
    why_it_matters: str
    evidence_highlights: List[str]
    recommended_service: str
    likely_buying_trigger: str
    sales_angle: str
    opening_message: str
    objection_to_expect: str
    objection_response: str
    recommended_next_step: str
    business_type: str = "LOCAL_FIRST"
    commercial_tier: str = "FOUNDATION"
    what_not_to_say: List[Dict[str, str]] = []

class AuditRequest(BaseModel):
    url: str
    is_demo: bool = False

class AuditResponse(BaseModel):
    audit_id: str
    created_at: str
    business: BusinessIdentity
    overall_score: int
    scores: AuditScore
    strongest_asset: str
    biggest_gap: str
    attention_callout: str = "We've identified one area we believe deserves immediate attention."
    top_opportunity: Opportunity
    recommendations: List[Recommendation]
    website_concept: WebsiteConcept
    quick_win: QuickWin
    whatsapp_message: str
    sales_brief: SalesBrief
    report_pdf_url: str
    report_download_url: str
    report_page_1_url: Optional[str] = None
    report_page_2_url: Optional[str] = None
    image_pack_zip_url: Optional[str] = None
    desktop_preview_url: str
    mobile_preview_url: str
    quick_win_url: str
    sales_pack_zip_url: str
    image_pack_urls: List[str] = []
    digital_pack_zip_url: str = ""
    contact_sheet_url: str = ""
    status: str = "COMPLETED"
    is_demo: bool = False
    business_type: str = "LOCAL_FIRST"
    maturity_band: str = "SIGNIFICANT OPPORTUNITY"
    commercial_tier: str = "FOUNDATION"

class LeadProspectRequest(BaseModel):
    niche: str
    location: str
    limit: int = 10
    webhook_url: Optional[str] = None

class LeadItem(BaseModel):
    id: str
    created_at: str
    business_name: str
    niche: str
    location: str
    category: str
    phone: Optional[str] = None
    website: Optional[str] = None
    maps_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    opportunity_flag: str  # NO_WEBSITE, NO_WHATSAPP, REVIEW_DEFICIT, STRONG_REPUTATION
    opportunity_summary: str
    status: str = "NEW"  # NEW, AUDITED, CONTACTED
    audit_id: Optional[str] = None
    audit_score: Optional[int] = None
    whatsapp_pitch_link: Optional[str] = None
    is_finalized: bool = False
    stage: str = "PITCH_READY"  # PITCH_READY, CONTACTED, FOLLOW_UP, CALL_SCHEDULED, WON, LOST
    notes: Optional[str] = None
    next_followup: Optional[str] = None
    last_contacted: Optional[str] = None

class LeadUpdateRequest(BaseModel):
    is_finalized: Optional[bool] = None
    stage: Optional[str] = None
    notes: Optional[str] = None
    next_followup: Optional[str] = None
    last_contacted: Optional[str] = None
    status: Optional[str] = None

class LeadProspectResponse(BaseModel):
    niche: str
    location: str
    total_found: int
    leads: List[LeadItem]
    csv_export_url: str
    webhook_synced: bool = False

class BulkDeleteRequest(BaseModel):
    lead_ids: List[str]

class BulkStageUpdateRequest(BaseModel):
    lead_ids: List[str]
    stage: str
