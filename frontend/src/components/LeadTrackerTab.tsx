'use client';

import React, { useState, useEffect } from 'react';
import { 
  ClipboardList, CheckCircle2, AlertTriangle, Clock, Calendar, 
  Send, Phone, Globe, ExternalLink, FileText, Trash2, Edit3, 
  Save, Star, RefreshCw, Check, Filter, MessageSquare, ChevronDown
} from 'lucide-react';
import { LeadItem, PipelineStage } from '../types/lead';

interface LeadTrackerTabProps {
  onViewAuditReport: (auditId: string) => void;
}

const STAGES: { key: PipelineStage; label: string; color: string; bg: string }[] = [
  { key: 'PITCH_READY', label: 'Pitch Ready', color: '#38BDF8', bg: 'rgba(56, 189, 248, 0.15)' },
  { key: 'CONTACTED', label: 'Report Sent / Contacted', color: '#F59E0B', bg: 'rgba(245, 158, 11, 0.15)' },
  { key: 'FOLLOW_UP', label: 'Follow-Up Due', color: '#EC4899', bg: 'rgba(236, 72, 153, 0.15)' },
  { key: 'CALL_SCHEDULED', label: 'Demo / Call Scheduled', color: '#8B5CF6', bg: 'rgba(139, 92, 246, 0.15)' },
  { key: 'WON', label: 'Deal Closed / Won 🎉', color: '#10B981', bg: 'rgba(16, 185, 129, 0.15)' },
  { key: 'LOST', label: 'Archived / Lost', color: '#64748B', bg: 'rgba(100, 116, 139, 0.15)' }
];

export const LeadTrackerTab: React.FC<LeadTrackerTabProps> = ({ onViewAuditReport }) => {
  const [leads, setLeads] = useState<LeadItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeStageFilter, setActiveStageFilter] = useState<string>('ALL');
  const [editingNotesId, setEditingNotesId] = useState<string | null>(null);
  const [noteDraft, setNoteDraft] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchTrackedLeads();
  }, []);

  const fetchTrackedLeads = async () => {
    setIsLoading(true);
    try {
      // Fetch finalized leads (or all leads if none finalized yet)
      const res = await fetch('/api/leads');
      if (res.ok) {
        const data: LeadItem[] = await res.json();
        // Priority to finalized leads, or audited leads
        const tracked = data.filter(l => l.is_finalized || l.status === 'AUDITED');
        setLeads(tracked.length > 0 ? tracked : data);
      }
    } catch (err) {
      console.warn('Could not load tracked leads:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateStage = async (leadId: string, newStage: PipelineStage) => {
    try {
      const res = await fetch(`/api/leads/${leadId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          stage: newStage,
          last_contacted: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
        })
      });

      if (res.ok) {
        const updated = await res.json();
        setLeads(prev => prev.map(l => l.id === leadId ? updated : l));
      }
    } catch (err) {
      console.error('Failed to update stage:', err);
    }
  };

  const handleSaveNotes = async (leadId: string) => {
    try {
      const res = await fetch(`/api/leads/${leadId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes: noteDraft })
      });

      if (res.ok) {
        const updated = await res.json();
        setLeads(prev => prev.map(l => l.id === leadId ? updated : l));
        setEditingNotesId(null);
      }
    } catch (err) {
      console.error('Failed to save notes:', err);
    }
  };

  const handleSetFollowup = async (leadId: string, followupStr: string) => {
    try {
      const res = await fetch(`/api/leads/${leadId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ next_followup: followupStr })
      });

      if (res.ok) {
        const updated = await res.json();
        setLeads(prev => prev.map(l => l.id === leadId ? updated : l));
      }
    } catch (err) {
      console.error('Failed to set followup:', err);
    }
  };

  const handleDeleteLead = async (leadId: string) => {
    if (!confirm('Are you sure you want to delete this lead from the pipeline?')) return;

    try {
      const res = await fetch(`/api/leads/${leadId}`, {
        method: 'DELETE'
      });

      if (res.ok) {
        setLeads(prev => prev.filter(l => l.id !== leadId));
      } else {
        throw new Error('Failed to delete lead.');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Error deleting lead.');
    }
  };

  const getFollowupWhatsAppLink = (lead: LeadItem, stage: PipelineStage) => {
    const cleanDigits = "".replace(/[^0-9]/g, '');
    const phoneDigits = lead.phone ? lead.phone.replace(/[^0-9]/g, '') : '';
    if (phoneDigits.length < 10) return null;

    let msg = '';
    if (stage === 'CONTACTED' || stage === 'FOLLOW_UP') {
      msg = `Hi ${lead.business_name}, following up on the 2-Page Digital Presence Intelligence Report we shared earlier. We noticed a couple of immediate opportunities to capture high-intent inquiries in ${lead.location}. Did you get a chance to review the report?`;
    } else if (stage === 'CALL_SCHEDULED') {
      msg = `Hi ${lead.business_name}, confirming our quick 10-minute strategy walkthrough for ${lead.location}. Looking forward to speaking!`;
    } else {
      msg = `Hi ${lead.business_name}, we prepared a 2-Page Digital Presence Audit for your business in ${lead.location}. Would you like me to share it here?`;
    }

    return `https://wa.me/${phoneDigits}?text=${encodeURIComponent(msg)}`;
  };

  // Filtered list
  const filteredLeads = leads.filter(l => {
    if (activeStageFilter === 'ALL') return true;
    return (l.stage || 'PITCH_READY') === activeStageFilter;
  });

  // Metrics
  const stageCounts = STAGES.reduce((acc, stage) => {
    acc[stage.key] = leads.filter(l => (l.stage || 'PITCH_READY') === stage.key).length;
    return acc;
  }, {} as Record<PipelineStage, number>);

  return (
    <div className="lead-tracker-container" style={{ marginTop: '20px' }}>
      {/* Top Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.1) 0%, rgba(16, 24, 40, 0.7) 100%)',
        border: '1px solid rgba(56, 189, 248, 0.3)',
        borderRadius: '12px',
        padding: '24px',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span style={{
                background: '#38BDF8',
                color: '#101828',
                fontSize: '11px',
                fontWeight: 900,
                padding: '3px 8px',
                borderRadius: '6px'
              }}>
                SALES CRM & OUTREACH TRACKER
              </span>
              <span style={{ fontSize: '12px', color: '#98A2B3' }}>
                Pipeline Stage & Follow-Up Management
              </span>
            </div>
            <h2 style={{ fontSize: '22px', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
              Lead Follow-Up & Deal Tracker
            </h2>
            <p style={{ fontSize: '13px', color: '#D0D5DD', margin: '6px 0 0 0' }}>
              Track finalized prospects across outreach stages: Pitch Ready, Report Sent, Follow-Up Due, Demo Scheduled, and Deals Closed.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              type="button"
              onClick={fetchTrackedLeads}
              style={{
                background: '#101828',
                border: '1px solid #38BDF8',
                color: '#38BDF8',
                padding: '8px 16px',
                fontSize: '12px',
                fontWeight: 700,
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                cursor: 'pointer'
              }}
            >
              <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
              <span>Refresh Tracker</span>
            </button>
          </div>
        </div>
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
          <AlertTriangle size={16} style={{ color: '#EF4444' }} />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Pipeline Stage Funnel Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '10px', marginBottom: '24px' }}>
        {STAGES.map(stage => {
          const count = stageCounts[stage.key] || 0;
          const isActive = activeStageFilter === stage.key;

          return (
            <div
              key={stage.key}
              onClick={() => setActiveStageFilter(isActive ? 'ALL' : stage.key)}
              style={{
                background: isActive ? stage.bg : '#101828',
                border: isActive ? `1.5px solid ${stage.color}` : '1px solid #1E293B',
                borderRadius: '10px',
                padding: '14px',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <div style={{ fontSize: '10px', fontWeight: 800, color: stage.color, textTransform: 'uppercase' }}>
                {stage.label.split('/')[0]}
              </div>
              <div style={{ fontSize: '22px', fontWeight: 900, color: '#FFFFFF', marginTop: '4px' }}>
                {count}
              </div>
              <div style={{ fontSize: '10px', color: '#64748B', marginTop: '2px' }}>
                {isActive ? 'Filtered' : 'Click to filter'}
              </div>
            </div>
          );
        })}
      </div>

      {/* Filter toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Filter size={14} style={{ color: '#94A3B8' }} />
          <span style={{ fontSize: '13px', color: '#F1F5F9', fontWeight: 700 }}>
            {activeStageFilter === 'ALL' ? `All Active Leads (${leads.length})` : `Filtered Stage: ${activeStageFilter} (${filteredLeads.length})`}
          </span>
          {activeStageFilter !== 'ALL' && (
            <button
              type="button"
              onClick={() => setActiveStageFilter('ALL')}
              style={{
                background: 'rgba(255, 255, 255, 0.08)',
                border: 'none',
                color: '#CBD5E1',
                borderRadius: '4px',
                padding: '2px 8px',
                fontSize: '11px',
                cursor: 'pointer'
              }}
            >
              Clear Filter
            </button>
          )}
        </div>
      </div>

      {/* Tracked Leads List */}
      {filteredLeads.length === 0 ? (
        <div style={{
          background: '#101828',
          border: '1px dashed #334155',
          borderRadius: '12px',
          padding: '48px',
          textAlign: 'center',
          color: '#94A3B8'
        }}>
          <ClipboardList size={36} style={{ margin: '0 auto 12px auto', color: '#475569' }} />
          <h3 style={{ fontSize: '16px', color: '#F1F5F9', margin: '0 0 6px 0' }}>No Leads in this Stage</h3>
          <p style={{ fontSize: '13px', margin: 0 }}>
            Move finalized leads from the <strong>Lead Prospector & Pipeline Hub</strong> tab to track and manage follow-ups here.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {filteredLeads.map(lead => {
            const currentStage = (lead.stage || 'PITCH_READY') as PipelineStage;
            const currentStageObj = STAGES.find(s => s.key === currentStage) || STAGES[0];
            const isEditingNotes = editingNotesId === lead.id;
            const waFollowupLink = getFollowupWhatsAppLink(lead, currentStage);

            return (
              <div 
                key={lead.id}
                style={{
                  background: '#101828',
                  border: '1px solid #1E293B',
                  borderRadius: '12px',
                  padding: '20px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '14px'
                }}
              >
                {/* Header Row: Business Info + Stage Selector + Delete */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <h3 style={{ fontSize: '16px', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
                          {lead.business_name}
                        </h3>
                        {lead.maps_url && (
                          <a href={lead.maps_url} target="_blank" rel="noopener noreferrer" style={{ color: '#94A3B8' }}>
                            <ExternalLink size={13} />
                          </a>
                        )}
                        {lead.audit_score && (
                          <span style={{
                            background: 'rgba(16, 185, 129, 0.15)',
                            color: '#10B981',
                            border: '1px solid rgba(16, 185, 129, 0.4)',
                            fontSize: '11px',
                            fontWeight: 800,
                            padding: '2px 8px',
                            borderRadius: '4px'
                          }}>
                            Score: {lead.audit_score}/100
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '12px', color: '#94A3B8', marginTop: '3px' }}>
                        {lead.category} • {lead.location} • {lead.phone || 'No phone'}
                      </div>
                    </div>
                  </div>

                  {/* Stage Dropdown + Delete */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ fontSize: '11px', color: '#64748B', fontWeight: 700 }}>STAGE:</span>
                      <select
                        value={currentStage}
                        onChange={(e) => handleUpdateStage(lead.id, e.target.value as PipelineStage)}
                        style={{
                          background: currentStageObj.bg,
                          color: currentStageObj.color,
                          border: `1px solid ${currentStageObj.color}`,
                          borderRadius: '8px',
                          padding: '6px 10px',
                          fontSize: '12px',
                          fontWeight: 800,
                          cursor: 'pointer'
                        }}
                      >
                        {STAGES.map(s => (
                          <option key={s.key} value={s.key} style={{ background: '#101828', color: '#FFFFFF' }}>
                            {s.label}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Delete Lead Button */}
                    <button
                      type="button"
                      onClick={() => handleDeleteLead(lead.id)}
                      title="Delete lead from tracker"
                      style={{
                        background: 'rgba(239, 68, 68, 0.1)',
                        border: '1px solid rgba(239, 68, 68, 0.3)',
                        color: '#EF4444',
                        borderRadius: '6px',
                        padding: '6px 10px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        fontSize: '11px'
                      }}
                    >
                      <Trash2 size={13} />
                      <span>Delete</span>
                    </button>
                  </div>
                </div>

                {/* Middle Row: Follow-Up Schedule & Notes */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1.2fr 2fr',
                  gap: '14px',
                  background: '#0B0F19',
                  borderRadius: '8px',
                  padding: '12px 16px',
                  border: '1px solid #1E293B'
                }}>
                  {/* Follow-up reminder */}
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                      <Clock size={13} style={{ color: '#FFC400' }} />
                      <span style={{ fontSize: '11px', fontWeight: 700, color: '#CBD5E1', textTransform: 'uppercase' }}>
                        Next Follow-Up
                      </span>
                    </div>

                    <div style={{ fontSize: '12px', color: lead.next_followup ? '#38BDF8' : '#64748B', marginBottom: '6px' }}>
                      {lead.next_followup ? `Scheduled: ${lead.next_followup}` : 'No follow-up date set'}
                    </div>

                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                      {['Tomorrow', 'In 3 Days', 'Next Monday'].map(timePreset => (
                        <button
                          key={timePreset}
                          type="button"
                          onClick={() => handleSetFollowup(lead.id, timePreset)}
                          style={{
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.15)',
                            color: '#94A3B8',
                            borderRadius: '4px',
                            padding: '3px 8px',
                            fontSize: '10px',
                            cursor: 'pointer'
                          }}
                        >
                          +{timePreset}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Notes / Call Log */}
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontSize: '11px', fontWeight: 700, color: '#CBD5E1', textTransform: 'uppercase' }}>
                        Consultative Notes & Objections
                      </span>
                      {!isEditingNotes && (
                        <button
                          type="button"
                          onClick={() => {
                            setEditingNotesId(lead.id);
                            setNoteDraft(lead.notes || '');
                          }}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            color: '#FFC400',
                            fontSize: '11px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '3px'
                          }}
                        >
                          <Edit3 size={11} />
                          <span>{lead.notes ? 'Edit Note' : 'Add Note'}</span>
                        </button>
                      )}
                    </div>

                    {isEditingNotes ? (
                      <div>
                        <textarea
                          className="audit-input"
                          value={noteDraft}
                          onChange={(e) => setNoteDraft(e.target.value)}
                          placeholder="e.g. Spoke with Dr. Sharma. Liked the 2-page report, wants to review pricing on Thursday..."
                          style={{ width: '100%', height: '60px', padding: '6px 10px', fontSize: '12px' }}
                        />
                        <div style={{ display: 'flex', gap: '6px', marginTop: '6px', justifyContent: 'flex-end' }}>
                          <button
                            type="button"
                            onClick={() => setEditingNotesId(null)}
                            style={{ background: 'transparent', border: 'none', color: '#94A3B8', fontSize: '11px', cursor: 'pointer' }}
                          >
                            Cancel
                          </button>
                          <button
                            type="button"
                            onClick={() => handleSaveNotes(lead.id)}
                            style={{
                              background: '#FFC400',
                              color: '#101828',
                              border: 'none',
                              borderRadius: '4px',
                              padding: '4px 10px',
                              fontSize: '11px',
                              fontWeight: 700,
                              cursor: 'pointer'
                            }}
                          >
                            Save Note
                          </button>
                        </div>
                      </div>
                    ) : (
                      <p style={{ fontSize: '12px', color: lead.notes ? '#E2E8F0' : '#475569', margin: 0, fontStyle: lead.notes ? 'normal' : 'italic' }}>
                        {lead.notes || 'No notes logged yet. Click to record call notes or prospect objections.'}
                      </p>
                    )}
                  </div>
                </div>

                {/* Bottom Row: Action Hub (View Report, WhatsApp Outreach, Sales Pack) */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
                  <div style={{ fontSize: '11px', color: '#64748B' }}>
                    {lead.opportunity_summary}
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    {lead.audit_id && (
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
                    )}

                    {waFollowupLink && (
                      <a
                        href={waFollowupLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          background: '#25D366',
                          color: '#FFFFFF',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '6px 12px',
                          fontSize: '12px',
                          fontWeight: 700,
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          textDecoration: 'none'
                        }}
                      >
                        <Send size={12} />
                        <span>Send WhatsApp Follow-Up</span>
                      </a>
                    )}

                    {lead.audit_id && (
                      <a
                        href={`/api/audits/${lead.audit_id}/sales-pack`}
                        style={{
                          background: '#1E293B',
                          color: '#CBD5E1',
                          border: '1px solid #334155',
                          borderRadius: '6px',
                          padding: '6px 10px',
                          fontSize: '12px',
                          textDecoration: 'none'
                        }}
                      >
                        Sales Pack
                      </a>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
