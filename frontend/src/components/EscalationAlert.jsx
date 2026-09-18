import React from 'react';
import { AlertOctagon, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function EscalationAlert({ escalations = [], count = 0 }) {
  const activeCount = count || escalations.length;
  if (activeCount === 0) return null;

  const latestReason = escalations[0]?.escalation_reason || 
    `${activeCount} tickets currently require human IT engineer intervention.`;

  return (
    <div className="escalation-banner">
      <div className="escalation-content">
        <div className="escalation-icon">
          <AlertOctagon size={22} />
        </div>
        <div className="escalation-text">
          <h4>{activeCount} Active Escalation{activeCount > 1 ? 's' : ''} Detected</h4>
          <p>{latestReason}</p>
        </div>
      </div>

      <Link to="/tickets?status=escalated" className="btn btn-danger" style={{ textDecoration: 'none' }}>
        <span>View In Queue</span>
        <ArrowRight size={15} />
      </Link>
    </div>
  );
}
