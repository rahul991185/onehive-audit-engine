import React, { useState } from 'react';
import { X, Copy, Check, MessageSquare, Send, ShieldAlert } from 'lucide-react';
import { StructuredAudit } from '../types/audit';

interface WhatsAppModalProps {
  audit: StructuredAudit;
  isOpen: boolean;
  onClose: () => void;
}

export const WhatsAppModal: React.FC<WhatsAppModalProps> = ({ audit, isOpen, onClose }) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const messageText = audit.whatsapp_message || '';
  const businessName = audit.business.business_name || audit.business.name || 'Business';

  const handleCopy = () => {
    if (messageText) {
      navigator.clipboard.writeText(messageText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog whatsapp-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-title">
            <MessageSquare size={18} style={{ color: '#25D366' }} />
            <div>
              <h3>Personalized WhatsApp Outreach</h3>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                Consultative, non-spammy introduction for OneHive sales executives
              </p>
            </div>
          </div>

          <div className="modal-header-actions">
            <button type="button" className="btn-close" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="modal-body whatsapp-body">
          {/* WhatsApp Preview Bubble */}
          <div className="whatsapp-preview-card">
            <div className="whatsapp-chat-header">
              <div className="chat-avatar">
                {businessName.charAt(0)}
              </div>
              <div className="chat-recipient">
                <span className="recipient-name">{businessName}</span>
                <span className="recipient-status">Digital Presence Contact</span>
              </div>
            </div>

            <div className="whatsapp-bubble-container">
              <div className="whatsapp-bubble">
                <p className="bubble-text">{messageText}</p>
                <div className="bubble-timestamp">
                  Just now • Delivered
                </div>
              </div>
            </div>
          </div>

          {/* Guidelines note */}
          <div className="whatsapp-note-row">
            <ShieldAlert size={14} style={{ color: 'var(--accent-gold)' }} />
            <span>
              Best practice: Review the message, personalize greeting if recipient contact is known, and paste manually into WhatsApp. No automated spamming is executed.
            </span>
          </div>

          {/* Action Button */}
          <div className="whatsapp-actions-row">
            <button
              type="button"
              className={`btn-action-primary whatsapp-copy-btn ${copied ? 'copied-btn' : ''}`}
              onClick={handleCopy}
            >
              {copied ? <Check size={16} /> : <Copy size={16} />}
              <span>{copied ? 'Copied to Clipboard!' : 'Copy WhatsApp Message'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
