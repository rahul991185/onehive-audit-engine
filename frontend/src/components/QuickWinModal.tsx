import React, { useState } from 'react';
import { X, Copy, Check, Download, Zap, Sparkles, MessageSquare, Link, MapPin } from 'lucide-react';
import { StructuredAudit } from '../types/audit';

interface QuickWinModalProps {
  audit: StructuredAudit;
  isOpen: boolean;
  onClose: () => void;
}

export const QuickWinModal: React.FC<QuickWinModalProps> = ({ audit, isOpen, onClose }) => {
  const [copiedLink, setCopiedLink] = useState(false);
  const [copiedScript, setCopiedScript] = useState(false);
  const [copiedFull, setCopiedFull] = useState(false);

  if (!isOpen) return null;

  const quickWin = audit.quick_win;
  const businessName = audit.business.business_name || audit.business.name || 'Business';

  const handleCopyLink = () => {
    if (quickWin?.whatsapp_link) {
      navigator.clipboard.writeText(quickWin.whatsapp_link);
      setCopiedLink(true);
      setTimeout(() => setCopiedLink(false), 2000);
    }
  };

  const handleCopyScript = () => {
    if (quickWin?.first_response_script) {
      navigator.clipboard.writeText(quickWin.first_response_script);
      setCopiedScript(true);
      setTimeout(() => setCopiedScript(false), 2000);
    }
  };

  const handleCopyFull = () => {
    if (quickWin?.ready_to_use_asset) {
      navigator.clipboard.writeText(quickWin.ready_to_use_asset);
      setCopiedFull(true);
      setTimeout(() => setCopiedFull(false), 2000);
    }
  };

  const downloadUrl = `/api/audits/${audit.audit_id}/quick-win`;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog quick-win-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-title">
            <Zap size={18} style={{ color: 'var(--accent-gold)' }} />
            <div>
              <h3>Your Personalized Quick Win</h3>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Immediate value asset derived directly from your #{1} opportunity
              </p>
            </div>
          </div>

          <div className="modal-header-actions">
            <button type="button" className="btn-close" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="modal-body quick-win-body">
          {/* Quick Win Title & Category */}
          <div className="quick-win-meta-card">
            <div className="quick-win-tag-row">
              <span className="quick-win-badge">{quickWin.category || 'High-Impact Asset'}</span>
              <span className="quick-win-for">Prepared for {businessName}</span>
            </div>
            <h2 className="quick-win-title">{quickWin.title}</h2>
          </div>

          {/* Why We Chose This */}
          <div className="quick-win-section">
            <div className="section-mini-header">
              <Sparkles size={14} style={{ color: 'var(--accent-gold)' }} />
              <span>Why We Chose This</span>
            </div>
            <p className="quick-win-why-text">
              {quickWin.why_chosen}
            </p>
          </div>

          {/* Structured Human-Readable Asset Blocks */}
          {quickWin.whatsapp_link && (
            <div className="quick-win-section">
              <div className="section-mini-header" style={{ justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Link size={14} style={{ color: 'var(--accent-gold)' }} />
                  <span style={{ color: '#FFFFFF', fontWeight: 700 }}>1. Direct WhatsApp Enquiry Link</span>
                </div>
                <button
                  type="button"
                  onClick={handleCopyLink}
                  style={{
                    background: copiedLink ? '#10B981' : '#27272A',
                    color: '#FFFFFF',
                    border: '1px solid #3F3F46',
                    padding: '4px 10px',
                    borderRadius: '6px',
                    fontSize: '11px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  {copiedLink ? <Check size={12} /> : <Copy size={12} />}
                  <span>{copiedLink ? 'Copied' : 'Copy Link'}</span>
                </button>
              </div>
              <div style={{ background: '#18181B', border: '1px solid #27272A', borderRadius: '8px', padding: '10px 14px', fontSize: '12px', color: '#38BDF8', wordBreak: 'break-all' }}>
                {quickWin.whatsapp_link}
              </div>
            </div>
          )}

          {quickWin.first_response_script && (
            <div className="quick-win-section">
              <div className="section-mini-header" style={{ justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <MessageSquare size={14} style={{ color: '#34D399' }} />
                  <span style={{ color: '#FFFFFF', fontWeight: 700 }}>2. First-Response Reception Script (WhatsApp Business)</span>
                </div>
                <button
                  type="button"
                  onClick={handleCopyScript}
                  style={{
                    background: copiedScript ? '#10B981' : '#27272A',
                    color: '#FFFFFF',
                    border: '1px solid #3F3F46',
                    padding: '4px 10px',
                    borderRadius: '6px',
                    fontSize: '11px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  {copiedScript ? <Check size={12} /> : <Copy size={12} />}
                  <span>{copiedScript ? 'Copied' : 'Copy Response'}</span>
                </button>
              </div>
              <div style={{ background: '#18181B', border: '1px solid #27272A', borderRadius: '8px', padding: '12px 14px', fontSize: '12px', color: '#E4E4E7', whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>
                {quickWin.first_response_script}
              </div>
            </div>
          )}

          {quickWin.suggested_placement && quickWin.suggested_placement.length > 0 && (
            <div className="quick-win-section">
              <div className="section-mini-header">
                <MapPin size={14} style={{ color: 'var(--accent-gold)' }} />
                <span style={{ color: '#FFFFFF', fontWeight: 700 }}>3. Suggested Placement Guidance</span>
              </div>
              <div style={{ background: '#18181B', border: '1px solid #27272A', borderRadius: '8px', padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', color: '#A1A1AA' }}>
                {quickWin.suggested_placement.map((item, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                    <span style={{ color: 'var(--accent-gold)', fontWeight: 800 }}>•</span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Raw Full Asset Fallback if not structured */}
          {!quickWin.whatsapp_link && (
            <div className="quick-win-section">
              <div className="asset-box">
                <pre className="asset-pre">{quickWin.ready_to_use_asset}</pre>
              </div>
            </div>
          )}

          {/* Action Bar */}
          <div className="quick-win-actions">
            <button
              type="button"
              className={`btn-action-primary ${copiedFull ? 'copied-btn' : ''}`}
              onClick={handleCopyFull}
            >
              {copiedFull ? <Check size={16} /> : <Copy size={16} />}
              <span>{copiedFull ? 'Full Asset Copied!' : 'Copy Entire Asset'}</span>
            </button>

            <a
              href={downloadUrl}
              download={`${businessName.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-quick-win.txt`}
              className="btn-action-secondary"
            >
              <Download size={16} />
              <span>Download Text Asset</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
