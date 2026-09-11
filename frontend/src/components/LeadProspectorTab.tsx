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

    try {
      const res = await fetch('/api/leads/prospect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          niche: niche.trim(),
          location: location.trim(),
          limit,
          webhook_url: webhookUrl.trim() || undefined
        })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to harvest business leads.');
      }

      const data = await res.json();
      setLeads(prev => {
        // Prepend new leads, avoiding duplicate IDs
        const existingIds = new Set(data.leads.map((l: LeadItem) => l.id));
        const filteredPrev = prev.filter(p => !existingIds.has(p.id));
        return [...data.leads, ...filteredPrev];
      });
    } catch (err: any) {
      setErrorMessage(err.message || 'Error occurred while discovering business leads.');
    } finally {
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

  return (
    <div className="lead-prospector-container" style={{ marginTop: '20px' }}>
      {/* Top Banner */}
      <div className="prospector-banner" style={{
        background: 'linear-gradient(135deg, rgba(255, 196, 0, 0.1) 0%, rgba(16, 24, 40, 0.7) 100%)',
        border: '1px solid rgba(255, 196, 0, 0.3)',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span style={{
                background: '#FFC400',
                color: '#101828',
                fontSize: '11px',
                fontWeight: 900,
                padding: '3px 8px',
                borderRadius: '6px'
              }}>
                AUTONOMOUS SALES PROSPECTOR
              </span>
              <span style={{ fontSize: '12px', color: '#98A2B3' }}>
                Google Maps & Local Search Discovery Engine
              </span>
            </div>
            <h2 style={{ fontSize: '22px', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
              Discover High-Value Leads & Auto-Generate 2-Page Audits
            </h2>
            <p style={{ fontSize: '13px', color: '#D0D5DD', margin: '6px 0 0 0' }}>
              Enter any business niche and location. OneHive identifies top local prospects, flags high-converting gaps (e.g. 4.8★ with No Website), links directly to Google Sheets, and generates audits in 1 click.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <a 
              href={`/api/leads/export-csv?niche=${encodeURIComponent(niche)}&location=${encodeURIComponent(location)}`}
              className="btn-action-primary"
              style={{
                background: '#101828',
                border: '1.5px solid #FFC400',
                color: '#FFC400',
                padding: '10px 16px',
                fontSize: '13px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                textDecoration: 'none'
              }}
            >
              <Download size={15} />
              <span>Download Google Sheets CSV</span>
            </a>

            <button
              type="button"
              className="btn-action-primary"
              onClick={() => setShowWebhookHelp(true)}
              style={{
                background: 'rgba(255, 255, 255, 0.06)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                color: '#FFFFFF',
                padding: '10px 14px',
                fontSize: '13px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <HelpCircle size={15} />
              <span>Link Google Sheet</span>
            </button>
          </div>
        </div>

        {/* Input Form */}
        <form onSubmit={handleHarvestLeads} style={{ marginTop: '20px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr 120px auto', gap: '12px', alignItems: 'flex-end' }}>
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: '#F1F5F9', marginBottom: '6px' }}>
                Target Business Niche
              </label>
              <input
                type="text"
                className="audit-input"
                value={niche}
                onChange={(e) => setNiche(e.target.value)}
                placeholder="e.g. Dental Clinics, Banquet Halls, Cosmetic Salons..."
                style={{ width: '100%', padding: '12px 14px', fontSize: '13px' }}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: '#F1F5F9', marginBottom: '6px' }}>
                Location / City / Suburb
              </label>
              <input
                type="text"
                className="audit-input"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Indiranagar, Bengaluru or South Extension, Delhi"
                style={{ width: '100%', padding: '12px 14px', fontSize: '13px' }}
                required
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: '#F1F5F9', marginBottom: '6px' }}>
                Lead Limit
              </label>
              <select
                className="audit-input"
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                style={{ width: '100%', padding: '12px 10px', fontSize: '13px', cursor: 'pointer' }}
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
                  height: '46px',
                  padding: '0 24px',
                  fontSize: '14px',
                  fontWeight: 800,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  whiteSpace: 'nowrap'
                }}
              >
                {isSearching ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" />
                    <span>Harvesting Leads...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    <span>Harvest Leads</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Preset Chips */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '12px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '11px', color: '#94A3B8', fontWeight: 600 }}>Quick Niches:</span>
            {NICHE_PRESETS.slice(0, 4).map(preset => (
              <button
                key={preset}
                type="button"
                onClick={() => setNiche(preset)}
                style={{
                  background: niche === preset ? 'rgba(255, 196, 0, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                  border: niche === preset ? '1px solid #FFC400' : '1px solid rgba(255, 255, 255, 0.1)',
                  color: niche === preset ? '#FFC400' : '#CBD5E1',
                  borderRadius: '16px',
                  padding: '3px 10px',
                  fontSize: '11px',
                  cursor: 'pointer'
                }}
              >
                {preset}
              </button>
            ))}

            <span style={{ fontSize: '11px', color: '#94A3B8', fontWeight: 600, marginLeft: '8px' }}>Cities:</span>
            {LOCATION_PRESETS.slice(0, 3).map(preset => (
              <button
                key={preset}
                type="button"
                onClick={() => setLocation(preset)}
                style={{
                  background: location === preset ? 'rgba(255, 196, 0, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                  border: location === preset ? '1px solid #FFC400' : '1px solid rgba(255, 255, 255, 0.1)',
                  color: location === preset ? '#FFC400' : '#CBD5E1',
                  borderRadius: '16px',
                  padding: '3px 10px',
                  fontSize: '11px',
                  cursor: 'pointer'
                }}
              >
                {preset}
              </button>
            ))}
          </div>

          {/* Optional Webhook Field */}
          <div style={{ marginTop: '14px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '12px', color: '#94A3B8' }}>Google Sheets Webhook URL (Optional):</span>
            <input
              type="url"
              className="audit-input"
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
              placeholder="https://script.google.com/macros/s/.../exec"
              style={{ flex: 1, padding: '8px 12px', fontSize: '12px' }}
            />
          </div>
        </form>
      </div>

      {/* Error Message */}
      {errorMessage && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid #EF4444',
          borderRadius: '8px',
          padding: '12px 16px',
          marginBottom: '20px',
          color: '#FCA5A5',
          fontSize: '13px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <AlertTriangle size={16} style={{ color: '#EF4444', flexShrink: 0 }} />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Pipeline Metrics Overview */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '20px' }}>
        <div style={{ background: '#101828', border: '1px solid #1E293B', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '11px', color: '#94A3B8', textTransform: 'uppercase', fontWeight: 700 }}>Total Discovered</div>
          <div style={{ fontSize: '24px', fontWeight: 900, color: '#FFFFFF', marginTop: '4px' }}>{leads.length}</div>
          <div style={{ fontSize: '11px', color: '#64748B', marginTop: '2px' }}>In prospect pipeline</div>
        </div>

        <div style={{ background: '#101828', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '11px', color: '#EF4444', textTransform: 'uppercase', fontWeight: 700 }}>No Website (High Value)</div>
          <div style={{ fontSize: '24px', fontWeight: 900, color: '#EF4444', marginTop: '4px' }}>{noWebsiteCount}</div>
          <div style={{ fontSize: '11px', color: '#FCA5A5', marginTop: '2px' }}>₹50k-1.5L website deals</div>
        </div>

        <div style={{ background: '#101828', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '11px', color: '#F59E0B', textTransform: 'uppercase', fontWeight: 700 }}>Missing WhatsApp Bridge</div>
          <div style={{ fontSize: '24px', fontWeight: 900, color: '#F59E0B', marginTop: '4px' }}>{noWhatsAppCount}</div>
          <div style={{ fontSize: '11px', color: '#FDE68A', marginTop: '2px' }}>Conversion bottleneck</div>
        </div>

        <div style={{ background: '#101828', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '10px', padding: '16px' }}>
          <div style={{ fontSize: '11px', color: '#10B981', textTransform: 'uppercase', fontWeight: 700 }}>Audited & Ready to Pitch</div>
          <div style={{ fontSize: '24px', fontWeight: 900, color: '#10B981', marginTop: '4px' }}>{auditedCount}</div>
          <div style={{ fontSize: '11px', color: '#A7F3D0', marginTop: '2px' }}>2-Page report ready</div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div style={{ display: 'flex', gap: '8px' }}>
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
                background: activeFilter === tab.key ? '#FFC400' : '#1E293B',
                color: activeFilter === tab.key ? '#101828' : '#CBD5E1',
                border: 'none',
                borderRadius: '8px',
                padding: '8px 14px',
                fontSize: '12px',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <button
          type="button"
          onClick={fetchExistingLeads}
          style={{
            background: 'transparent',
            border: '1px solid #334155',
            color: '#94A3B8',
            borderRadius: '6px',
            padding: '6px 12px',
            fontSize: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            cursor: 'pointer'
          }}
        >
          <RefreshCw size={13} />
          <span>Refresh Leads</span>
        </button>
      </div>

      {/* Leads Table / Cards */}
      {filteredLeads.length === 0 ? (
        <div style={{
          background: '#101828',
          border: '1px dashed #334155',
          borderRadius: '12px',
          padding: '48px',
          textAlign: 'center',
          color: '#94A3B8'
        }}>
          <Building2 size={36} style={{ margin: '0 auto 12px auto', color: '#475569' }} />
          <h3 style={{ fontSize: '16px', color: '#F1F5F9', margin: '0 0 6px 0' }}>No Prospects in Current Filter</h3>
          <p style={{ fontSize: '13px', margin: 0 }}>
            Enter a niche and city above to discover high-value business leads automatically.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {filteredLeads.map(lead => {
            const isAudited = lead.status === 'AUDITED';
            const isAuditing = auditingLeadId === lead.id;

            return (
              <div 
                key={lead.id}
                style={{
                  background: '#101828',
                  border: isAudited ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid #1E293B',
                  borderRadius: '10px',
                  padding: '18px 20px',
                  display: 'grid',
                  gridTemplateColumns: '2fr 1.5fr 2fr 1.5fr',
                  gap: '16px',
                  alignItems: 'center'
                }}
              >
                {/* Col 1: Business Identity */}
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                    <h3 style={{ fontSize: '15px', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
                      {lead.business_name}
                    </h3>
                    {lead.maps_url && (
                      <a href={lead.maps_url} target="_blank" rel="noopener noreferrer" style={{ color: '#94A3B8' }} title="View on Google Maps">
                        <ExternalLink size={13} />
                      </a>
                    )}
                  </div>
                  <div style={{ fontSize: '12px', color: '#94A3B8', display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span>{lead.category}</span>
                    <span>•</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#FFC400', fontWeight: 700 }}>
                      <Star size={12} fill="#FFC400" />
                      {lead.rating ? `${lead.rating}★` : '4.5★'} ({lead.review_count || 40} reviews)
                    </span>
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748B', marginTop: '4px' }}>
                    <MapPin size={11} style={{ display: 'inline', marginRight: '4px' }} />
                    {lead.location}
                  </div>
                </div>

                {/* Col 2: Digital Asset Status */}
                <div>
                  <div style={{ marginBottom: '6px' }}>
                    {lead.website ? (
                      <a 
                        href={lead.website} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ fontSize: '12px', color: '#38BDF8', display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none' }}
                      >
                        <Globe size={13} />
                        <span>{lead.website.replace('https://', '').replace('http://', '').split('/')[0]}</span>
                      </a>
                    ) : (
                      <span style={{
                        background: 'rgba(239, 68, 68, 0.15)',
                        border: '1px solid rgba(239, 68, 68, 0.4)',
                        color: '#EF4444',
                        fontSize: '11px',
                        fontWeight: 800,
                        padding: '2px 8px',
                        borderRadius: '4px'
                      }}>
                        🔴 NO WEBSITE DETECTED
                      </span>
                    )}
                  </div>

                  <div style={{ fontSize: '12px', color: '#CBD5E1', display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Phone size={12} style={{ color: '#94A3B8' }} />
                    <span>{lead.phone || 'Available via Maps'}</span>
                  </div>
                </div>

                {/* Col 3: Opportunity Diagnosis */}
                <div>
                  <div style={{ marginBottom: '4px' }}>
                    {lead.opportunity_flag === 'NO_WEBSITE' && (
                      <span style={{
                        background: 'rgba(239, 68, 68, 0.2)',
                        color: '#FCA5A5',
                        border: '1px solid rgba(239, 68, 68, 0.5)',
                        fontSize: '10px',
                        fontWeight: 900,
                        padding: '2px 8px',
                        borderRadius: '4px',
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
                        fontSize: '10px',
                        fontWeight: 900,
                        padding: '2px 8px',
                        borderRadius: '4px',
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
                        fontSize: '10px',
                        fontWeight: 900,
                        padding: '2px 8px',
                        borderRadius: '4px',
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
                        fontSize: '10px',
                        fontWeight: 900,
                        padding: '2px 8px',
                        borderRadius: '4px',
                        letterSpacing: '0.4px'
                      }}>
                        DIGITAL GROWTH
                      </span>
                    )}
                  </div>
                  <p style={{ fontSize: '11px', color: '#94A3B8', margin: 0, lineHeight: 1.4 }}>
                    {lead.opportunity_summary}
                  </p>
                </div>

                {/* Col 4: 1-Click Action Hub */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignItems: 'flex-end' }}>
                  {/* Quick Track & Delete Actions */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <button
                      type="button"
                      onClick={() => handleToggleFinalize(lead)}
                      title={lead.is_finalized ? "In Lead Tracker" : "Move to Lead Tracker"}
                      style={{
                        background: lead.is_finalized ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.06)',
                        border: lead.is_finalized ? '1px solid #38BDF8' : '1px solid rgba(255, 255, 255, 0.15)',
                        color: lead.is_finalized ? '#38BDF8' : '#CBD5E1',
                        borderRadius: '4px',
                        padding: '3px 8px',
                        fontSize: '11px',
                        fontWeight: 700,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      <BookmarkCheck size={11} />
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
                        borderRadius: '4px',
                        padding: '3px 8px',
                        fontSize: '11px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        cursor: 'pointer'
                      }}
                    >
                      <Trash2 size={11} />
                      <span>Delete</span>
                    </button>
                  </div>
                  {isAudited ? (
                    <>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{
                          background: 'rgba(16, 185, 129, 0.15)',
                          color: '#10B981',
                          border: '1px solid rgba(16, 185, 129, 0.4)',
                          fontSize: '11px',
                          fontWeight: 800,
                          padding: '2px 8px',
                          borderRadius: '6px'
                        }}>
                          Score: {lead.audit_score}/100
                        </span>
                        <button
                          type="button"
                          onClick={() => onViewAuditReport(lead.audit_id!)}
                          style={{
                            background: '#FFC400',
                            color: '#101828',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '6px 12px',
                            fontSize: '12px',
                            fontWeight: 800,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px',
                            cursor: 'pointer'
                          }}
                        >
                          <FileText size={13} />
                          <span>View 2-Page Report</span>
                        </button>
                      </div>

                      <div style={{ display: 'flex', gap: '6px' }}>
                        {lead.whatsapp_pitch_link && (
                          <a
                            href={lead.whatsapp_pitch_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              background: '#25D366',
                              color: '#FFFFFF',
                              border: 'none',
                              borderRadius: '4px',
                              padding: '4px 10px',
                              fontSize: '11px',
                              fontWeight: 700,
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px',
                              textDecoration: 'none'
                            }}
                          >
                            <Send size={11} />
                            <span>WhatsApp Pitch</span>
                          </a>
                        )}
                        <a
                          href={`/api/audits/${lead.audit_id}/sales-pack`}
                          style={{
                            background: '#1E293B',
                            color: '#CBD5E1',
                            border: '1px solid #334155',
                            borderRadius: '4px',
                            padding: '4px 8px',
                            fontSize: '11px',
                            textDecoration: 'none'
                          }}
                        >
                          Sales Pack
                        </a>
                      </div>
                    </>
                  ) : (
                    <>
                      <button
                        type="button"
                        onClick={() => handleOneClickAudit(lead)}
                        disabled={isAuditing}
                        style={{
                          background: 'linear-gradient(135deg, #FFC400 0%, #E5A800 100%)',
                          color: '#101828',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '8px 14px',
                          fontSize: '12px',
                          fontWeight: 800,
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          cursor: isAuditing ? 'not-allowed' : 'pointer',
                          boxShadow: '0 2px 8px rgba(255, 196, 0, 0.2)'
                        }}
                      >
                        {isAuditing ? (
                          <>
                            <RefreshCw size={13} className="animate-spin" />
                            <span>Analyzing & Generating...</span>
                          </>
                        ) : (
                          <>
                            <Zap size={13} />
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
                            fontSize: '11px',
                            fontWeight: 700,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px',
                            textDecoration: 'none'
                          }}
                        >
                          <Send size={10} />
                          <span>Pre-fill WhatsApp Pitch</span>
                        </a>
                      )}
                    </>
                  )}
                </div>
              </div>
            );
          })}
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
