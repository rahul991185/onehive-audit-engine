import React, { useEffect, useState } from 'react';
import { Check, Loader2, Circle } from 'lucide-react';

interface ProgressTrackerProps {
  onComplete?: () => void;
}

const STEPS = [
  "Identifying business & source channel",
  "Collecting available public signals",
  "Reviewing 6-dimension digital footprint",
  "Analyzing #1 primary growth opportunity",
  "Synthesizing structured diagnostic brief",
  "Rendering verified 5-page OneHive PDF"
];

export const ProgressTracker: React.FC<ProgressTrackerProps> = () => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStepIndex((prev) => {
        if (prev < STEPS.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 900);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="progress-container">
      <div className="progress-header">
        <h3>
          <Loader2 size={18} className="animate-spin" style={{ color: 'var(--accent-gold)' }} />
          <span>Analyzing Business Presence...</span>
        </h3>
        <span style={{ fontSize: '12px', color: 'var(--accent-gold)', fontWeight: 700 }}>
          Step {Math.min(currentStepIndex + 1, STEPS.length)} of {STEPS.length}
        </span>
      </div>

      <div className="progress-steps-list">
        {STEPS.map((step, idx) => {
          let status: 'done' | 'active' | 'pending' = 'pending';
          if (idx < currentStepIndex) status = 'done';
          else if (idx === currentStepIndex) status = 'active';

          return (
            <div key={step} className={`progress-step-item ${status}`}>
              <div className={`step-icon-badge ${status}`}>
                {status === 'done' && <Check size={14} />}
                {status === 'active' && <Loader2 size={14} className="animate-spin" />}
                {status === 'pending' && <Circle size={10} />}
              </div>
              <span className="step-text">{step}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
