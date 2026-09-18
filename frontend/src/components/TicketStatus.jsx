import React from 'react';
import { 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  AlertCircle, 
  Archive 
} from 'lucide-react';
import { capitalize } from '../utils/formatters';

export function TicketStatus({ status }) {
  const s = status ? status.toLowerCase() : 'open';

  const icons = {
    open: <Clock size={12} />,
    in_progress: <Clock size={12} />,
    resolved: <CheckCircle2 size={12} />,
    escalated: <AlertTriangle size={12} />,
    closed: <Archive size={12} />,
  };

  return (
    <span className={`badge badge-${s}`}>
      {icons[s] || <Clock size={12} />}
      {capitalize(s)}
    </span>
  );
}

export function TicketPriorityBadge({ priority }) {
  const p = priority ? priority.toLowerCase() : 'medium';

  return (
    <span className={`badge badge-priority-${p}`}>
      {p === 'critical' && <AlertCircle size={12} />}
      {capitalize(p)}
    </span>
  );
}

export default TicketStatus;
