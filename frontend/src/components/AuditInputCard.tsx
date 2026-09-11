import React, { useState } from 'react';
import { Link2, Sparkles, MapPin, Globe, Instagram, Facebook, PlayCircle, ShieldCheck } from 'lucide-react';
import { SourceType } from '../types/audit';

interface AuditInputCardProps {
  onGenerate: (url: string, isDemo?: boolean) => void;
  isLoading: boolean;
}

const SAMPLE_PRESETS = [
  {
    label: "Google Maps CID (Test Target)",
    icon: MapPin,
    url: "https://maps.google.com/?cid=8429486214490638391&g_mp=Cidnb29nbGUubWFwcy5wbGFjZXMudjEuUGxhY2VzLlNlYXJjaFRleHQQAhgEIAA",
    badge: "Real Maps CID"
  },
  {
    label: "Business Website",
    icon: Globe,
    url: "https://lumina-interiors.in",
    badge: "Architecture"
  },
  {
    label: "Instagram Profile",
    icon: Instagram,
    url: "https://instagram.com/velvetglowsalon",
    badge: "Wellness"
  },
  {
    label: "Facebook Business",
    icon: Facebook,
    url: "https://facebook.com/sterlingautoworks",
    badge: "Automotive"
  }
];

export const AuditInputCard: React.FC<AuditInputCardProps> = ({ onGenerate, isLoading }) => {
  const [url, setUrl] = useState('');

  const detectSource = (input: string): SourceType => {
    const low = input.toLowerCase();
    if (low.includes('google.com/maps') || low.includes('maps.google') || low.includes('goo.gl/maps') || low.includes('maps.app.goo.gl')) {
      return 'GOOGLE_MAPS';
    }
    if (low.includes('instagram.com')) return 'INSTAGRAM';
    if (low.includes('facebook.com') || low.includes('fb.com')) return 'FACEBOOK';
    if (low.includes('.') && low.length > 4) return 'WEBSITE';
    return 'UNKNOWN';
  };

  const detectedSource = detectSource(url);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim() && !isLoading) {
      onGenerate(url.trim(), false);
    }
  };

  const handleDemoClick = () => {
    if (!isLoading) {
      onGenerate("https://demo.onehive.io/apex-dental", true);
    }
  };

  const handleSelectSample = (sampleUrl: string) => {
    setUrl(sampleUrl);
  };

  return (
    <div className="card-input-container">
      <form onSubmit={handleSubmit} className="input-form">
        {/* Main Input Row: Grid layout ensures input and button never overlap */}
        <div className="input-action-grid">
          <div className="url-input-wrapper">
            <Link2 className="url-icon" size={20} />
            <input
              type="text"
              className="main-url-input"
              placeholder="Paste Google Maps, Website, Instagram, or Facebook URL..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={isLoading}
              autoFocus
            />
            {url.trim() && detectedSource !== 'UNKNOWN' && (
              <div className="url-source-detected-badge">
                {detectedSource === 'GOOGLE_MAPS' && <MapPin size={12} />}
                {detectedSource === 'WEBSITE' && <Globe size={12} />}
                {detectedSource === 'INSTAGRAM' && <Instagram size={12} />}
                {detectedSource === 'FACEBOOK' && <Facebook size={12} />}
                <span>{detectedSource.replace('_', ' ')}</span>
              </div>
            )}
          </div>

          <button
            type="submit"
            className="btn-generate"
            disabled={isLoading || !url.trim()}
          >
            <Sparkles size={18} />
            <span>{isLoading ? 'Researching...' : 'Generate Free Audit'}</span>
          </button>
        </div>

        {/* Quick presets and Demo Mode row */}
        <div className="quick-fill-row">
          <div className="quick-fill-left">
            <span className="quick-fill-label">Quick Test Presets:</span>
            {SAMPLE_PRESETS.map((p) => {
              const Icon = p.icon;
              return (
                <button
                  key={p.label}
                  type="button"
                  className="sample-pill-btn"
                  onClick={() => handleSelectSample(p.url)}
                  disabled={isLoading}
                >
                  <Icon size={13} style={{ color: 'var(--accent-gold)' }} />
                  <span>{p.label}</span>
                </button>
              );
            })}
          </div>

          {/* Explicit Demo Mode Button */}
          <div className="demo-mode-container">
            <button
              type="button"
              className="btn-demo-mode"
              onClick={handleDemoClick}
              disabled={isLoading}
              title="Loads deterministic Apex Dental fixture without external research"
            >
              <PlayCircle size={14} />
              <span>Load Demo Business</span>
              <span className="demo-badge-tag">MOCK</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
