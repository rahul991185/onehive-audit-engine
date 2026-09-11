import React, { useState, useEffect } from 'react';
import { 
  X, Download, ChevronLeft, ChevronRight, Layers, FileText, 
  CheckCircle2, Image as ImageIcon, Archive, Grid
} from 'lucide-react';
import { StructuredAudit } from '../types/audit';

interface ImagePackModalProps {
  audit: StructuredAudit;
  isOpen: boolean;
  onClose: () => void;
  initialPage?: number;
}

const PAGE_NAMES = [
  '01 Digital Presence Snapshot',
  '02 Your Growth Opportunity'
];

export const ImagePackModal: React.FC<ImagePackModalProps> = ({ 
  audit, 
  isOpen, 
  onClose,
  initialPage = 1 
}) => {
  const [currentPage, setCurrentPage] = useState<number>(initialPage);
  const [viewMode, setViewMode] = useState<'image' | 'contact-sheet' | 'pdf'>('image');

  useEffect(() => {
    setCurrentPage(initialPage);
  }, [initialPage, isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft') {
        setCurrentPage((prev) => (prev > 1 ? prev - 1 : 2));
      }
      if (e.key === 'ArrowRight') {
        setCurrentPage((prev) => (prev < 2 ? prev + 1 : 1));
      }
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

  const businessName = audit.business.business_name || audit.business.name || 'Client';
  const businessSlug = businessName.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  
  const currentImageUrl = `/api/audits/${audit.audit_id}/images/${currentPage}`;
  const zipUrl = `/api/audits/${audit.audit_id}/image-pack-zip`;
  const contactSheetUrl = `/api/audits/${audit.audit_id}/contact-sheet`;
  const pdfUrl = `/api/reports/${audit.audit_id}/pdf`;
  const pdfDownloadUrl = `/api/reports/${audit.audit_id}/download`;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div 
        className="modal-dialog image-pack-modal-dialog" 
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '1100px', width: '95vw', height: '94vh', display: 'flex', flexDirection: 'column' }}
      >
        {/* Modal Header */}
        <div className="modal-header" style={{ padding: '12px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
          <div className="modal-header-title" style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Layers size={20} style={{ color: 'var(--accent-gold)' }} />
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 800, color: '#FFFFFF' }}>
                  {businessName}
                </h3>
                <span className="pack-verified-pill" style={{
                  fontSize: '10px',
                  background: 'rgba(255, 196, 0, 0.15)',
                  color: 'var(--accent-gold)',
                  padding: '2px 8px',
                  borderRadius: '10px',
                  fontWeight: 800,
                  letterSpacing: '0.5px'
                }}>
                  PRIMARY DELIVERABLE: 2-PAGE REPORT
                </span>
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                300 DPI A4 High-Resolution Deliverable (2480 × 3508 px)
              </div>
            </div>
          </div>

          <div className="modal-header-actions" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {/* View Mode Switcher */}
            <div style={{ display: 'flex', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px', padding: '2px' }}>
              <button
                type="button"
                className={`tab-btn ${viewMode === 'image' ? 'active' : ''}`}
                onClick={() => setViewMode('image')}
                style={{
                  padding: '6px 12px',
                  fontSize: '11px',
                  fontWeight: 700,
                  borderRadius: '6px',
                  border: 'none',
                  background: viewMode === 'image' ? 'var(--accent-gold)' : 'transparent',
                  color: viewMode === 'image' ? '#101828' : 'var(--text-muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}
              >
                <ImageIcon size={13} />
                Images (2)
              </button>

              <button
                type="button"
                className={`tab-btn ${viewMode === 'contact-sheet' ? 'active' : ''}`}
                onClick={() => setViewMode('contact-sheet')}
                style={{
                  padding: '6px 12px',
                  fontSize: '11px',
                  fontWeight: 700,
                  borderRadius: '6px',
                  border: 'none',
                  background: viewMode === 'contact-sheet' ? 'var(--accent-gold)' : 'transparent',
                  color: viewMode === 'contact-sheet' ? '#101828' : 'var(--text-muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}
              >
                <Grid size={13} />
                Side-by-Side QA Sheet
              </button>

              <button
                type="button"
                className={`tab-btn ${viewMode === 'pdf' ? 'active' : ''}`}
                onClick={() => setViewMode('pdf')}
                style={{
                  padding: '6px 12px',
                  fontSize: '11px',
                  fontWeight: 700,
                  borderRadius: '6px',
                  border: 'none',
                  background: viewMode === 'pdf' ? 'var(--accent-gold)' : 'transparent',
                  color: viewMode === 'pdf' ? '#101828' : 'var(--text-muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}
              >
                <FileText size={13} />
                PDF (2 Pages)
              </button>
            </div>

            {/* ZIP Download Button */}
            <a
              href={zipUrl}
              className="btn-action-primary"
              download={`onehive-${businessSlug}-digital-presence-pack.zip`}
              style={{ padding: '7px 14px', fontSize: '11px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}
              title="Download 2 high-res PNG images + audit metadata in ZIP"
            >
              <Archive size={14} />
              <span>Download 2-Page ZIP</span>
            </a>

            <button type="button" className="btn-close" onClick={onClose} aria-label="Close modal">
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Page Switcher Bar (when in image mode) */}
        {viewMode === 'image' && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 20px',
            background: 'rgba(16, 24, 40, 0.6)',
            borderBottom: '1px solid var(--border-subtle)',
            gap: '12px'
          }}>
            {/* Page Buttons */}
            <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', flex: 1 }}>
              {[1, 2].map((pageNum) => (
                <button
                  key={pageNum}
                  type="button"
                  onClick={() => setCurrentPage(pageNum)}
                  style={{
                    padding: '6px 16px',
                    fontSize: '12px',
                    fontWeight: currentPage === pageNum ? 800 : 600,
                    borderRadius: '6px',
                    border: currentPage === pageNum ? '1px solid var(--accent-gold)' : '1px solid rgba(255, 255, 255, 0.1)',
                    background: currentPage === pageNum ? 'rgba(255, 196, 0, 0.15)' : 'rgba(255, 255, 255, 0.03)',
                    color: currentPage === pageNum ? 'var(--accent-gold)' : 'var(--text-secondary)',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {PAGE_NAMES[pageNum - 1]}
                </button>
              ))}
            </div>

            {/* Quick Actions for Current Page */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
              <a
                href={`${currentImageUrl}?download=true`}
                download={`page-0${currentPage}.png`}
                className="btn-action-secondary"
                style={{ padding: '5px 12px', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '5px' }}
                title={`Download Page ${currentPage} as 2480x3508 PNG`}
              >
                <Download size={12} />
                <span>Save PNG</span>
              </a>
            </div>
          </div>
        )}

        {/* Modal Main Display Body */}
        <div style={{
          flex: 1,
          overflow: 'auto',
          background: '#0B0F19',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px',
          position: 'relative'
        }}>
          {viewMode === 'image' && (
            <div style={{
              position: 'relative',
              maxWidth: '100%',
              maxHeight: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {/* Previous Page Arrow Button */}
              <button
                type="button"
                onClick={() => setCurrentPage((prev) => (prev > 1 ? prev - 1 : 2))}
                style={{
                  position: 'fixed',
                  left: '30px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'rgba(16, 24, 40, 0.85)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  color: '#FFFFFF',
                  borderRadius: '50%',
                  width: '44px',
                  height: '44px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  zIndex: 20,
                  transition: 'all 0.15s ease'
                }}
                title="Previous Page (ArrowLeft)"
              >
                <ChevronLeft size={24} />
              </button>

              {/* Page Image */}
              <img
                src={currentImageUrl}
                alt={`${businessName} — Page ${currentPage}`}
                style={{
                  maxHeight: '75vh',
                  maxWidth: '100%',
                  objectFit: 'contain',
                  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)',
                  borderRadius: '4px',
                  border: '1px solid rgba(255, 255, 255, 0.08)'
                }}
              />

              {/* Next Page Arrow Button */}
              <button
                type="button"
                onClick={() => setCurrentPage((prev) => (prev < 2 ? prev + 1 : 1))}
                style={{
                  position: 'fixed',
                  right: '30px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'rgba(16, 24, 40, 0.85)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  color: '#FFFFFF',
                  borderRadius: '50%',
                  width: '44px',
                  height: '44px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  zIndex: 20,
                  transition: 'all 0.15s ease'
                }}
                title="Next Page (ArrowRight)"
              >
                <ChevronRight size={24} />
              </button>
            </div>
          )}

          {viewMode === 'contact-sheet' && (
            <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '10px' }}>
                Visual QA Side-by-Side Sheet — Review both pages side-by-side
              </div>
              <img
                src={contactSheetUrl}
                alt="Visual QA Contact Sheet"
                style={{
                  maxHeight: '72vh',
                  maxWidth: '95%',
                  objectFit: 'contain',
                  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)',
                  borderRadius: '6px',
                  border: '1px solid rgba(255, 255, 255, 0.1)'
                }}
              />
              <div style={{ marginTop: '10px' }}>
                <a
                  href={contactSheetUrl}
                  download="onehive-qa-contact-sheet.png"
                  className="btn-action-secondary"
                  style={{ padding: '6px 14px', fontSize: '11px', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                >
                  <Download size={13} />
                  <span>Download Contact Sheet PNG</span>
                </a>
              </div>
            </div>
          )}

          {viewMode === 'pdf' && (
            <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
              <iframe
                src={`${pdfUrl}#toolbar=0`}
                style={{ width: '100%', flex: 1, border: 'none', borderRadius: '4px' }}
                title="2-Page PDF Preview"
              />
              <div style={{ padding: '10px 0', textAlign: 'center' }}>
                <a
                  href={pdfDownloadUrl}
                  download={`${businessSlug}-digital-presence-report.pdf`}
                  className="btn-action-primary"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '8px 18px', fontSize: '12px' }}
                >
                  <Download size={14} />
                  <span>Download 2-Page PDF</span>
                </a>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer Info */}
        <div className="modal-footer" style={{
          padding: '10px 20px',
          borderTop: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '11.5px',
          color: 'var(--text-muted)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle2 size={13} style={{ color: 'var(--status-green)' }} />
            <span>Strictly 2 Pages • Zero Website Preview Mockups Inside Report • Pure Vector SVGs</span>
          </div>

          <div>
            {viewMode === 'image' && (
              <span>Page {currentPage} of 2 (Use &larr; / &rarr; keys to flip)</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
