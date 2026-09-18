import React from 'react';
import { TicketStatus, TicketPriorityBadge } from './TicketStatus';
import { formatRelativeTime } from '../utils/formatters';
import { Tag } from 'lucide-react';

export default function TicketCard({ ticket, onClick }) {
  return (
    <div className="glass-panel ticket-card" onClick={() => onClick && onClick(ticket)}>
      <div className="ticket-card-header">
        <span className="ticket-id">{ticket.ticket_id}</span>
        <div style={{ display: 'flex', gap: '6px' }}>
          <TicketPriorityBadge priority={ticket.priority} />
          <TicketStatus status={ticket.status} />
        </div>
      </div>

      <div className="ticket-card-title">
        {ticket.subject}
      </div>

      <div className="ticket-card-desc">
        {ticket.description}
      </div>

      <div className="ticket-card-footer">
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <Tag size={13} />
          <span>{ticket.category?.toUpperCase() || 'GENERAL'}</span>
        </div>
        <div>
          {ticket.created_at ? formatRelativeTime(ticket.created_at) : 'recently'}
        </div>
      </div>
    </div>
  );
}
