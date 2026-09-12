'use client';

import React, { useState, useEffect } from 'react';
import { 
  Search, Sparkles, Download, ExternalLink, FileText, CheckCircle2, 
  AlertTriangle, Star, Phone, Globe, Building2, MapPin, TrendingUp, 
  Send, Table as TableIcon, Copy, Check, HelpCircle, RefreshCw, Zap,
  Layers, ArrowUpRight, Trash2, BookmarkCheck
} from 'lucide-react';
import { LeadItem, OpportunityFlag } from '../types/lead';

interface LeadProspectorTabProps {
  onViewAuditReport: (auditId: string) => void;
}

const NICHE_PRESETS = [
  'Dental & Healthcare Clinics',
  'Cosmetic & Luxury Salons',
  'Banquet & Wedding Venues',
  'Fine Dining Restaurants',
  'Interior & Architecture Studios',
  'Private Schools & Academies',
  'Automotive Detailing & Workshops'
];

const LOCATION_PRESETS = [
  'Indiranagar, Bengaluru',
  'South Extension, New Delhi',
  'Bandra West, Mumbai',
  'Gomti Nagar, Lucknow',
  'Jubilee Hills, Hyderabad'
];

const GOOGLE_APPS_SCRIPT_TEMPLATE = `// ------------------------------------------------------------------
// ONEHIVE LEAD PROSPECTOR -> GOOGLE SHEETS SYNC WEBHOOK
// Paste into: Google Sheet -> Extensions -> Apps Script
// Deploy -> New Deployment -> Web App (Anyone can access)
// ------------------------------------------------------------------

function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var data = JSON.parse(e.postData.contents);
    
    // Add header row if first time
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        "Timestamp", "Lead ID", "Business Name", "Niche", "Location",
        "Phone", "Website", "Rating", "Reviews", "Opportunity Trigger",
        "Consultative Summary", "Status", "WhatsApp Pitch Link"
      ]);
      sheet.getRange(1, 1, 1, 13).setFontWeight("bold").setBackground("#FFC400");
    }
    
    // Append newly discovered leads
    data.leads.forEach(function(lead) {
      sheet.appendRow([
        new Date(), lead.lead_id, lead.business_name, lead.niche, lead.location,
        lead.phone, lead.website, lead.rating, lead.reviews, lead.opportunity_trigger,
        lead.opportunity_summary, lead.status, lead.whatsapp_pitch
      ]);
    });
    
    return ContentService.createTextOutput(JSON.stringify({ "status": "success" }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ "status": "error", "message": err.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}`;

export const LeadProspectorTab: React.FC<LeadProspectorTabProps> = ({ onViewAuditReport }) => {
  const [niche, setNiche] = useState('Dental & Healthcare Clinics');
  const [location, setLocation] = useState('Indiranagar, Bengaluru');
  const [limit, setLimit] = useState(10);
  const [webhookUrl, setWebhookUrl] = useState('');
  const [showWebhookHelp, setShowWebhookHelp] = useState(false);
  const [copiedScript, setCopiedScript] = useState(false);

  const [leads, setLeads] = useState<LeadItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [auditingLeadId, setAuditingLeadId] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState<string>('ALL');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedLeadIds, setSelectedLeadIds] = useState<Set<string>>(new Set());
  const [isBulkDeleting, setIsBulkDeleting] = useState(false);
  const [isBulkTracking, setIsBulkTracking] = useState(false);

  useEffect(() => {
    fetchExistingLeads();
  }, []);

  const fetchExistingLeads = async () => {
    try {
      const res = await fetch('/api/leads');
      if (res.ok) {
        const data = await res.json();
        setLeads(data);
      }
    } catch (err) {
      console.warn('Could not fetch existing leads:', err);
    }
  };

  const handleHarvestLeads = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!niche.trim() || !location.trim()) return;

    setIsSearching(true);
    setErrorMessage(null);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 20000);

    try {
      const res = await fetch('/api/leads/prospect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          niche: niche.trim(),
          location: location.trim(),
          limit,
          webhook_url: webhookUrl.trim() || undefined
        }),
        signal: controller.signal
      });

      if (!res.ok) {
        let errorDetail = '';
        try {
          const errData = await res.json();
          errorDetail = errData.detail || errData.message || '';
        } catch {
          if (res.status === 404) {
            errorDetail = 'Lead Prospector API route not found (404). Please ensure BACKEND_API_URL is configured in Vercel.';
          } else if (res.status === 502 || res.status === 503 || res.status === 504) {
            errorDetail = 'Backend service is starting up on Render (free tier cold starts take ~40 seconds). Please retry in 30 seconds.';
          } else {
            errorDetail = `Server connection returned status ${res.status}.`;
          }
        }
        throw new Error(errorDetail || 'Failed to harvest business leads.');
      }

      const data = await res.json();
      setLeads(prev => {
        // Prepend new leads, avoiding duplicate IDs
        const existingIds = new Set(data.leads.map((l: LeadItem) => l.id));
        const filteredPrev = prev.filter(p => !existingIds.has(p.id));
        return [...data.leads, ...filteredPrev];
      });
    } catch (err: any) {
      if (err.name === 'AbortError') {
        setErrorMessage('Lead harvesting timed out. If the backend is waking up on Render, please retry in 30 seconds.');
      } else {
        setErrorMessage(err.message || 'Error occurred while discovering business leads.');
      }
    } finally {
      clearTimeout(timeoutId);
      setIsSearching(false);
    }
  };

  const handleOneClickAudit = async (lead: LeadItem) => {
    setAuditingLeadId(lead.id);
    setErrorMessage(null);

    try {
      const res = await fetch(`/api/leads/${lead.id}/audit`, {
        method: 'POST'
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Could not complete audit for this lead.');
      }

      const auditData = await res.json();

      // Update lead state in table
      setLeads(prev => prev.map(l => {
        if (l.id === lead.id) {
          return {
            ...l,
            status: 'AUDITED',
            audit_id: auditData.audit_id,
            audit_score: auditData.overall_score
          };
        }
        return l;
      }));

      // Automatically offer to view the generated report
      onViewAuditReport(auditData.audit_id);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to run audit for selected business.');
    } finally {
      setAuditingLeadId(null);
    }
  };

  const handleDeleteLead = async (leadId: string) => {
    if (!confirm('Are you sure you want to delete this lead?')) return;
    try {
      const res = await fetch(`/api/leads/${leadId}`, { method: 'DELETE' });
      if (res.ok) {
        setLeads(prev => prev.filter(l => l.id !== leadId));
        setSelectedLeadIds(prev => {
          const next = new Set(prev);
          next.delete(leadId);
          return next;
        });
      } else {
        throw new Error('Could not delete lead.');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Error deleting lead.');
    }
  };

  const handleToggleFinalize = async (lead: LeadItem) => {
    const nextFinalized = !lead.is_finalized;
    try {
      const res = await fetch(`/api/leads/${lead.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_finalized: nextFinalized })
      });
      if (res.ok) {
        setLeads(prev => prev.map(l => l.id === lead.id ? { ...l, is_finalized: nextFinalized } : l));
      }
    } catch (err) {
      console.error('Failed to update finalized status:', err);
    }
  };

  const copyScriptToClipboard = () => {
    navigator.clipboard.writeText(GOOGLE_APPS_SCRIPT_TEMPLATE);
    setCopiedScript(true);
    setTimeout(() => setCopiedScript(false), 2500);
  };

  // Filtered leads
  const filteredLeads = leads.filter(l => {
    if (activeFilter === 'ALL') return true;
    if (activeFilter === 'NO_WEBSITE') return l.opportunity_flag === 'NO_WEBSITE';
    if (activeFilter === 'NO_WHATSAPP') return l.opportunity_flag === 'NO_WHATSAPP';
    if (activeFilter === 'AUDITED') return l.status === 'AUDITED';
    return true;
  });

  const noWebsiteCount = leads.filter(l => l.opportunity_flag === 'NO_WEBSITE').length;
  const noWhatsAppCount = leads.filter(l => l.opportunity_flag === 'NO_WHATSAPP').length;
  const auditedCount = leads.filter(l => l.status === 'AUDITED').length;

  // Multiselect logic
  const handleToggleSelectLead = (leadId: string) => {
    setSelectedLeadIds(prev => {
      const next = new Set(prev);
      if (next.has(leadId)) {
        next.delete(leadId);
      } else {
        next.add(leadId);
      }
      return next;
    });
  };

  const isAllSelected = filteredLeads.length > 0 && filteredLeads.every(l => selectedLeadIds.has(l.id));
  const isSomeSelected = filteredLeads.some(l => selectedLeadIds.has(l.id)) && !isAllSelected;

  const handleToggleSelectAll = () => {
    if (isAllSelected) {
      setSelectedLeadIds(prev => {
        const next = new Set(prev);
        filteredLeads.forEach(l => next.delete(l.id));
        return next;
      });
    } else {
      setSelectedLeadIds(prev => {
        const next = new Set(prev);
        filteredLeads.forEach(l => next.add(l.id));
        return next;
      });
    }
  };

  const handleBulkDelete = async () => {
    if (selectedLeadIds.size === 0) return;
    const count = selectedLeadIds.size;
    if (!confirm(`Are you sure you want to permanently delete ${count} selected lead${count > 1 ? 's' : ''}?`)) return;

    setIsBulkDeleting(true);
    try {
      const idsToDelete = Array.from(selectedLeadIds);
      const res = await fetch('/api/leads/bulk-delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lead_ids: idsToDelete })
      });
      if (!res.ok) throw new Error('Failed to delete selected leads.');

      const deletedSet = new Set(idsToDelete);
      setLeads(prev => prev.filter(l => !deletedSet.has(l.id)));
      setSelectedLeadIds(new Set());
    } catch (err: any) {
      setErrorMessage(err.message || 'Error deleting selected leads.');
    } finally {
      setIsBulkDeleting(false);
    }
  };

  const handleBulkMoveToTracker = async () => {
    if (selectedLeadIds.size === 0) return;
    setIsBulkTracking(true);
    try {
      const idsToTrack = Array.from(selectedLeadIds);
      await Promise.all(idsToTrack.map(id =>
        fetch(`/api/leads/${id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ is_finalized: true })
        })
      ));
      const trackedSet = new Set(idsToTrack);
      setLeads(prev => prev.map(l => trackedSet.has(l.id) ? { ...l, is_finalized: true } : l));
      setSelectedLeadIds(new Set());
    } catch (err) {
      console.error('Failed to move leads to tracker:', err);
    } finally {
      setIsBulkTracking(false);
    }
  };

  return (
    <div className="lead-prospector-container" style={{ marginTop: '24px' }}>
      {/* Top Banner & Search Form */}
      <div className="prospector-banner" style={{
        background: 'linear-gradient(135deg, rgba(255, 184, 0, 0.08) 0%, rgba(13, 18, 31, 0.95) 100%)',
        border: '1px solid rgba(255, 184, 0, 0.25)',
        borderRadius: '16px',
        padding: '32px',
        marginBottom: '28px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span style={{
                background: '#FFB800',
                color: '#070A12',
                fontSize: '11px',
                fontWeight: 900,
                padding: '4px 10px',
                borderRadius: '6px',
                letterSpacing: '0.4px'
              }}>
                AUTONOMOUS SALES PROSPECTOR
              </span>
              <span style={{ fontSize: '13px', color: '#94A3B8' }}>
                Instant Local Discovery & Automated 2-Page Audit Generator
              </span>
            </div>
            <h2 style={{ fontSize: '24px', fontWeight: 800, color: '#FFFFFF', margin: 0, letterSpacing: '-0.3px' }}>
              Discover High-Value Leads & Auto-Generate Client Audits
            </h2>
            <p style={{ fontSize: '14px', color: '#CBD5E1', margin: '8px 0 0 0', lineHeight: 1.6, maxWidth: '850px' }}>
              Search any niche and city. OneHive automatically diagnoses high-converting gaps (e.g. 4.8★ with No Website), links directly to Google Sheets, and allows you to generate executive-ready 2-page reports in 1 click.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <a 
              href={`/api/leads/export-csv?niche=${encodeURIComponent(niche)}&location=${encodeURIComponent(location)}`}
              className="btn-action-primary"
              style={{
                background: 'rgba(19, 27, 45, 0.8)',
                border: '1.5px solid #FFB800',
                color: '#FFB800',
                padding: '12px 20px',
                fontSize: '13px',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                textDecoration: 'none',
                borderRadius: '10px',
                boxShadow: '0 4px 14px rgba(255, 184, 0, 0.15)'
              }}
            >
              <Download size={16} />
              <span>Export Google Sheets CSV</span>
            </a>

            <button
              type="button"
              className="btn-action-primary"
              onClick={() => setShowWebhookHelp(true)}
              style={{
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid rgba(255, 255, 255, 0.18)',
                color: '#FFFFFF',
                padding: '12px 18px',
                fontSize: '13px',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                borderRadius: '10px'
              }}
            >
              <HelpCircle size={16} />
              <span>Link Google Sheet</span>
            </button>
          </div>
        </div>

        {/* Input Form */}
        <form onSubmit={handleHarvestLeads} style={{ marginTop: '24px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1.2fr 140px auto', gap: '16px', alignItems: 'flex-end' }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 700, color: '#F1F5F9', marginBottom: '8px' }}>
                Target Business Niche
              </label>
              <input
                type="text"
                className="audit-input"
                value={niche}
                onChange={(e) => setNiche(e.target.value)}
                placeholder="e.g. Dental Clinics, Cosmetic Salons, Banquet Halls..."
                style={{ width: '100%', height: '48px', padding: '0 16px', fontSize: '14px', borderRadius: '10px' }}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 700, color: '#F1F5F9', marginBottom: '8px' }}>
                Location / City / Suburb
              </label>
              <input
                type="text"
                className="audit-input"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Indiranagar, Bengaluru or Bandra West, Mumbai"
                style={{ width: '100%', height: '48px', padding: '0 16px', fontSize: '14px', borderRadius: '10px' }}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 700, color: '#F1F5F9', marginBottom: '8px' }}>
                Lead Limit
              </label>
              <select
                className="audit-input"
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                style={{ width: '100%', height: '48px', padding: '0 12px', fontSize: '14px', borderRadius: '10px', cursor: 'pointer' }}
              >
                <option value={5}>5 Leads</option>
                <option value={10}>10 Leads</option>
                <option value={15}>15 Leads</option>
                <option value={20}>20 Leads</option>
              </select>
            </div>

            <div>
              <button
                type="submit"
                className="btn-action-primary"
                disabled={isSearching}
                style={{
                  height: '48px',
                  padding: '0 28px',
                  fontSize: '14px',
                  fontWeight: 800,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  whiteSpace: 'nowrap',
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #FFB800 0%, #E5A800 100%)',
                  color: '#070A12',
                  boxShadow: '0 4px 16px rgba(255, 184, 0, 0.3)'
                }}
              >
                {isSearching ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" />
                    <span>Discovering Leads...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    <span>Discover Leads</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Preset Chips */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '16px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 700 }}>Popular Niches:</span>
            {NICHE_PRESETS.slice(0, 4).map(preset => (
              <button
                key={preset}
                type="button"
                onClick={() => setNiche(preset)}
                style={{
                  background: niche === preset ? 'rgba(255, 184, 0, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                  border: niche === preset ? '1px solid #FFB800' : '1px solid rgba(255, 255, 255, 0.12)',
                  color: niche === preset ? '#FFB800' : '#CBD5E1',
                  borderRadius: '9999px',
                  padding: '5px 12px',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                {preset}
              </button>
            ))}

            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 700, marginLeft: '12px' }}>Cities:</span>
            {LOCATION_PRESETS.slice(0, 3).map(preset => (
              <button
                key={preset}
                type="button"
                onClick={() => setLocation(preset)}
                style={{
                  background: location === preset ? 'rgba(255, 184, 0, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                  border: location === preset ? '1px solid #FFB800' : '1px solid rgba(255, 255, 255, 0.12)',
                  color: location === preset ? '#FFB800' : '#CBD5E1',
                  borderRadius: '9999px',
                  padding: '5px 12px',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                {preset}
              </button>
            ))}
          </div>

          {/* Webhook Field */}
          <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>Google Sheets Webhook (Optional):</span>
            <input
              type="url"
              className="audit-input"
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
              placeholder="https://script.google.com/macros/s/.../exec"
              style={{ flex: 1, height: '38px', padding: '0 14px', fontSize: '12px', borderRadius: '8px' }}
            />
          </div>
        </form>
      </div>

      {/* Error Message */}
      {errorMessage && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid #EF4444',
          borderRadius: '12px',
          padding: '16px 20px',
          marginBottom: '24px',
          color: '#FCA5A5',
          fontSize: '14px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <AlertTriangle size={18} style={{ color: '#EF4444', flexShrink: 0 }} />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Pipeline Metrics Overview */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '28px' }}>
        <div className="spacious-metric-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 800, letterSpacing: '0.4px' }}>
              Total Discovered
            </span>
            <Building2 size={18} style={{ color: '#94A3B8' }} />
          </div>
          <div style={{ fontSize: '32px', fontWeight: 900, color: '#FFFFFF', margin: '8px 0 4px 0' }}>{leads.length}</div>
          <div style={{ fontSize: '12px', color: '#64748B' }}>In prospect pipeline</div>
        </div>

        <div className="spacious-metric-card" style={{ borderColor: 'rgba(239, 68, 68, 0.35)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', color: '#EF4444', textTransform: 'uppercase', fontWeight: 800, letterSpacing: '0.4px' }}>
              No Website Detected
            </span>
            <AlertTriangle size={18} style={{ color: '#EF4444' }} />
          </div>
          <div style={{ fontSize: '32px', fontWeight: 900, color: '#EF4444', margin: '8px 0 4px 0' }}>{noWebsiteCount}</div>
          <div style={{ fontSize: '12px', color: '#FCA5A5' }}>₹50k–1.5L website opportunities</div>
        </div>

        <div className="spacious-metric-card" style={{ borderColor: 'rgba(245, 158, 11, 0.35)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', color: '#F59E0B', textTransform: 'uppercase', fontWeight: 800, letterSpacing: '0.4px' }}>
              Missing WhatsApp
            </span>
            <Send size={18} style={{ color: '#F59E0B' }} />
          </div>
          <div style={{ fontSize: '32px', fontWeight: 900, color: '#F59E0B', margin: '8px 0 4px 0' }}>{noWhatsAppCount}</div>
          <div style={{ fontSize: '12px', color: '#FDE68A' }}>Immediate conversion bottleneck</div>
        </div>

        <div className="spacious-metric-card" style={{ borderColor: 'rgba(16, 185, 129, 0.35)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontSize: '12px', color: '#10B981', textTransform: 'uppercase', fontWeight: 800, letterSpacing: '0.4px' }}>
              Audited & Ready
            </span>
            <CheckCircle2 size={18} style={{ color: '#10B981' }} />
          </div>
          <div style={{ fontSize: '32px', fontWeight: 900, color: '#10B981', margin: '8px 0 4px 0' }}>{auditedCount}</div>
          <div style={{ fontSize: '12px', color: '#A7F3D0' }}>2-Page reports generated</div>
        </div>
      </div>

      {/* Filter Tabs & Selection Toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {[
            { key: 'ALL', label: `All Prospects (${leads.length})` },
            { key: 'NO_WEBSITE', label: `🔴 No Website (${noWebsiteCount})` },
            { key: 'NO_WHATSAPP', label: `🟡 Missing WhatsApp (${noWhatsAppCount})` },
            { key: 'AUDITED', label: `🟢 Audited (${auditedCount})` }
          ].map(tab => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveFilter(tab.key)}
              style={{
                background: activeFilter === tab.key ? '#FFB800' : 'rgba(19, 27, 45, 0.8)',
                color: activeFilter === tab.key ? '#070A12' : '#CBD5E1',
                border: activeFilter === tab.key ? '1px solid #FFB800' : '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '10px',
                padding: '10px 18px',
                fontSize: '13px',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.18s ease',
                boxShadow: activeFilter === tab.key ? '0 4px 12px rgba(255, 184, 0, 0.25)' : 'none'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          {/* Select All Checkbox */}
          {filteredLeads.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255, 255, 255, 0.04)', padding: '8px 14px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
              <input
                type="checkbox"
                id="selectAllProspects"
                className="onehive-checkbox"
                checked={isAllSelected}
                ref={input => {
                  if (input) input.indeterminate = isSomeSelected;
                }}
                onChange={handleToggleSelectAll}
              />
              <label htmlFor="selectAllProspects" style={{ fontSize: '13px', fontWeight: 700, color: '#E2E8F0', cursor: 'pointer', userSelect: 'none' }}>
                Select All ({filteredLeads.length})
              </label>
            </div>
          )}

          <button
            type="button"
            onClick={fetchExistingLeads}
            style={{
              background: 'transparent',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              color: '#94A3B8',
              borderRadius: '8px',
              padding: '8px 14px',
              fontSize: '13px',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Leads Table / Cards */}
      {filteredLeads.length === 0 ? (
        <div style={{
          background: 'rgba(19, 27, 45, 0.6)',
          border: '1px dashed rgba(255, 255, 255, 0.15)',
          borderRadius: '16px',
          padding: '64px 32px',
          textAlign: 'center',
          color: '#94A3B8'
        }}>
          <Building2 size={44} style={{ margin: '0 auto 16px auto', color: '#475569' }} />
          <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#F1F5F9', margin: '0 0 8px 0' }}>No Prospects in Current Filter</h3>
          <p style={{ fontSize: '14px', margin: 0, color: '#94A3B8' }}>
            Enter a niche and city above to discover high-value business leads automatically.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {filteredLeads.map(lead => {
            const isAudited = lead.status === 'AUDITED';
            const isAuditing = auditingLeadId === lead.id;
            const isSelected = selectedLeadIds.has(lead.id);

            return (
              <div 
                key={lead.id}
                className={`spacious-card ${isSelected ? 'is-selected' : ''}`}
                style={{
                  border: isSelected 
                    ? '1.5px solid rgba(255, 184, 0, 0.6)' 
                    : isAudited 
                      ? '1px solid rgba(16, 185, 129, 0.35)' 
                      : '1px solid rgba(255, 255, 255, 0.08)',
                  display: 'grid',
                  gridTemplateColumns: '36px 2.2fr 1.4fr 2fr 1.8fr',
                  gap: '20px',
                  alignItems: 'center'
                }}
              >
                {/* Col 0: Checkbox */}
                <div style={{ display: 'flex', justifyContent: 'center' }}>
                  <input
                    type="checkbox"
                    className="onehive-checkbox"
                    checked={isSelected}
                    onChange={() => handleToggleSelectLead(lead.id)}
                    aria-label={`Select lead ${lead.business_name}`}
                  />
                </div>

                {/* Col 1: Business Identity */}
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
                      {lead.business_name}
                    </h3>
                    {lead.maps_url && (
                      <a href={lead.maps_url} target="_blank" rel="noopener noreferrer" style={{ color: '#94A3B8', display: 'flex', alignItems: 'center' }} title="View on Google Maps">
                        <ExternalLink size={14} />
                      </a>
                    )}
                  </div>
                  <div style={{ fontSize: '13px', color: '#94A3B8', display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                    <span style={{ color: '#E2E8F0', fontWeight: 600 }}>{lead.category}</span>
                    <span>•</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#FFB800', fontWeight: 700 }}>
                      <Star size={13} fill="#FFB800" />
                      {lead.rating ? `${lead.rating}★` : '4.5★'} ({lead.review_count || 40} reviews)
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: '#64748B', marginTop: '6px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <MapPin size={13} style={{ color: '#94A3B8' }} />
                    <span>{lead.location}</span>
                  </div>
                </div>

                {/* Col 2: Digital Asset Status */}
                <div>
                  <div style={{ marginBottom: '8px' }}>
                    {lead.website ? (
                      <a 
                        href={lead.website} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ fontSize: '13px', color: '#38BDF8', display: 'flex', alignItems: 'center', gap: '6px', textDecoration: 'none', fontWeight: 600 }}
                      >
                        <Globe size={14} />
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '170px' }}>
                          {lead.website.replace('https://', '').replace('http://', '').split('/')[0]}
                        </span>
                      </a>
                    ) : (
                      <span style={{
                        background: 'rgba(239, 68, 68, 0.15)',
                        border: '1px solid rgba(239, 68, 68, 0.4)',
                        color: '#EF4444',
                        fontSize: '11px',
                        fontWeight: 800,
                        padding: '3px 8px',
                        borderRadius: '6px',
                        display: 'inline-block'
                      }}>
                        🔴 NO WEBSITE DETECTED
                      </span>
                    )}
                  </div>

                  <div style={{ fontSize: '13px', color: '#CBD5E1', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Phone size={13} style={{ color: '#94A3B8' }} />
                    <span>{lead.phone || 'Available via Maps'}</span>
                  </div>
                </div>

                {/* Col 3: Opportunity Diagnosis */}
                <div>
                  <div style={{ marginBottom: '6px' }}>
                    {lead.opportunity_flag === 'NO_WEBSITE' && (
                      <span style={{
                        background: 'rgba(239, 68, 68, 0.2)',
                        color: '#FCA5A5',
                        border: '1px solid rgba(239, 68, 68, 0.5)',
                        fontSize: '11px',
                        fontWeight: 900,
                        padding: '3px 10px',
                        borderRadius: '6px',
                        letterSpacing: '0.4px'
                      }}>
                        HIGH-VALUE WEBSITE PITCH
                      </span>
                    )}
                    {lead.opportunity_flag === 'NO_WHATSAPP' && (
                      <span style={{
                        background: 'rgba(245, 158, 11, 0.2)',
                        color: '#FDE68A',
                        border: '1px solid rgba(245, 158, 11, 0.5)',
                        fontSize: '11px',
                        fontWeight: 900,
                        padding: '3px 10px',
                        borderRadius: '6px',
                        letterSpacing: '0.4px'
                      }}>
                        CONVERSION BOTTLENECK
                      </span>
                    )}
                    {lead.opportunity_flag === 'REVIEW_DEFICIT' && (
                      <span style={{
                        background: 'rgba(56, 189, 248, 0.2)',
                        color: '#BAE6FD',
                        border: '1px solid rgba(56, 189, 248, 0.5)',
                        fontSize: '11px',
                        fontWeight: 900,
                        padding: '3px 10px',
                        borderRadius: '6px',
                        letterSpacing: '0.4px'
                      }}>
                        REVIEW ENGINE OPPORTUNITY
                      </span>
                    )}
                    {lead.opportunity_flag === 'GROWTH_OPPORTUNITY' && (
                      <span style={{
                        background: 'rgba(16, 185, 129, 0.2)',
                        color: '#A7F3D0',
                        border: '1px solid rgba(16, 185, 129, 0.5)',
                        fontSize: '11px',
                        fontWeight: 900,
                        padding: '3px 10px',
                        borderRadius: '6px',
                        letterSpacing: '0.4px'
                      }}>
                        DIGITAL GROWTH
                      </span>
                    )}
                  </div>
                  <p style={{ fontSize: '13px', color: '#94A3B8', margin: 0, lineHeight: 1.5 }}>
                    {lead.opportunity_summary}
                  </p>
                </div>

                {/* Col 4: Action Hub */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', alignItems: 'flex-end' }}>
                  {/* Top action row: Track toggle & Delete button */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <button
                      type="button"
                      onClick={() => handleToggleFinalize(lead)}
                      title={lead.is_finalized ? "In Lead Tracker" : "Move to Lead Tracker"}
                      style={{
                        background: lead.is_finalized ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.06)',
                        border: lead.is_finalized ? '1px solid #38BDF8' : '1px solid rgba(255, 255, 255, 0.15)',
                        color: lead.is_finalized ? '#38BDF8' : '#CBD5E1',
                        borderRadius: '6px',
                        padding: '5px 10px',
                        fontSize: '12px',
                        fontWeight: 700,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '5px',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <BookmarkCheck size={13} />
                      <span>{lead.is_finalized ? '✓ In Tracker' : '+ Track'}</span>
                    </button>

                    <button
                      type="button"
                      onClick={() => handleDeleteLead(lead.id)}
                      title="Delete this lead"
                      style={{
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid rgba(239, 68, 68, 0.3)',
                        color: '#EF4444',
                        borderRadius: '6px',
                        padding: '5px 10px',
                        fontSize: '12px',
                        fontWeight: 700,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '5px',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <Trash2 size={13} />
                      <span>Delete</span>
                    </button>
                  </div>

                  {/* Primary CTA Row */}
                  {isAudited ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end', width: '100%' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{
                          background: 'rgba(16, 185, 129, 0.15)',
                          color: '#10B981',
                          border: '1px solid rgba(16, 185, 129, 0.4)',
                          fontSize: '12px',
                          fontWeight: 800,
                          padding: '4px 10px',
                          borderRadius: '6px'
                        }}>
                          Score: {lead.audit_score}/100
                        </span>
                        <button
                          type="button"
                          onClick={() => onViewAuditReport(lead.audit_id!)}
                          style={{
                            background: '#FFB800',
                            color: '#070A12',
                            border: 'none',
                            borderRadius: '8px',
                            padding: '8px 14px',
                            fontSize: '12px',
                            fontWeight: 800,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            cursor: 'pointer',
                            boxShadow: '0 4px 12px rgba(255, 184, 0, 0.25)'
                          }}
                        >
                          <FileText size={14} />
                          <span>View 2-Page Report</span>
                        </button>
                      </div>

                      <div style={{ display: 'flex', gap: '8px' }}>
                        {lead.whatsapp_pitch_link && (
                          <a
                            href={lead.whatsapp_pitch_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              background: '#25D366',
                              color: '#FFFFFF',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '5px 12px',
                              fontSize: '12px',
                              fontWeight: 700,
                              display: 'flex',
                              alignItems: 'center',
                              gap: '5px',
                              textDecoration: 'none'
                            }}
                          >
                            <Send size={12} />
                            <span>WhatsApp Pitch</span>
                          </a>
                        )}
                        <a
                          href={`/api/audits/${lead.audit_id}/sales-pack`}
                          style={{
                            background: 'rgba(255, 255, 255, 0.06)',
                            color: '#CBD5E1',
                            border: '1px solid rgba(255, 255, 255, 0.15)',
                            borderRadius: '6px',
                            padding: '5px 10px',
                            fontSize: '12px',
                            textDecoration: 'none',
                            display: 'flex',
                            alignItems: 'center'
                          }}
                        >
                          Sales Pack
                        </a>
                      </div>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end', width: '100%' }}>
                      <button
                        type="button"
                        onClick={() => handleOneClickAudit(lead)}
                        disabled={isAuditing}
                        style={{
                          background: 'linear-gradient(135deg, #FFB800 0%, #E5A800 100%)',
                          color: '#070A12',
                          border: 'none',
                          borderRadius: '8px',
                          padding: '10px 16px',
                          fontSize: '13px',
                          fontWeight: 800,
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          cursor: isAuditing ? 'not-allowed' : 'pointer',
                          boxShadow: '0 4px 14px rgba(255, 184, 0, 0.25)'
                        }}
                      >
                        {isAuditing ? (
                          <>
                            <RefreshCw size={14} className="animate-spin" />
                            <span>Generating Report...</span>
                          </>
                        ) : (
                          <>
                            <Zap size={14} />
                            <span>Generate 2-Page Report</span>
                          </>
                        )}
                      </button>

                      {lead.whatsapp_pitch_link && (
                        <a
                          href={lead.whatsapp_pitch_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            color: '#25D366',
                            fontSize: '12px',
                            fontWeight: 700,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            textDecoration: 'none'
                          }}
                        >
                          <Send size={11} />
                          <span>Pre-fill WhatsApp Pitch</span>
                        </a>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Floating Bulk Action Bar */}
      {selectedLeadIds.size > 0 && (
        <div className="floating-bulk-bar">
          <div className="floating-bulk-badge">
            <CheckCircle2 size={16} />
            <span>{selectedLeadIds.size} Lead{selectedLeadIds.size > 1 ? 's' : ''} Selected</span>
          </div>

          <button
            type="button"
            onClick={handleBulkDelete}
            disabled={isBulkDeleting}
            style={{
              background: '#EF4444',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '9999px',
              padding: '8px 20px',
              fontSize: '13px',
              fontWeight: 800,
              cursor: isBulkDeleting ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              boxShadow: '0 4px 14px rgba(239, 68, 68, 0.4)',
              transition: 'all 0.15s ease'
            }}
          >
            <Trash2 size={15} />
            <span>{isBulkDeleting ? 'Deleting...' : `Delete Selected (${selectedLeadIds.size})`}</span>
          </button>

          <button
            type="button"
            onClick={handleBulkMoveToTracker}
            disabled={isBulkTracking}
            style={{
              background: 'rgba(56, 189, 248, 0.15)',
              border: '1.5px solid #38BDF8',
              color: '#38BDF8',
              borderRadius: '9999px',
              padding: '8px 18px',
              fontSize: '13px',
              fontWeight: 800,
              cursor: isBulkTracking ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              transition: 'all 0.15s ease'
            }}
          >
            <BookmarkCheck size={15} />
            <span>{isBulkTracking ? 'Moving...' : 'Move to Tracker'}</span>
          </button>

          <button
            type="button"
            onClick={() => setSelectedLeadIds(new Set())}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#94A3B8',
              fontSize: '13px',
              cursor: 'pointer',
              padding: '6px 12px',
              fontWeight: 600
            }}
          >
            Clear Selection
          </button>
        </div>
      )}

      {/* How to Link Google Sheet Modal */}
      {showWebhookHelp && (
        <div className="modal-overlay" style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.85)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '20px'
        }}>
          <div style={{
            background: '#101828',
            border: '1.5px solid #FFC400',
            borderRadius: '14px',
            width: '100%',
            maxWidth: '680px',
            padding: '24px',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <TableIcon size={20} style={{ color: '#FFC400' }} />
                <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 800, color: '#FFFFFF' }}>
                  Link OneHive directly to your Google Sheet
                </h3>
              </div>
              <button 
                type="button" 
                onClick={() => setShowWebhookHelp(false)}
                style={{ background: 'transparent', border: 'none', color: '#94A3B8', fontSize: '20px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <p style={{ fontSize: '13px', color: '#CBD5E1', lineHeight: 1.5, margin: '0 0 16px 0' }}>
              Follow these 3 quick steps to have OneHive automatically append every discovered lead into your live Google Sheet in real time:
            </p>

            <ol style={{ fontSize: '12px', color: '#E2E8F0', lineHeight: 1.6, paddingLeft: '20px', margin: '0 0 16px 0' }}>
              <li>Open your Google Sheet, click <strong>Extensions → Apps Script</strong>.</li>
              <li>Paste the snippet below into the editor and click <strong>Deploy → New deployment</strong>.</li>
              <li>Select type <strong>Web app</strong>, set <em>Who has access</em> to <strong>Anyone</strong>, and click Deploy.</li>
              <li>Copy the resulting Web App URL and paste it into the <em>Google Sheets Webhook URL</em> field in OneHive!</li>
            </ol>

            <div style={{ position: 'relative', background: '#0B0F19', border: '1px solid #1E293B', borderRadius: '8px', padding: '14px' }}>
              <button
                type="button"
                onClick={copyScriptToClipboard}
                style={{
                  position: 'absolute',
                  top: '10px',
                  right: '10px',
                  background: copiedScript ? '#10B981' : '#FFC400',
                  color: '#101828',
                  border: 'none',
                  borderRadius: '4px',
                  padding: '4px 10px',
                  fontSize: '11px',
                  fontWeight: 800,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  cursor: 'pointer'
                }}
              >
                {copiedScript ? <Check size={12} /> : <Copy size={12} />}
                <span>{copiedScript ? 'Copied!' : 'Copy Script'}</span>
              </button>
              <pre style={{ margin: 0, fontSize: '11px', color: '#A7F3D0', fontFamily: 'monospace', overflowX: 'auto', maxHeight: '200px' }}>
                {GOOGLE_APPS_SCRIPT_TEMPLATE}
              </pre>
            </div>

            <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end' }}>
              <button
                type="button"
                className="btn-action-primary"
                onClick={() => setShowWebhookHelp(false)}
                style={{ padding: '8px 20px', fontSize: '13px' }}
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
