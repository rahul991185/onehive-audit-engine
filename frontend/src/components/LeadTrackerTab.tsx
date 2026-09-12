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
  const [selectedLeadIds, setSelectedLeadIds] = useState<Set<string>>(new Set());
  const [isBulkDeleting, setIsBulkDeleting] = useState(false);
  const [isBulkUpdatingStage, setIsBulkUpdatingStage] = useState(false);

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
        setSelectedLeadIds(prev => {
          const next = new Set(prev);
          next.delete(leadId);
          return next;
        });
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

  // Multiselect logic
  const handleToggleSelectLead = (leadId: string) => {
    setSelectedLeadIds(prev => {
      const next = new Set(prev);
      if (next.has(leadId)) next.delete(leadId);
      else next.add(leadId);
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
    if (!confirm(`Are you sure you want to permanently delete ${count} selected lead${count > 1 ? 's' : ''} from the tracker?`)) return;

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

  const handleBulkStageChange = async (newStage: PipelineStage) => {
    if (selectedLeadIds.size === 0) return;
    setIsBulkUpdatingStage(true);
    try {
      const idsToUpdate = Array.from(selectedLeadIds);
      const res = await fetch('/api/leads/bulk-stage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lead_ids: idsToUpdate, stage: newStage })
      });
      if (!res.ok) throw new Error('Failed to update stage for selected leads.');

      const idSet = new Set(idsToUpdate);
      setLeads(prev => prev.map(l => idSet.has(l.id) ? { ...l, stage: newStage } : l));
      setSelectedLeadIds(new Set());
    } catch (err: any) {
      setErrorMessage(err.message || 'Error updating stage for selected leads.');
    } finally {
      setIsBulkUpdatingStage(false);
    }
  };

  // Metrics
  const stageCounts = STAGES.reduce((acc, stage) => {
    acc[stage.key] = leads.filter(l => (l.stage || 'PITCH_READY') === stage.key).length;
    return acc;
  }, {} as Record<PipelineStage, number>);

  return (
    <div className="lead-tracker-container" style={{ marginTop: '24px' }}>
      {/* Top Banner */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(56, 189, 248, 0.08) 0%, rgba(13, 18, 31, 0.95) 100%)',
        border: '1px solid rgba(56, 189, 248, 0.25)',
        borderRadius: '16px',
        padding: '32px',
        marginBottom: '28px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span style={{
                background: '#38BDF8',
                color: '#070A12',
                fontSize: '11px',
                fontWeight: 900,
                padding: '4px 10px',
                borderRadius: '6px',
                letterSpacing: '0.4px'
              }}>
                SALES CRM & OUTREACH PIPELINE
              </span>
              <span style={{ fontSize: '13px', color: '#94A3B8' }}>
                Pipeline Stage Transitions & Direct WhatsApp Follow-Ups
              </span>
            </div>
            <h2 style={{ fontSize: '24px', fontWeight: 800, color: '#FFFFFF', margin: 0, letterSpacing: '-0.3px' }}>
              Lead Follow-Up & Deal Tracker
            </h2>
            <p style={{ fontSize: '14px', color: '#CBD5E1', margin: '8px 0 0 0', lineHeight: 1.6, maxWidth: '850px' }}>
              Track finalized prospects through the sales cycle: Pitch Ready, Report Sent, Follow-Up Due, Demo Scheduled, and Closed Deals.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              type="button"
              onClick={fetchTrackedLeads}
              style={{
                background: 'rgba(19, 27, 45, 0.8)',
                border: '1px solid #38BDF8',
                color: '#38BDF8',
                padding: '12px 20px',
                fontSize: '13px',
                fontWeight: 700,
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                cursor: 'pointer',
                boxShadow: '0 4px 14px rgba(56, 189, 248, 0.15)',
                transition: 'all 0.15s ease'
              }}
            >
              <RefreshCw size={15} className={isLoading ? 'animate-spin' : ''} />
              <span>Refresh Pipeline</span>
            </button>
          </div>
        </div>
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

      {/* Pipeline Stage Funnel Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(190px, 1fr))',
        gap: '14px',
        marginBottom: '28px'
      }}>
        {STAGES.map(stage => {
          const count = stageCounts[stage.key] || 0;
          const isActive = activeStageFilter === stage.key;

          return (
            <div
              key={stage.key}
              onClick={() => setActiveStageFilter(isActive ? 'ALL' : stage.key)}
              style={{
                background: isActive ? stage.bg : 'linear-gradient(180deg, rgba(19, 27, 45, 0.85) 0%, rgba(13, 18, 31, 0.95) 100%)',
                border: isActive ? `2px solid ${stage.color}` : '1px solid rgba(255, 255, 255, 0.08)',
                borderRadius: '14px',
                padding: '18px 20px',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                boxShadow: isActive ? `0 0 20px ${stage.color}25` : '0 4px 14px rgba(0, 0, 0, 0.25)',
                transform: isActive ? 'translateY(-2px)' : 'none'
              }}
            >
              <div style={{ fontSize: '11px', fontWeight: 800, color: stage.color, textTransform: 'uppercase', letterSpacing: '0.4px' }}>
                {stage.label.split('/')[0]}
              </div>
              <div style={{ fontSize: '28px', fontWeight: 900, color: '#FFFFFF', margin: '6px 0 2px 0' }}>
                {count}
              </div>
              <div style={{ fontSize: '11px', color: isActive ? stage.color : '#64748B', fontWeight: isActive ? 700 : 400 }}>
                {isActive ? '● Active Filter' : 'Click to filter'}
              </div>
            </div>
          );
        })}
      </div>

      {/* Filter Toolbar & Selection Controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Filter size={15} style={{ color: '#94A3B8' }} />
          <span style={{ fontSize: '14px', color: '#F1F5F9', fontWeight: 700 }}>
            {activeStageFilter === 'ALL' ? `All Active Pipeline Leads (${leads.length})` : `Filtered Stage: ${activeStageFilter} (${filteredLeads.length})`}
          </span>
          {activeStageFilter !== 'ALL' && (
            <button
              type="button"
              onClick={() => setActiveStageFilter('ALL')}
              style={{
                background: 'rgba(255, 255, 255, 0.08)',
                border: 'none',
                color: '#CBD5E1',
                borderRadius: '6px',
                padding: '4px 10px',
                fontSize: '12px',
                cursor: 'pointer',
                fontWeight: 600
              }}
            >
              Clear Filter
            </button>
          )}
        </div>

        {/* Select All Checkbox */}
        {filteredLeads.length > 0 && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(255, 255, 255, 0.04)', padding: '8px 14px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
            <input
              type="checkbox"
              id="selectAllTrackedLeads"
              className="onehive-checkbox"
              checked={isAllSelected}
              ref={input => {
                if (input) input.indeterminate = isSomeSelected;
              }}
              onChange={handleToggleSelectAll}
            />
            <label htmlFor="selectAllTrackedLeads" style={{ fontSize: '13px', fontWeight: 700, color: '#E2E8F0', cursor: 'pointer', userSelect: 'none' }}>
              Select All ({filteredLeads.length})
            </label>
          </div>
        )}
      </div>

      {/* Tracked Leads List */}
      {filteredLeads.length === 0 ? (
        <div style={{
          background: 'rgba(19, 27, 45, 0.6)',
          border: '1px dashed rgba(255, 255, 255, 0.15)',
          borderRadius: '16px',
          padding: '64px 32px',
          textAlign: 'center',
          color: '#94A3B8'
        }}>
          <ClipboardList size={44} style={{ margin: '0 auto 16px auto', color: '#475569' }} />
          <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#F1F5F9', margin: '0 0 8px 0' }}>No Leads in this Stage</h3>
          <p style={{ fontSize: '14px', margin: 0, color: '#94A3B8' }}>
            Move finalized leads from the <strong>Lead Prospector & Pipeline Hub</strong> tab to track and manage follow-ups here.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
          {filteredLeads.map(lead => {
            const currentStage = (lead.stage || 'PITCH_READY') as PipelineStage;
            const currentStageObj = STAGES.find(s => s.key === currentStage) || STAGES[0];
            const isEditingNotes = editingNotesId === lead.id;
            const waFollowupLink = getFollowupWhatsAppLink(lead, currentStage);
            const isSelected = selectedLeadIds.has(lead.id);

            return (
              <div 
                key={lead.id}
                className={`spacious-card ${isSelected ? 'is-selected' : ''}`}
                style={{
                  border: isSelected ? '1.5px solid rgba(255, 184, 0, 0.6)' : '1px solid rgba(255, 255, 255, 0.08)',
                  borderRadius: '16px',
                  padding: '24px 28px',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '18px'
                }}
              >
                {/* Header Row: Checkbox + Business Info + Stage Selector + Delete */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <input
                      type="checkbox"
                      className="onehive-checkbox"
                      checked={isSelected}
                      onChange={() => handleToggleSelectLead(lead.id)}
                      aria-label={`Select lead ${lead.business_name}`}
                    />

                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                        <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#FFFFFF', margin: 0 }}>
                          {lead.business_name}
                        </h3>
                        {lead.maps_url && (
                          <a href={lead.maps_url} target="_blank" rel="noopener noreferrer" style={{ color: '#94A3B8', display: 'flex', alignItems: 'center' }}>
                            <ExternalLink size={14} />
                          </a>
                        )}
                        {lead.audit_score && (
                          <span style={{
                            background: 'rgba(16, 185, 129, 0.15)',
                            color: '#10B981',
                            border: '1px solid rgba(16, 185, 129, 0.4)',
                            fontSize: '12px',
                            fontWeight: 800,
                            padding: '3px 10px',
                            borderRadius: '6px'
                          }}>
                            Audit Score: {lead.audit_score}/100
                          </span>
                        )}
                      </div>
                      <div style={{ fontSize: '13px', color: '#94A3B8', marginTop: '4px' }}>
                        <span style={{ color: '#E2E8F0', fontWeight: 600 }}>{lead.category}</span> • <span>{lead.location}</span> • <span>{lead.phone || 'No phone recorded'}</span>
                      </div>
                    </div>
                  </div>

                  {/* Stage Dropdown + Delete */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 800, letterSpacing: '0.4px' }}>STAGE:</span>
                      <select
                        value={currentStage}
                        onChange={(e) => handleUpdateStage(lead.id, e.target.value as PipelineStage)}
                        style={{
                          background: currentStageObj.bg,
                          color: currentStageObj.color,
                          border: `1.5px solid ${currentStageObj.color}`,
                          borderRadius: '8px',
                          padding: '8px 14px',
                          fontSize: '13px',
                          fontWeight: 800,
                          cursor: 'pointer',
                          outline: 'none'
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
                        borderRadius: '8px',
                        padding: '8px 12px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontSize: '12px',
                        fontWeight: 700,
                        transition: 'all 0.15s ease'
                      }}
                    >
                      <Trash2 size={14} />
                      <span>Delete</span>
                    </button>
                  </div>
                </div>

                {/* Middle Row: Follow-Up Schedule & Notes */}
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: '1.2fr 2fr',
                  gap: '20px',
                  background: 'rgba(11, 15, 25, 0.7)',
                  borderRadius: '12px',
                  padding: '18px 22px',
                  border: '1px solid rgba(255, 255, 255, 0.06)'
                }}>
                  {/* Follow-up reminder */}
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <Clock size={15} style={{ color: '#FFB800' }} />
                      <span style={{ fontSize: '12px', fontWeight: 800, color: '#E2E8F0', textTransform: 'uppercase', letterSpacing: '0.4px' }}>
                        Next Follow-Up
                      </span>
                    </div>

                    <div style={{ fontSize: '14px', fontWeight: 600, color: lead.next_followup ? '#38BDF8' : '#64748B', marginBottom: '10px' }}>
                      {lead.next_followup ? `Scheduled: ${lead.next_followup}` : 'No follow-up date set'}
                    </div>

                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                      {['Tomorrow', 'In 3 Days', 'Next Monday'].map(timePreset => (
                        <button
                          key={timePreset}
                          type="button"
                          onClick={() => handleSetFollowup(lead.id, timePreset)}
                          style={{
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.15)',
                            color: '#CBD5E1',
                            borderRadius: '6px',
                            padding: '6px 12px',
                            fontSize: '12px',
                            fontWeight: 600,
                            cursor: 'pointer',
                            transition: 'all 0.15s ease'
                          }}
                        >
                          +{timePreset}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Notes / Call Log */}
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <span style={{ fontSize: '12px', fontWeight: 800, color: '#E2E8F0', textTransform: 'uppercase', letterSpacing: '0.4px' }}>
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
                            color: '#FFB800',
                            fontSize: '12px',
                            fontWeight: 700,
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '4px'
                          }}
                        >
                          <Edit3 size={13} />
                          <span>{lead.notes ? 'Edit Note' : '+ Add Note'}</span>
                        </button>
                      )}
                    </div>

                    {isEditingNotes ? (
                      <div>
                        <textarea
                          className="audit-input"
                          value={noteDraft}
                          onChange={(e) => setNoteDraft(e.target.value)}
                          placeholder="e.g. Spoke with Dr. Sharma. Reviewed the 2-page report, interested in the website concept for Thursday walkthrough..."
                          style={{ width: '100%', height: '75px', padding: '10px 12px', fontSize: '13px', borderRadius: '8px' }}
                        />
                        <div style={{ display: 'flex', gap: '8px', marginTop: '8px', justifyContent: 'flex-end' }}>
                          <button
                            type="button"
                            onClick={() => setEditingNotesId(null)}
                            style={{ background: 'transparent', border: 'none', color: '#94A3B8', fontSize: '12px', cursor: 'pointer', padding: '4px 10px' }}
                          >
                            Cancel
                          </button>
                          <button
                            type="button"
                            onClick={() => handleSaveNotes(lead.id)}
                            style={{
                              background: '#FFB800',
                              color: '#070A12',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '6px 14px',
                              fontSize: '12px',
                              fontWeight: 800,
                              cursor: 'pointer'
                            }}
                          >
                            Save Note
                          </button>
                        </div>
                      </div>
                    ) : (
                      <p style={{ fontSize: '13px', color: lead.notes ? '#E2E8F0' : '#475569', margin: 0, lineHeight: 1.5, fontStyle: lead.notes ? 'normal' : 'italic' }}>
                        {lead.notes || 'No notes logged yet. Click to record call notes or prospect objections.'}
                      </p>
                    )}
                  </div>
                </div>

                {/* Bottom Row: Action Hub (View Report, WhatsApp Outreach, Sales Pack) */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
                  <div style={{ fontSize: '13px', color: '#94A3B8', maxWidth: '600px' }}>
                    {lead.opportunity_summary}
                  </div>

                  <div style={{ display: 'flex', gap: '10px' }}>
                    {lead.audit_id && (
                      <button
                        type="button"
                        onClick={() => onViewAuditReport(lead.audit_id!)}
                        style={{
                          background: '#FFB800',
                          color: '#070A12',
                          border: 'none',
                          borderRadius: '8px',
                          padding: '8px 16px',
                          fontSize: '13px',
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
                          borderRadius: '8px',
                          padding: '8px 16px',
                          fontSize: '13px',
                          fontWeight: 700,
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          textDecoration: 'none'
                        }}
                      >
                        <Send size={14} />
                        <span>Send WhatsApp Follow-Up</span>
                      </a>
                    )}

                    {lead.audit_id && (
                      <a
                        href={`/api/audits/${lead.audit_id}/sales-pack`}
                        style={{
                          background: 'rgba(255, 255, 255, 0.06)',
                          color: '#CBD5E1',
                          border: '1px solid rgba(255, 255, 255, 0.15)',
                          borderRadius: '8px',
                          padding: '8px 14px',
                          fontSize: '13px',
                          textDecoration: 'none',
                          display: 'flex',
                          alignItems: 'center'
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

          {/* Bulk Stage Transition */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '13px', color: '#94A3B8', fontWeight: 600 }}>Set Stage:</span>
            <select
              onChange={(e) => {
                if (e.target.value) {
                  handleBulkStageChange(e.target.value as PipelineStage);
                }
              }}
              defaultValue=""
              style={{
                background: 'rgba(16, 24, 40, 0.9)',
                color: '#38BDF8',
                border: '1.5px solid #38BDF8',
                borderRadius: '9999px',
                padding: '6px 14px',
                fontSize: '13px',
                fontWeight: 800,
                cursor: 'pointer',
                outline: 'none'
              }}
            >
              <option value="" disabled>Choose Stage...</option>
              {STAGES.map(s => (
                <option key={s.key} value={s.key} style={{ background: '#101828', color: '#FFFFFF' }}>
                  {s.label}
                </option>
              ))}
            </select>
          </div>

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
    </div>
  );
};
