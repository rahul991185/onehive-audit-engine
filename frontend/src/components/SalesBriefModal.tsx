import React from 'react';
import { X, ShieldAlert, Download, Briefcase, Target, HelpCircle, CheckCircle2, TrendingUp, AlertTriangle } from 'lucide-react';
import { StructuredAudit } from '../types/audit';

interface SalesBriefModalProps {
  audit: StructuredAudit;
  isOpen: boolean;
  onClose: () => void;
}

export const SalesBriefModal: React.FC<SalesBriefModalProps> = ({ audit, isOpen, onClose }) => {
  if (!isOpen) return null;

  const brief = audit.sales_brief;
  const businessName = audit.business.business_name || audit.business.name || brief?.business_name || 'Business';
  const downloadUrl = `/api/audits/${audit.audit_id}/sales-brief`;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog sales-brief-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-title">
            <ShieldAlert size={18} style={{ color: 'var(--accent-gold)' }} />
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h3>Internal Sales Intelligence Brief</h3>
                <span className="internal-confidential-tag">INTERNAL USE ONLY</span>
              </div>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Target Account Strategy & Discovery Playbook • {businessName}
              </p>
            </div>
          </div>

          <div className="modal-header-actions">
            <a
              href={downloadUrl}
              download={`${businessName.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-sales-brief.txt`}
              className="btn-modal-action"
            >
              <Download size={14} />
              <span>Download Brief</span>
            </a>

            <button type="button" className="btn-close" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="modal-body sales-brief-body">
          {/* Quick Business & Confidence Summary */}
          <div className="brief-account-grid">
            <div className="brief-field-card">
              <span className="brief-field-label">Account Name</span>
              <span className="brief-field-val">{businessName}</span>
            </div>
            <div className="brief-field-card">
              <span className="brief-field-label">Industry & Location</span>
              <span className="brief-field-val">
                {audit.business.category || brief?.industry} • {audit.business.city || audit.business.address || brief?.location}
              </span>
            </div>
            <div className="brief-field-card">
              <span className="brief-field-label">Identity Confidence</span>
              <span className="brief-field-val confidence-high">
                {brief?.identity_confidence || 'HIGH'} (Verified)
              </span>
            </div>
            <div className="brief-field-card">
              <span className="brief-field-label">Audit Score</span>
              <span className="brief-field-val score-val">{audit.overall_score} / 100</span>
            </div>
          </div>

          {/* Core Opportunity & Recommended Solution */}
          <div className="brief-strategy-section">
            <div className="strategy-card primary-opp">
              <div className="card-top-tag">
                <Target size={14} />
                <span>Primary Sales Wedge (#1 Opportunity)</span>
              </div>
              <h4 className="strategy-title">{brief?.top_opportunity || audit.top_opportunity.title}</h4>
              <p className="strategy-desc">{brief?.why_it_matters || audit.top_opportunity.why_it_matters}</p>
            </div>

            <div className="strategy-card solution-opp">
              <div className="card-top-tag">
                <Briefcase size={14} />
                <span>Recommended OneHive Service</span>
              </div>
              <h4 className="strategy-title">{brief?.recommended_service || audit.top_opportunity.recommended_service}</h4>
              <p className="strategy-desc">
                <strong>Likely Buying Trigger:</strong> {brief?.likely_buying_trigger || 'Converting high-intent inbound searchers with zero website friction'}
              </p>
            </div>
          </div>

          {/* Strengths & Weakness Analysis */}
          <div className="brief-swot-grid">
            <div className="brief-swot-box asset">
              <div className="swot-label">
                <CheckCircle2 size={13} />
                <span>Strongest Validated Asset (Leverage in Pitch)</span>
              </div>
              <p className="swot-text">{brief?.strongest_asset || audit.strongest_asset}</p>
            </div>

            <div className="brief-swot-box gap">
              <div className="swot-label">
                <AlertTriangle size={13} />
                <span>Primary Gap (The Diagnosis)</span>
              </div>
              <p className="swot-text">{brief?.biggest_gap || audit.biggest_gap}</p>
            </div>
          </div>

          {/* The Pitch Angle & Script */}
          <div className="brief-playbook-section">
            <h4 className="playbook-heading">
              <TrendingUp size={15} style={{ color: 'var(--accent-gold)' }} />
              <span>Consultative Sales Pitch Script</span>
            </h4>

            <div className="playbook-card">
              <div className="playbook-item">
                <span className="playbook-item-label">Consultative Angle:</span>
                <p className="playbook-item-content">{brief?.sales_angle}</p>
              </div>

              <div className="playbook-item">
                <span className="playbook-item-label">Opening Message Script:</span>
                <p className="playbook-item-content script-quote">{brief?.opening_message}</p>
              </div>
            </div>
          </div>

          {/* Objection Handling */}
          <div className="brief-playbook-section">
            <h4 className="playbook-heading">
              <HelpCircle size={15} style={{ color: '#F59E0B' }} />
              <span>Anticipated Objection & Recommended Counter</span>
            </h4>

            <div className="objection-card">
              <div className="objection-row">
                <span className="objection-tag">Anticipated Objection:</span>
                <span className="objection-text">"{brief?.objection_to_expect}"</span>
              </div>
              <div className="objection-row response">
                <span className="objection-tag green">Recommended Pivot:</span>
                <span className="objection-text">{brief?.objection_response}</span>
              </div>
            </div>
          </div>

          {/* Sales Safety: What NOT to say vs Say Instead */}
          {brief?.what_not_to_say && brief.what_not_to_say.length > 0 && (
            <div className="brief-playbook-section">
              <h4 className="playbook-heading" style={{ color: '#F87171' }}>
                <ShieldAlert size={15} style={{ color: '#F87171' }} />
                <span>Sales Safety Guardrails (What NOT To Say vs. Say Instead)</span>
              </h4>
              <div style={{ background: '#18181B', borderRadius: '8px', border: '1px solid #27272A', overflow: 'hidden' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                  <thead>
                    <tr style={{ background: '#27272A', textAlign: 'left', color: '#A1A1AA' }}>
                      <th style={{ padding: '8px 12px', width: '50%', color: '#F87171' }}>✕ DO NOT SAY</th>
                      <th style={{ padding: '8px 12px', width: '50%', color: '#34D399' }}>✓ SAY INSTEAD</th>
                    </tr>
                  </thead>
                  <tbody>
                    {brief.what_not_to_say.map((item, idx) => (
                      <tr key={idx} style={{ borderTop: '1px solid #27272A' }}>
                        <td style={{ padding: '10px 12px', color: '#FCA5A5', verticalAlign: 'top' }}>"{item.do_not_say}"</td>
                        <td style={{ padding: '10px 12px', color: '#6EE7B7', verticalAlign: 'top' }}>"{item.say_instead}"</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Recommended Next Step */}
          <div className="brief-next-step-bar">
            <div>
              <span className="next-step-label">Recommended Next Action:</span>
              <p className="next-step-val">{brief?.recommended_next_step || 'Send WhatsApp outreach message and offer complimentary diagnostic review walkthrough.'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
