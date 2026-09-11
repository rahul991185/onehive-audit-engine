export type SourceType = 'GOOGLE_MAPS' | 'WEBSITE' | 'INSTAGRAM' | 'FACEBOOK' | 'UNKNOWN';

export interface BusinessIdentity {
  business_name: string;
  category: string;
  address?: string;
  city?: string;
  phone?: string;
  website?: string;
  source_url: string;
  resolved_url?: string;
  place_id?: string;
  rating?: number;
  review_count?: number;
  identity_confidence: number;
  verified: boolean;
  is_demo: boolean;

  // Compatibility properties
  name?: string;
  industry?: string;
  location?: string;
  source_type?: SourceType;
}

export interface Scores {
  overall_score: number;
  discoverability: number;
  brand_identity: number;
  trust_reputation: number;
  website_experience: number;
  lead_conversion: number;
  social_presence: number;
  business_type?: string;
  maturity_band?: string;
  commercial_tier?: string;
  dimension_explanations?: Record<string, string>;
}

export interface EvidenceItem {
  source: string;
  field: string;
  value: string;
  confidence: number;
  observation?: string;
  status?: string;
}

export interface TopOpportunity {
  title: string;
  priority: string;
  finding: string;
  evidence: EvidenceItem[];
  why_it_matters: string;
  current_journey: string;
  improved_journey: string;
  recommended_service?: string;
  confidence: number;
}

export interface Recommendation {
  order: number;
  category: 'BUILD' | 'CONVERT' | 'GROW';
  title: string;
  description: string;
}

export interface WebsiteConcept {
  business_name: string;
  industry: string;
  location: string;
  headline: string;
  subheadline: string;
  primary_cta: string;
  secondary_cta: string;
  services: Array<{ title: string; description: string }>;
  trust_signals: string[];
  brand_colors: {
    primary: string;
    dark: string;
    background: string;
    text: string;
  };
  whatsapp_cta: string;
  final_cta: string;
}

export interface QuickWin {
  title: string;
  category: string;
  why_chosen: string;
  ready_to_use_asset: string;
  instructions: string;
  asset_format: string;
  whatsapp_link?: string;
  first_response_script?: string;
  suggested_placement?: string[];
}

export interface SalesBrief {
  business_name: string;
  industry: string;
  location: string;
  website?: string;
  identity_confidence: string;
  overall_score: number;
  scores: Scores;
  strongest_asset: string;
  biggest_gap: string;
  top_opportunity: string;
  why_it_matters: string;
  evidence_highlights: string[];
  recommended_service: string;
  likely_buying_trigger: string;
  sales_angle: string;
  opening_message: string;
  objection_to_expect: string;
  objection_response: string;
  recommended_next_step: string;
  business_type?: string;
  commercial_tier?: string;
  what_not_to_say?: Array<{ do_not_say: string; say_instead: string }>;
}

export interface StructuredAudit {
  audit_id: string;
  created_at: string;
  business: BusinessIdentity;
  overall_score: number;
  scores: Scores;
  strongest_asset: string;
  biggest_gap: string;
  attention_callout: string;
  top_opportunity: TopOpportunity;
  recommendations: Recommendation[];
  website_concept: WebsiteConcept;
  quick_win: QuickWin;
  whatsapp_message: string;
  sales_brief: SalesBrief;
  report_pdf_url: string;
  report_download_url: string;
  desktop_preview_url: string;
  mobile_preview_url: string;
  quick_win_url: string;
  sales_pack_zip_url: string;
  image_pack_urls?: string[];
  digital_pack_zip_url?: string;
  contact_sheet_url?: string;
  status: string;
  is_demo: boolean;
  business_type?: string;
  maturity_band?: string;
  commercial_tier?: string;
}
