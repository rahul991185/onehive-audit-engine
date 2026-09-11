import React, { useEffect } from 'react';
import { X, Download, FileText } from 'lucide-react';
import { StructuredAudit } from '../types/audit';

interface PdfViewerModalProps {
  audit: StructuredAudit;
  isOpen: boolean;
  onClose: () => void;
}

export const PdfViewerModal: React.FC<PdfViewerModalProps> = ({ audit, isOpen, onClose }) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const pdfUrl = `/api/reports/${audit.audit_id}/pdf`;
  const downloadUrl = `/api/reports/${audit.audit_id}/download`;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-title">
            <FileText size={18} style={{ color: 'var(--accent-gold)' }} />
            <h3>{audit.business.name} — 5-Page Consulting Report</h3>
            <span style={{ 
              fontSize: '11px', 
              background: 'rgba(255, 184, 0, 0.15)', 
              color: 'var(--accent-gold)', 
              padding: '2px 8px', 
              borderRadius: '12px',
              fontWeight: 700 
            }}>
              Verified 5 Pages
            </span>
          </div>

          <div className="modal-header-actions">
            <a 
              href={downloadUrl} 
              className="btn-action-primary" 
              style={{ padding: '8px 16px', fontSize: '12px' }}
              download
            >
              <Download size={14} />
              <span>Download PDF</span>
            </a>
            <button type="button" className="btn-close" onClick={onClose} aria-label="Close modal">
              <X size={20} />
            </button>
          </div>
        </div>

        <div className="modal-body">
          <iframe
            src={`${pdfUrl}#toolbar=1&navpanes=0&scrollbar=1`}
            title={`OneHive Intelligence Report - ${audit.business.name}`}
            className="modal-iframe"
          />
        </div>
      </div>
    </div>
  );
};
