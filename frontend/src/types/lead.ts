export type OpportunityFlag = 'NO_WEBSITE' | 'NO_WHATSAPP' | 'REVIEW_DEFICIT' | 'GROWTH_OPPORTUNITY';
export type LeadStatus = 'NEW' | 'AUDITING' | 'AUDITED' | 'CONTACTED';
export type PipelineStage = 'PITCH_READY' | 'CONTACTED' | 'FOLLOW_UP' | 'CALL_SCHEDULED' | 'WON' | 'LOST';

export interface LeadItem {
  id: string;
  created_at: string;
  business_name: string;
  niche: string;
  location: string;
  category: string;
  phone?: string | null;
  website?: string | null;
  maps_url?: string | null;
  rating?: number | null;
  review_count?: number | null;
  opportunity_flag: OpportunityFlag;
  opportunity_summary: string;
  status: LeadStatus;
  audit_id?: string | null;
  audit_score?: number | null;
  whatsapp_pitch_link?: string | null;
  is_finalized?: boolean;
  stage?: PipelineStage;
  notes?: string | null;
  next_followup?: string | null;
  last_contacted?: string | null;
}

export interface LeadProspectRequest {
  niche: string;
  location: string;
  limit?: number;
  webhook_url?: string | null;
}

export interface LeadProspectResponse {
  niche: string;
  location: string;
  total_found: number;
  leads: LeadItem[];
  csv_export_url: string;
  webhook_synced: boolean;
}
