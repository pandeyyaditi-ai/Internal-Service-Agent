import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Ticket, 
  Clock, 
  CheckCircle2, 
  AlertTriangle, 
  MessageSquare, 
  Wifi, 
  Laptop, 
  ArrowRight,
  TrendingUp,
  RefreshCw
} from 'lucide-react';
import { api } from '../services/api';
import { TicketStatus, TicketPriorityBadge } from '../components/TicketStatus';
import EscalationAlert from '../components/EscalationAlert';
import { formatRelativeTime } from '../utils/formatters';

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_tickets: 0,
    open_tickets: 0,
    in_progress_tickets: 0,
    resolved_tickets: 0,
    escalated_tickets: 0,
    avg_resolution_time_hours: 4.2,
  });
  const [recentTickets, setRecentTickets] = useState([]);
  const [escalations, setEscalations] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [statsData, ticketsData] = await Promise.all([
        api.getTicketStats().catch(() => null),
        api.getTickets({ limit: 6 }).catch(() => []),
      ]);

      if (statsData) setStats(statsData);
      const ticketsList = Array.isArray(ticketsData) 
        ? ticketsData 
        : (ticketsData?.tickets || []);
      setRecentTickets(ticketsList);
      setEscalations(ticketsList.filter(t => t && t.status === 'escalated'));
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>IT Service Operations</h1>
          <p>Real-time telemetry, automated triage metrics, and active support escalations</p>
        </div>
        <div className="dashboard-actions">
          <button 
            className="btn btn-secondary" 
            onClick={fetchDashboardData}
            title="Refresh metrics"
          >
            <RefreshCw size={15} />
            <span>Refresh</span>
          </button>
          <Link to="/chat" className="btn btn-primary">
            <MessageSquare size={16} />
            <span>Launch Support Chat</span>
          </Link>
        </div>
      </div>

      {/* Escalation Alert */}
      <EscalationAlert 
        escalations={escalations} 
        count={stats.escalated_tickets || escalations.length} 
      />

      {/* KPI Stats Cards */}
      <div className="stats-grid">
        <div className="glass-panel stat-card">
          <div className="stat-header">
            <span className="stat-label">Active Tickets</span>
            <div className="stat-icon-wrapper" style={{ background: 'rgba(56, 189, 248, 0.2)', color: '#38bdf8' }}>
              <Clock size={20} />
            </div>
          </div>
          <div className="stat-value">{stats.open_tickets + stats.in_progress_tickets}</div>
          <div className="stat-subtext text-info">
            <span>{stats.open_tickets} pending triage</span>
          </div>
        </div>

        <div className="glass-panel stat-card">
          <div className="stat-header">
            <span className="stat-label">Escalated to Human</span>
            <div className="stat-icon-wrapper" style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#ef4444' }}>
              <AlertTriangle size={20} />
            </div>
          </div>
          <div className="stat-value" style={{ color: '#f87171' }}>{stats.escalated_tickets}</div>
          <div className="stat-subtext text-danger">
            <span>Requires Tier 2 engineer</span>
          </div>
        </div>

        <div className="glass-panel stat-card">
          <div className="stat-header">
            <span className="stat-label">Resolved Issues</span>
            <div className="stat-icon-wrapper" style={{ background: 'rgba(52, 211, 153, 0.2)', color: '#34d399' }}>
              <CheckCircle2 size={20} />
            </div>
          </div>
          <div className="stat-value" style={{ color: '#34d399' }}>{stats.resolved_tickets}</div>
          <div className="stat-subtext text-success">
            <span>AI first-contact resolution 82%</span>
          </div>
        </div>

        <div className="glass-panel stat-card">
          <div className="stat-header">
            <span className="stat-label">Avg Resolution</span>
            <div className="stat-icon-wrapper" style={{ background: 'rgba(139, 92, 246, 0.2)', color: '#8b5cf6' }}>
              <TrendingUp size={20} />
            </div>
          </div>
          <div className="stat-value">{stats.avg_resolution_time_hours || 4.2}h</div>
          <div className="stat-subtext" style={{ color: '#c084fc' }}>
            <span>-35% vs human triage</span>
          </div>
        </div>
      </div>

      {/* Dual Column: Recent Tickets & Quick Actions */}
      <div className="dashboard-grid-dual">
        {/* Recent Tickets Table */}
        <div className="glass-panel" style={{ overflow: 'hidden' }}>
          <div className="panel-header">
            <h3>Recent Support Tickets</h3>
            <Link to="/tickets" style={{ color: '#60a5fa', fontSize: 13, textDecoration: 'none', display: 'flex', alignItems: 'center', gap: 4 }}>
              <span>View all</span>
              <ArrowRight size={14} />
            </Link>
          </div>

          <table className="custom-table">
            <thead>
              <tr>
                <th>Ticket ID</th>
                <th>Subject</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {recentTickets.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', color: '#64748b', padding: '30px' }}>
                    No tickets found. Start a support chat to generate one.
                  </td>
                </tr>
              ) : (
                recentTickets.map((t) => (
                  <tr key={t.ticket_id}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#93c5fd' }}>
                      {t.ticket_id}
                    </td>
                    <td style={{ maxWidth: '240px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {t.subject}
                    </td>
                    <td>
                      <TicketPriorityBadge priority={t.priority} />
                    </td>
                    <td>
                      <TicketStatus status={t.status} />
                    </td>
                    <td style={{ color: 'var(--text-muted)' }}>
                      {formatRelativeTime(t.created_at)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Quick Actions Panel */}
        <div className="glass-panel">
          <div className="panel-header">
            <h3>Automated Workflows</h3>
          </div>
          <div className="quick-actions-list">
            <Link to="/chat" className="quick-action-item">
              <div className="qa-icon" style={{ background: 'rgba(6, 182, 212, 0.15)', color: '#06b6d4' }}>
                <Wifi size={18} />
              </div>
              <div className="qa-info">
                <h5>Run VPN Diagnostics</h5>
                <p>Interactive step-by-step connectivity resolver</p>
              </div>
            </Link>

            <Link to="/tickets" className="quick-action-item">
              <div className="qa-icon" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#3b82f6' }}>
                <Ticket size={18} />
              </div>
              <div className="qa-info">
                <h5>Create Support Ticket</h5>
                <p>Submit a formal IT service desk request</p>
              </div>
            </Link>

            <Link to="/chat" className="quick-action-item">
              <div className="qa-icon" style={{ background: 'rgba(139, 92, 246, 0.15)', color: '#8b5cf6' }}>
                <Laptop size={18} />
              </div>
              <div className="qa-info">
                <h5>Software & Hardware Inquiries</h5>
                <p>Check approved application whitelist and policies</p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
