import React, { useState } from 'react';
import { X, Monitor, Smartphone, Download, ExternalLink, Sparkles } from 'lucide-react';
import { StructuredAudit } from '../types/audit';

interface WebsitePreviewModalProps {
  audit: StructuredAudit;
  isOpen: boolean;
  onClose: () => void;
}

export const WebsitePreviewModal: React.FC<WebsitePreviewModalProps> = ({ audit, isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'desktop' | 'mobile'>('desktop');

  if (!isOpen) return null;

  const desktopUrl = `/api/audits/${audit.audit_id}/preview/desktop`;
  const mobileUrl = `/api/audits/${audit.audit_id}/preview/mobile`;

  const businessName = audit.business.business_name || audit.business.name || 'Business Concept';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog preview-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-title">
            <Sparkles size={18} style={{ color: 'var(--accent-gold)' }} />
            <div>
              <h3>Personalized Website Concept Preview</h3>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                {businessName} • Tailored Visual Concept (Non-production sales teaser)
              </p>
            </div>
          </div>

          <div className="modal-header-actions">
            {/* Tab switchers */}
            <div className="preview-tab-group">
              <button
                type="button"
                className={`preview-tab-btn ${activeTab === 'desktop' ? 'active' : ''}`}
                onClick={() => setActiveTab('desktop')}
              >
                <Monitor size={14} />
                <span>Desktop (1440px)</span>
              </button>
              <button
                type="button"
                className={`preview-tab-btn ${activeTab === 'mobile' ? 'active' : ''}`}
                onClick={() => setActiveTab('mobile')}
              >
                <Smartphone size={14} />
                <span>Mobile (390px)</span>
              </button>
            </div>

            <a
              href={activeTab === 'desktop' ? desktopUrl : mobileUrl}
              download={`${businessName.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-website-${activeTab}.png`}
              className="btn-modal-action"
            >
              <Download size={14} />
              <span>Download {activeTab === 'desktop' ? 'Desktop' : 'Mobile'} PNG</span>
            </a>

            <button type="button" className="btn-close" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="modal-body preview-modal-body">
          <div className={`preview-viewport-frame ${activeTab}`}>
            <div className="browser-mockup-bar">
              <div className="browser-dots">
                <span className="dot red"></span>
                <span className="dot yellow"></span>
                <span className="dot green"></span>
              </div>
              <div className="browser-address-bar">
                https://{businessName.toLowerCase().replace(/[^a-z0-9]+/g, '')}.onehive.preview/concept
              </div>
            </div>

            <div className="preview-image-scroll-container">
              <img
                src={activeTab === 'desktop' ? desktopUrl : mobileUrl}
                alt={`${businessName} Personalized Website Concept`}
                className={`concept-preview-img ${activeTab}`}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
