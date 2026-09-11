'use client';

import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { AuditInputCard } from '../components/AuditInputCard';
import { ProgressTracker } from '../components/ProgressTracker';
import { AuditResultCard } from '../components/AuditResultCard';
import { PdfViewerModal } from '../components/PdfViewerModal';
import { ImagePackModal } from '../components/ImagePackModal';
import { WebsitePreviewModal } from '../components/WebsitePreviewModal';
import { QuickWinModal } from '../components/QuickWinModal';
import { WhatsAppModal } from '../components/WhatsAppModal';
import { SalesBriefModal } from '../components/SalesBriefModal';
import { LeadProspectorTab } from '../components/LeadProspectorTab';
import { LeadTrackerTab } from '../components/LeadTrackerTab';
import { StructuredAudit } from '../types/audit';
import { History, ArrowRight, ShieldCheck, CheckCircle2, Search, Target, ClipboardList } from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'AUDIT' | 'PROSPECTOR' | 'TRACKER'>('AUDIT');
  const [audit, setAudit] = useState<StructuredAudit | null>(null);
  const [recentAudits, setRecentAudits] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Modal display toggles
  const [isImagePackModalOpen, setIsImagePackModalOpen] = useState(false);
  const [selectedReportPage, setSelectedReportPage] = useState<number>(1);
  const [isPdfModalOpen, setIsPdfModalOpen] = useState(false);
  const [isPreviewModalOpen, setIsPreviewModalOpen] = useState(false);
  const [isQuickWinModalOpen, setIsQuickWinModalOpen] = useState(false);
  const [isWhatsAppModalOpen, setIsWhatsAppModalOpen] = useState(false);
  const [isSalesBriefModalOpen, setIsSalesBriefModalOpen] = useState(false);

  useEffect(() => {
    fetchRecentAudits();
  }, []);

  const fetchRecentAudits = async () => {
    try {
      const res = await fetch('/api/audits');
      if (res.ok) {
        const data = await res.json();
        setRecentAudits(data);
      }
    } catch (err) {
      console.warn('Could not fetch audit history:', err);
    }
  };

  const handleSelectRecent = async (auditId: string) => {
    try {
      setIsLoading(true);
      setErrorMessage(null);
      const res = await fetch(`/api/audits/${auditId}`);
      if (!res.ok) throw new Error('Could not load audit details.');
      const data = await res.json();
      setAudit(data);
      setActiveTab('AUDIT');
    } catch (err: any) {
      setErrorMessage(err.message || 'Error loading saved audit.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewAuditFromLead = async (auditId: string) => {
    try {
      setIsLoading(true);
      const res = await fetch(`/api/audits/${auditId}`);
      if (res.ok) {
        const data = await res.json();
        setAudit(data);
        setSelectedReportPage(1);
        setIsImagePackModalOpen(true);
      }
    } catch (err) {
      console.error('Could not load lead audit:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateAudit = async (url: string, isDemo: boolean = false) => {
    setIsLoading(true);
    setErrorMessage(null);
    setAudit(null);

    try {
      const res = await fetch('/api/audits', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, is_demo: isDemo }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Business identification could not be verified from this URL. Please check the URL.');
      }

      const result = await res.json();
      setAudit(result);
      fetchRecentAudits();
    } catch (err: any) {
      setErrorMessage(err.message || 'An unexpected error occurred while analyzing the URL.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="app-container">
      <Header />

      {/* Hero Header */}
      <section className="hero-section">
        <div className="hero-tag">
          <span>OneHive Digital Presence Intelligence</span>
        </div>
        <h1 className="hero-title">
          Give Away The Diagnosis.<br />
          <span>Sell The Treatment.</span>
        </h1>
        <p className="hero-subtitle">
          Autonomous sales enablement platform: discover local business leads, diagnose conversion bottlenecks, and generate bespoke 2-page intelligence reports in 1 click.
        </p>

        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '12px',
          marginTop: '28px',
          marginBottom: '8px'
        }}>
          <button
            type="button"
            onClick={() => setActiveTab('AUDIT')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              borderRadius: '10px',
              fontSize: '14px',
              fontWeight: 800,
              cursor: 'pointer',
              transition: 'all 0.2s',
              background: activeTab === 'AUDIT' ? '#FFC400' : '#101828',
              color: activeTab === 'AUDIT' ? '#101828' : '#CBD5E1',
              border: activeTab === 'AUDIT' ? '2px solid #FFC400' : '1px solid #1E293B',
              boxShadow: activeTab === 'AUDIT' ? '0 4px 14px rgba(255, 196, 0, 0.25)' : 'none'
            }}
          >
            <Search size={16} />
            <span>Single Business Audit</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('PROSPECTOR')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              borderRadius: '10px',
              fontSize: '14px',
              fontWeight: 800,
              cursor: 'pointer',
              transition: 'all 0.2s',
              background: activeTab === 'PROSPECTOR' ? '#FFC400' : '#101828',
              color: activeTab === 'PROSPECTOR' ? '#101828' : '#CBD5E1',
              border: activeTab === 'PROSPECTOR' ? '2px solid #FFC400' : '1px solid #1E293B',
              boxShadow: activeTab === 'PROSPECTOR' ? '0 4px 14px rgba(255, 196, 0, 0.25)' : 'none'
            }}
          >
            <Target size={16} />
            <span>Lead Prospector & Pipeline Hub</span>
            <span style={{
              background: activeTab === 'PROSPECTOR' ? '#101828' : '#FFC400',
              color: activeTab === 'PROSPECTOR' ? '#FFC400' : '#101828',
              fontSize: '10px',
              fontWeight: 900,
              padding: '2px 6px',
              borderRadius: '4px',
              marginLeft: '4px'
            }}>
              NEW
            </span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('TRACKER')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              borderRadius: '10px',
              fontSize: '14px',
              fontWeight: 800,
              cursor: 'pointer',
              transition: 'all 0.2s',
              background: activeTab === 'TRACKER' ? '#38BDF8' : '#101828',
              color: activeTab === 'TRACKER' ? '#101828' : '#CBD5E1',
              border: activeTab === 'TRACKER' ? '2px solid #38BDF8' : '1px solid #1E293B',
              boxShadow: activeTab === 'TRACKER' ? '0 4px 14px rgba(56, 189, 248, 0.25)' : 'none'
            }}
          >
            <ClipboardList size={16} />
            <span>Lead Tracker & Follow-Ups</span>
          </button>
        </div>
      </section>

      {/* Tab 1: Single Business Audit Mode */}
      {activeTab === 'AUDIT' && (
        <>
          {/* Input Card with Responsive Grid & Demo Mode */}
          <AuditInputCard 
            onGenerate={handleGenerateAudit} 
            isLoading={isLoading} 
          />

          {/* Error Message if verification fails */}
          {errorMessage && (
            <div className="error-banner-container">
              <div className="error-title">Business Verification Notice</div>
              <div className="error-desc">{errorMessage}</div>
              <div className="error-helper-note">
                Try: full Google Maps place URL, business homepage, Instagram profile, or Facebook page.
              </div>
            </div>
          )}

          {/* Animated Multi-Step Progress Tracker */}
          {isLoading && <ProgressTracker />}

          {/* Generated Audit Result Dashboard */}
          {audit && !isLoading && (
            <AuditResultCard 
              audit={audit} 
              onViewReport={(page = 1) => {
                setSelectedReportPage(page);
                setIsImagePackModalOpen(true);
              }}
              onViewPreview={() => setIsPreviewModalOpen(true)}
              onViewQuickWin={() => setIsQuickWinModalOpen(true)}
              onViewWhatsApp={() => setIsWhatsAppModalOpen(true)}
              onViewSalesBrief={() => setIsSalesBriefModalOpen(true)}
            />
          )}

          {/* Recent Audits Table */}
          {recentAudits.length > 0 && !isLoading && (
            <div className="recent-audits-card">
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <History size={16} style={{ color: 'var(--accent-gold)' }} />
                  <h3 style={{ fontSize: '14px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.05em', color: '#FFFFFF' }}>
                    Audited Accounts History
                  </h3>
                </div>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{recentAudits.length} Records</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {recentAudits.map((item) => (
                  <div 
                    key={item.audit_id}
                    onClick={() => handleSelectRecent(item.audit_id)}
                    className="recent-audit-item"
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '14px', fontWeight: 700, color: '#FFFFFF' }}>
                          {item.business_name}
                        </span>
                        {item.is_demo ? (
                          <span className="demo-chip-small">DEMO</span>
                        ) : (
                          <span className="live-chip-small">VERIFIED</span>
                        )}
                      </div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                        {item.industry} • {item.location} • {item.created_at}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '16px', fontWeight: 800, color: 'var(--accent-gold)' }}>
                          {item.overall_score}/100
                        </div>
                        <div style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Score</div>
                      </div>
                      <ArrowRight size={14} style={{ color: 'var(--text-muted)' }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Tab 2: Lead Prospector & Pipeline Hub */}
      {activeTab === 'PROSPECTOR' && (
        <LeadProspectorTab 
          onViewAuditReport={handleViewAuditFromLead}
        />
      )}

      {/* Tab 3: Lead Tracker & Follow-Ups */}
      {activeTab === 'TRACKER' && (
        <LeadTrackerTab 
          onViewAuditReport={handleViewAuditFromLead}
        />
      )}

      {/* Modals for All Pack Elements */}
      {audit && (
        <>
          {/* 1. Primary 5-Image Digital Presence Pack Modal */}
          <ImagePackModal
            audit={audit}
            isOpen={isImagePackModalOpen}
            onClose={() => setIsImagePackModalOpen(false)}
            initialPage={selectedReportPage}
          />

          {/* 2. Secondary 5-Page PDF Viewer Modal */}
          <PdfViewerModal 
            audit={audit} 
            isOpen={isPdfModalOpen} 
            onClose={() => setIsPdfModalOpen(false)} 
          />

          {/* 2. Personalized Website Concept Viewer Modal (Desktop & Mobile) */}
          <WebsitePreviewModal
            audit={audit}
            isOpen={isPreviewModalOpen}
            onClose={() => setIsPreviewModalOpen(false)}
          />

          {/* 3. Quick Win Modal */}
          <QuickWinModal
            audit={audit}
            isOpen={isQuickWinModalOpen}
            onClose={() => setIsQuickWinModalOpen(false)}
          />

          {/* 4. WhatsApp Message Modal */}
          <WhatsAppModal
            audit={audit}
            isOpen={isWhatsAppModalOpen}
            onClose={() => setIsWhatsAppModalOpen(false)}
          />

          {/* 5. Internal Sales Intelligence Brief Modal */}
          <SalesBriefModal
            audit={audit}
            isOpen={isSalesBriefModalOpen}
            onClose={() => setIsSalesBriefModalOpen(false)}
          />
        </>
      )}
    </main>
  );
}
