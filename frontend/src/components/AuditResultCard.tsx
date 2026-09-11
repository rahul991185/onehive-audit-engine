import React, { useState } from 'react';
import { 
  FileText, Download, Eye, Sparkles, Zap, MessageSquare, 
  ShieldAlert, Box, CheckCircle2, AlertTriangle, ExternalLink,
  MapPin, Globe, Check
} from 'lucide-react';
import { StructuredAudit } from '../types/audit';

interface AuditResultCardProps {
  audit: StructuredAudit;
  onViewReport: (initialPage?: number) => void;
  onViewPreview: () => void;
  onViewQuickWin: () => void;
  onViewWhatsApp: () => void;
  onViewSalesBrief: () => void;
}

export const AuditResultCard: React.FC<AuditResultCardProps> = ({ 
  audit, 
  onViewReport,
  onViewPreview,
  onViewQuickWin,
  onViewWhatsApp,
  onViewSalesBrief
}) => {
  const [copiedWhatsApp, setCopiedWhatsApp] = useState(false);

  const businessName = audit.business.business_name || audit.business.name || 'Business Name';
  const industry = audit.business.category || audit.business.industry || 'Local Business';
  const location = audit.business.city || audit.business.address || audit.business.location || 'Local Area';
  const source = (audit.business.source_type || (audit.business.source_url?.includes('maps') ? 'GOOGLE_MAPS' : 'WEBSITE')).replace('_', ' ');

  const downloadPdfUrl = `/api/audits/${audit.audit_id}/report?download=true`;
  const downloadZipUrl = `/api/audits/${audit.audit_id}/sales-pack`;

  const handleCopyWhatsAppDirect = () => {
    if (audit.whatsapp_message) {
      navigator.clipboard.writeText(audit.whatsapp_message);
      setCopiedWhatsApp(true);
      setTimeout(() => setCopiedWhatsApp(false), 2500);
    }
  };

  const dimensionMaxes = {
    discoverability: 20,
    brand_identity: 15,
    trust_reputation: 20,
    website_experience: 15,
    lead_conversion: 20,
    social_presence: 10,
  };

  return (
    <div className="result-section">
      <div className="result-card">
        {/* Demo Mode / Real Research Banner */}
        {audit.is_demo ? (
          <div className="demo-data-indicator-banner">
            <span className="demo-tag">DEMO DATA MODE</span>
            <span>
              This audit was generated using verified fixture data for Apex Dental & Implant Centre. Real URL mode uses live research.
            </span>
          </div>
        ) : (
          <div className="live-research-indicator-banner">
            <span className="live-tag">LIVE EVIDENCE VERIFIED</span>
            <span>
              Real-time multi-source research completed for <strong>{businessName}</strong>. Zero mock data applied.
            </span>
          </div>
        )}

        {/* Header with Business Meta & Overall Score Badge */}
        <div className="result-header">
          <div className="result-business-info">
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span className="audit-ready-badge">
                <CheckCircle2 size={12} />
                Audit Ready
              </span>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>ID: {audit.audit_id}</span>
              {audit.business.rating && (
                <span className="rating-pill">★ {audit.business.rating.toFixed(1)} Verified Rating</span>
              )}
            </div>

            <h2>{businessName}</h2>

            <div className="result-meta-row">
              <span><strong>Category:</strong> {industry}</span>
              <span>•</span>
              <span><strong>Location:</strong> {location}</span>
              <span>•</span>
              <span><strong>Source:</strong> {source}</span>
            </div>
          </div>

          <div className="result-score-badge">
            <div className="score-number">{audit.overall_score}</div>
            <div className="score-details-text">
              <span style={{ fontWeight: 800, color: 'var(--accent-gold)' }}>{audit.maturity_band || audit.scores.maturity_band || 'Digital Maturity'}</span>
              <span>out of 100</span>
            </div>
          </div>
        </div>

        {/* 6 Deterministic Dimensions Grid */}
        <div className="dimensions-dashboard">
          <div className="dimension-metric-card">
            <div className="metric-top">
              <span>01 Discoverability</span>
              <span className="metric-score">{audit.scores.discoverability} / {dimensionMaxes.discoverability}</span>
            </div>
            <div className="metric-progress-bg">
              <div 
                className="metric-progress-bar" 
                style={{ width: `${(audit.scores.discoverability / dimensionMaxes.discoverability) * 100}%` }}
              ></div>
            </div>
            {audit.scores.dimension_explanations?.discoverability && (
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                {audit.scores.dimension_explanations.discoverability}
              </div>
            )}
          </div>

          <div className="dimension-metric-card">
            <div className="metric-top">
              <span>02 Brand & Identity</span>
              <span className="metric-score">{audit.scores.brand_identity} / {dimensionMaxes.brand_identity}</span>
            </div>
            <div className="metric-progress-bg">
              <div 
                className="metric-progress-bar" 
                style={{ width: `${(audit.scores.brand_identity / dimensionMaxes.brand_identity) * 100}%` }}
              ></div>
            </div>
            {(audit.scores.dimension_explanations?.brand_identity || audit.scores.dimension_explanations?.brand_positioning) && (
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                {audit.scores.dimension_explanations.brand_identity || audit.scores.dimension_explanations.brand_positioning}
              </div>
            )}
          </div>

          <div className="dimension-metric-card">
            <div className="metric-top">
              <span>03 Trust & Reputation</span>
              <span className="metric-score">{audit.scores.trust_reputation} / {dimensionMaxes.trust_reputation}</span>
            </div>
            <div className="metric-progress-bg">
              <div 
                className="metric-progress-bar" 
                style={{ width: `${(audit.scores.trust_reputation / dimensionMaxes.trust_reputation) * 100}%` }}
              ></div>
            </div>
            {audit.scores.dimension_explanations?.trust_reputation && (
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                {audit.scores.dimension_explanations.trust_reputation}
              </div>
            )}
          </div>

          <div className="dimension-metric-card">
            <div className="metric-top">
              <span>04 Website Experience</span>
              <span className="metric-score">{audit.scores.website_experience} / {dimensionMaxes.website_experience}</span>
            </div>
            <div className="metric-progress-bg">
              <div 
                className="metric-progress-bar" 
                style={{ width: `${(audit.scores.website_experience / dimensionMaxes.website_experience) * 100}%` }}
              ></div>
            </div>
            {(audit.scores.dimension_explanations?.website_experience || audit.scores.dimension_explanations?.digital_experience) && (
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                {audit.scores.dimension_explanations.website_experience || audit.scores.dimension_explanations.digital_experience}
              </div>
            )}
          </div>

          <div className="dimension-metric-card">
            <div className="metric-top">
              <span>05 Lead Conversion</span>
              <span className="metric-score">{audit.scores.lead_conversion} / {dimensionMaxes.lead_conversion}</span>
            </div>
            <div className="metric-progress-bg">
              <div 
                className="metric-progress-bar" 
                style={{ width: `${(audit.scores.lead_conversion / dimensionMaxes.lead_conversion) * 100}%` }}
              ></div>
            </div>
            {audit.scores.dimension_explanations?.lead_conversion && (
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                {audit.scores.dimension_explanations.lead_conversion}
              </div>
            )}
          </div>

          <div className="dimension-metric-card">
            <div className="metric-top">
              <span>06 Social Presence</span>
              <span className="metric-score">{audit.scores.social_presence} / {dimensionMaxes.social_presence}</span>
            </div>
            <div className="metric-progress-bg">
              <div 
                className="metric-progress-bar" 
                style={{ width: `${(audit.scores.social_presence / dimensionMaxes.social_presence) * 100}%` }}
              ></div>
            </div>
            {audit.scores.dimension_explanations?.social_presence && (
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                {audit.scores.dimension_explanations.social_presence}
              </div>
            )}
          </div>
        </div>

        {/* Attention Highlights */}
        <div className="highlights-grid">
          <div className="highlight-box asset">
            <div className="highlight-label">
              <CheckCircle2 size={13} style={{ display: 'inline', marginRight: '4px' }} />
              Strongest Asset
            </div>
            <div className="highlight-text">{audit.strongest_asset}</div>
          </div>

          <div className="highlight-box gap">
            <div className="highlight-label">
              <AlertTriangle size={13} style={{ display: 'inline', marginRight: '4px' }} />
              Primary Bottleneck / Gap
            </div>
            <div className="highlight-text">{audit.biggest_gap}</div>
          </div>
        </div>

        {/* #1 Primary Growth Opportunity */}
        <div className="top-opp-banner">
          <div className="opp-badge-line">
            <span className="opp-high-tag">HIGH PRIORITY #1 OPPORTUNITY</span>
            <span style={{ fontSize: '12px', color: 'var(--accent-gold)', fontWeight: 600 }}>
              Verified Signal ({(audit.top_opportunity.confidence * 100).toFixed(0)}% Confidence)
            </span>
          </div>
          <div className="opp-title-text">{audit.top_opportunity.title}</div>
          <p className="opp-desc-text">{audit.top_opportunity.finding}</p>

          <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div style={{ background: 'rgba(0,0,0,0.3)', padding: '12px 14px', borderRadius: '8px', border: '1px dashed var(--border-subtle)' }}>
              <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>
                Current Customer Journey
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                {audit.top_opportunity.current_journey}
              </div>
            </div>

            <div style={{ background: 'rgba(16, 185, 129, 0.08)', padding: '12px 14px', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.25)' }}>
              <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--status-green)', textTransform: 'uppercase', marginBottom: '4px' }}>
                Engineered Growth Journey
              </div>
              <div style={{ fontSize: '12px', color: '#A7F3D0' }}>
                {audit.top_opportunity.improved_journey}
              </div>
            </div>
          </div>
        </div>

        {/* PRIMARY CLIENT DELIVERABLE: 2-PAGE DIGITAL PRESENCE INTELLIGENCE REPORT */}
        <div className="digital-presence-pack-section" style={{
          background: 'linear-gradient(135deg, rgba(255, 196, 0, 0.08) 0%, rgba(16, 24, 40, 0.6) 100%)',
          border: '1.5px solid rgba(255, 196, 0, 0.4)',
          borderRadius: '12px',
          padding: '20px',
          marginTop: '24px',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <span style={{
                  background: '#FFC400',
                  color: '#101828',
                  fontSize: '10px',
                  fontWeight: 900,
                  padding: '3px 8px',
                  borderRadius: '6px',
                  letterSpacing: '0.5px'
                }}>
                  PRIMARY CLIENT DELIVERABLE
                </span>
                <span style={{ fontSize: '11px', color: '#98A2B3' }}>
                  A4 High-Resolution (2480 × 3508 px • 300 DPI)
                </span>
              </div>
              <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 800, color: '#FFFFFF' }}>
                2-Page Digital Presence Intelligence Report
              </h3>
              <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#D0D5DD' }}>
                Engineered for WhatsApp and email cold outreach. Zero website preview mockups inside report pages.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <button 
                type="button" 
                className="btn-action-primary"
                onClick={() => onViewReport(1)}
                style={{ padding: '10px 18px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <Eye size={16} />
                <span>View 2-Page Report</span>
              </button>

              <a 
                href={`/api/audits/${audit.audit_id}/image-pack-zip`} 
                className="btn-action-primary"
                style={{
                  background: '#101828',
                  border: '1.5px solid #FFC400',
                  color: '#FFC400',
                  padding: '10px 18px',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}
                download={`onehive-${businessName.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-digital-presence-pack.zip`}
                title="Download 2 PNG images + audit.json in ZIP"
              >
                <Download size={16} />
                <span>Download 2-Page ZIP</span>
              </a>

              <a 
                href={downloadPdfUrl} 
                className="btn-action-secondary"
                style={{ padding: '10px 16px', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}
                download={`${businessName.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-digital-presence-report.pdf`}
                title="Optional secondary PDF export (2 Pages)"
              >
                <FileText size={15} />
                <span>PDF (2 Pages)</span>
              </a>
            </div>
          </div>

          {/* 2 Quick-View Page Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
            {[
              { num: 1, title: '01 Digital Presence Snapshot', desc: 'Verified details, overall score gauge, 6-dimension breakdown & observations' },
              { num: 2, title: '02 Your Growth Opportunity', desc: 'High priority fix, why it matters, current vs recommended journey & CTA' }
            ].map((p) => (
              <button
                key={p.num}
                type="button"
                onClick={() => onViewReport(p.num)}
                style={{
                  background: 'rgba(16, 24, 40, 0.7)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px',
                  padding: '14px 16px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
                onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#FFC400')}
                onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)')}
              >
                <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--accent-gold)', marginBottom: '3px' }}>
                  PAGE 0{p.num}
                </div>
                <div style={{ fontSize: '14px', fontWeight: 700, color: '#FFFFFF', marginBottom: '4px' }}>
                  {p.title}
                </div>
                <div style={{ fontSize: '11.5px', color: 'var(--text-muted)', lineHeight: 1.35 }}>
                  {p.desc}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* STAGE-2 SALES DEMO & CONVERSION ASSETS (UNBUNDLED) */}
        <div style={{
          background: 'rgba(16, 24, 40, 0.4)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px',
          padding: '18px 20px',
          marginTop: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
            <div>
              <span style={{
                background: 'rgba(2, 122, 72, 0.15)',
                color: '#12B76A',
                fontSize: '10px',
                fontWeight: 800,
                padding: '2px 8px',
                borderRadius: '6px',
                letterSpacing: '0.5px'
              }}>
                STAGE-2 SALES DEMO & CONVERSION ASSETS
              </span>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
                Unbundled demo & outreach assets — share website preview AFTER prospect responds to report pack.
              </div>
            </div>
          </div>

          <div className="action-buttons-bar" style={{ marginTop: 0 }}>
            <button
              type="button"
              className="btn-action-primary"
              style={{ background: 'linear-gradient(135deg, #12B76A 0%, #027A48 100%)', borderColor: '#12B76A' }}
              onClick={onViewPreview}
            >
              <Sparkles size={16} />
              <span>Personalized Website Preview</span>
            </button>

            <button
              type="button"
              className="btn-action-secondary"
              onClick={onViewQuickWin}
            >
              <Zap size={16} style={{ color: '#F59E0B' }} />
              <span>View Quick Win</span>
            </button>

            <button
              type="button"
              className={`btn-action-secondary ${copiedWhatsApp ? 'action-copied-feedback' : ''}`}
              onClick={onViewWhatsApp}
            >
              <MessageSquare size={16} style={{ color: '#25D366' }} />
              <span>{copiedWhatsApp ? 'Copied WhatsApp!' : 'WhatsApp Message'}</span>
            </button>

            <button
              type="button"
              className="btn-action-secondary"
              onClick={onViewSalesBrief}
            >
              <ShieldAlert size={16} style={{ color: 'var(--accent-gold)' }} />
              <span>Sales Intelligence Brief</span>
            </button>

            <a 
              href={downloadZipUrl} 
              className="btn-action-secondary zip-pack-btn"
              download={`${businessName.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-growth-pack.zip`}
              title="Download full package: PDF, Desktop/Mobile PNGs, Quick Win, Sales Brief, and JSON metadata"
            >
              <Box size={16} />
              <span>Complete Sales Pack ZIP</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
