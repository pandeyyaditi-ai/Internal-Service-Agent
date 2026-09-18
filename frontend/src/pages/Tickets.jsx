import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  X, 
  AlertTriangle 
} from 'lucide-react';
import { api } from '../services/api';
import TicketCard from '../components/TicketCard';
import { TicketStatus, TicketPriorityBadge } from '../components/TicketStatus';
import { formatDateTime } from '../utils/formatters';

export default function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');

  // New ticket form
  const [newSubject, setNewSubject] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newCategory, setNewCategory] = useState('vpn');
  const [newPriority, setNewPriority] = useState('medium');

  // Resolution edit
  const [resNotes, setResNotes] = useState('');
  const [updateStatus, setUpdateStatus] = useState('');

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const data = await api.getTickets({
        search: search || undefined,
        status: statusFilter || undefined,
        priority: priorityFilter || undefined,
        category: categoryFilter || undefined,
      });
      const list = Array.isArray(data) ? data : (data?.tickets || []);
      setTickets(list);
    } catch (err) {
      console.error('Error fetching tickets:', err);
      setTickets([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [statusFilter, priorityFilter, categoryFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchTickets();
  };

  const handleCreateTicket = async (e) => {
    e.preventDefault();
    if (!newSubject.trim() || !newDesc.trim()) return;

    try {
      await api.createTicket({
        employee_id: 'EMP-001',
        subject: newSubject.trim(),
        description: newDesc.trim(),
        category: newCategory,
        priority: newPriority,
      });
      setIsCreateOpen(false);
      setNewSubject('');
      setNewDesc('');
      fetchTickets();
    } catch (err) {
      alert(`Failed to create ticket: ${err.message}`);
    }
  };

  const handleUpdateTicket = async () => {
    if (!selectedTicket) return;
    try {
      const payload = {};
      if (updateStatus) payload.status = updateStatus;
      if (resNotes) payload.resolution_notes = resNotes;

      await api.updateTicket(selectedTicket.ticket_id, payload);
      setSelectedTicket(null);
      fetchTickets();
    } catch (err) {
      alert(`Failed to update ticket: ${err.message}`);
    }
  };

  return (
    <div className="tickets-page">
      {/* Page Title & Create Trigger */}
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>Support Tickets</h1>
          <p>Manage, inspect, and update internal IT incident requests</p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsCreateOpen(true)}>
          <Plus size={16} />
          <span>New Ticket</span>
        </button>
      </div>

      {/* Filter & Search Bar */}
      <div className="glass-panel filter-bar">
        <form onSubmit={handleSearchSubmit} className="search-input-group">
          <Search size={16} style={{ color: 'var(--text-muted)' }} />
          <input
            type="text"
            placeholder="Search by ticket ID or subject..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </form>

        <div className="filter-controls">
          <select 
            className="select-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="escalated">Escalated</option>
            <option value="closed">Closed</option>
          </select>

          <select 
            className="select-filter"
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <option value="">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>

          <select 
            className="select-filter"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
          >
            <option value="">All Categories</option>
            <option value="vpn">VPN</option>
            <option value="password">Password</option>
            <option value="hardware">Hardware</option>
            <option value="software">Software</option>
            <option value="network">Network</option>
            <option value="email">Email</option>
            <option value="access">Access</option>
          </select>
        </div>
      </div>

      {/* Tickets List */}
      {loading ? (
        <div style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading tickets...
        </div>
      ) : tickets.length === 0 ? (
        <div className="glass-panel" style={{ padding: '60px', textAlign: 'center', color: 'var(--text-muted)' }}>
          No matching tickets found. Try clearing your filters or create a new ticket.
        </div>
      ) : (
        <div className="tickets-grid">
          {tickets.map((t) => (
            <TicketCard 
              key={t.ticket_id} 
              ticket={t} 
              onClick={(ticket) => {
                setSelectedTicket(ticket);
                setUpdateStatus(ticket.status);
                setResNotes(ticket.resolution_notes || '');
              }}
            />
          ))}
        </div>
      )}

      {/* Create Ticket Modal */}
      {isCreateOpen && (
        <div className="modal-backdrop" onClick={() => setIsCreateOpen(false)}>
          <div className="glass-panel modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Support Ticket</h3>
              <button 
                className="btn btn-secondary" 
                style={{ padding: '4px 8px' }}
                onClick={() => setIsCreateOpen(false)}
              >
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleCreateTicket}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Subject</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    placeholder="e.g. Cisco AnyConnect VPN fails to handshake"
                    value={newSubject}
                    onChange={(e) => setNewSubject(e.target.value)}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                  <div className="form-group">
                    <label>Category</label>
                    <select
                      className="form-control"
                      value={newCategory}
                      onChange={(e) => setNewCategory(e.target.value)}
                    >
                      <option value="vpn">VPN</option>
                      <option value="password">Password / MFA</option>
                      <option value="hardware">Hardware / Laptop</option>
                      <option value="software">Software / License</option>
                      <option value="network">Network / WiFi</option>
                      <option value="email">Email / Outlook</option>
                      <option value="access">Access / Permissions</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Priority</label>
                    <select
                      className="form-control"
                      value={newPriority}
                      onChange={(e) => setNewPriority(e.target.value)}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical (Immediate Escalation)</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label>Detailed Description</label>
                  <textarea
                    rows={4}
                    required
                    className="form-control"
                    placeholder="Provide specific details, error codes, and steps to reproduce..."
                    value={newDesc}
                    onChange={(e) => setNewDesc(e.target.value)}
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setIsCreateOpen(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Submit Ticket
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Ticket Details / Update Modal */}
      {selectedTicket && (
        <div className="modal-backdrop" onClick={() => setSelectedTicket(null)}>
          <div className="glass-panel modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span className="ticket-id">{selectedTicket.ticket_id}</span>
                <TicketPriorityBadge priority={selectedTicket.priority} />
                <TicketStatus status={selectedTicket.status} />
              </div>
              <button 
                className="btn btn-secondary" 
                style={{ padding: '4px 8px' }}
                onClick={() => setSelectedTicket(null)}
              >
                <X size={16} />
              </button>
            </div>

            <div className="modal-body">
              <div>
                <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>{selectedTicket.subject}</h2>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', gap: 16 }}>
                  <span>Created: {formatDateTime(selectedTicket.created_at)}</span>
                  <span>Employee: {selectedTicket.employee_id}</span>
                  <span>Category: {selectedTicket.category?.toUpperCase()}</span>
                </div>
              </div>

              <div className="glass-panel" style={{ padding: 16, background: 'rgba(255,255,255,0.02)' }}>
                <h4 style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 6 }}>Description</h4>
                <p style={{ fontSize: 14, lineHeight: 1.6 }}>{selectedTicket.description}</p>
              </div>

              {selectedTicket.escalation_reason && (
                <div style={{
                  padding: 12,
                  borderRadius: 8,
                  background: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  color: '#fca5a5',
                  fontSize: 13
                }}>
                  <AlertTriangle size={18} />
                  <div>
                    <strong>Escalation Reason:</strong> {selectedTicket.escalation_reason}
                  </div>
                </div>
              )}

              <div className="form-group">
                <label>Update Status</label>
                <select 
                  className="form-control"
                  value={updateStatus}
                  onChange={(e) => setUpdateStatus(e.target.value)}
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                  <option value="escalated">Escalated</option>
                  <option value="closed">Closed</option>
                </select>
              </div>

              <div className="form-group">
                <label>Resolution Notes / Comments</label>
                <textarea
                  rows={3}
                  className="form-control"
                  placeholder="Add resolution explanation or technician notes..."
                  value={resNotes}
                  onChange={(e) => setResNotes(e.target.value)}
                />
              </div>
            </div>

            <div className="modal-footer">
              <button 
                type="button" 
                className="btn btn-secondary" 
                onClick={() => setSelectedTicket(null)}
              >
                Close
              </button>
              <button 
                type="button" 
                className="btn btn-primary"
                onClick={handleUpdateTicket}
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
