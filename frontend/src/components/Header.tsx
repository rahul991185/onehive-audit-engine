import React from 'react';
import { ShieldCheck } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="app-header">
      <div className="header-brand-group">
        <img 
          src="/onehive_logo.png" 
          alt="OneHive Technologies" 
          className="header-logo-img" 
        />
        <div className="header-brand-divider"></div>
        <div className="header-product-title">
          <h1>OneHive Technologies</h1>
          <p>Digital Presence Intelligence Engine</p>
        </div>
      </div>

      <div className="header-badge">
        <span className="pulse-dot"></span>
        <span>Live Diagnostic System</span>
      </div>
    </header>
  );
};
