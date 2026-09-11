from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class SourceType(str, Enum):
    GOOGLE_MAPS = "GOOGLE_MAPS"
    WEBSITE = "WEBSITE"
    INSTAGRAM = "INSTAGRAM"
    FACEBOOK = "FACEBOOK"
    UNKNOWN = "UNKNOWN"

class BusinessInfo(BaseModel):
    name: str
    industry: str
    location: str
    website: Optional[str] = None
    input_url: str
    source_type: SourceType

class Scores(BaseModel):
    discoverability: int = Field(..., ge=0, le=20, description="Local discovery & SEO (max 20)")
    brand_identity: int = Field(..., ge=0, le=15, description="Brand clarity & positioning (max 15)")
    trust_reputation: int = Field(..., ge=0, le=20, description="Social proof & ratings (max 20)")
    website_experience: int = Field(..., ge=0, le=15, description="Mobile UX & load experience (max 15)")
    lead_conversion: int = Field(..., ge=0, le=20, description="Lead capture & enquiry journey (max 20)")
    social_presence: int = Field(..., ge=0, le=10, description="Social activity & cross-linking (max 10)")

class EvidenceItem(BaseModel):
    source: str
    field: str
    value: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    observation: Optional[str] = None

class TopOpportunity(BaseModel):
    title: str
    priority: str = "HIGH"
    finding: str
    evidence: List[EvidenceItem] = []
    why_it_matters: str
    current_journey: str
    improved_journey: str
    confidence: float = Field(default=0.92, ge=0.0, le=1.0)

class Recommendation(BaseModel):
    order: int
    category: str  # "BUILD" | "CONVERT" | "GROW"
    title: str
    description: str

class StructuredAudit(BaseModel):
    audit_id: str
    created_at: str
    business: BusinessInfo
    overall_score: int = Field(..., ge=0, le=100)
    scores: Scores
    strongest_asset: str
    biggest_gap: str
    attention_callout: str = "We've identified one area we believe deserves immediate attention."
    top_opportunity: TopOpportunity
    recommendations: List[Recommendation]
    report_pdf_url: Optional[str] = None
    report_download_url: Optional[str] = None

class AuditRequest(BaseModel):
    url: str

class AuditResponse(BaseModel):
    status: str = "success"
    audit: StructuredAudit
