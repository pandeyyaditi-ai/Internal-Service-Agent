import React, { useState, useEffect } from 'react';
import { 
  ChevronDown, 
  ChevronRight, 
  Terminal, 
  Cpu, 
  User 
} from 'lucide-react';
import { api } from '../services/api';
import { formatDateTime } from '../utils/formatters';

export default function AuditTrail() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');
  const [actorFilter, setActorFilter] = useState('');
  const [expandedLogId, setExpandedLogId] = useState(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await api.getAuditLogs({
        action_type: actionFilter || undefined,
        actor: actorFilter || undefined,
        limit: 50,
      });
      const list = Array.isArray(data) ? data : (data?.logs || []);
      setLogs(list);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [actionFilter, actorFilter]);

  const toggleExpand = (logId) => {
    setExpandedLogId(expandedLogId === logId ? null : logId);
  };

  const getActorBadge = (actor) => {
    const act = (actor || 'system').toLowerCase();
    if (act.includes('agent') || act.includes('ai')) {
      return (
        <span className="badge" style={{ background: 'rgba(139, 92, 246, 0.2)', color: '#c084fc' }}>
          <Cpu size={12} /> AI Agent
        </span>
      );
    }
    if (act.includes('emp') || act.includes('user')) {
      return (
        <span className="badge" style={{ background: 'rgba(56, 189, 248, 0.2)', color: '#38bdf8' }}>
          <User size={12} /> {actor}
        </span>
      );
    }
    return (
      <span className="badge" style={{ background: 'rgba(148, 163, 184, 0.2)', color: '#94a3b8' }}>
        <Terminal size={12} /> System
      </span>
    );
  };

  return (
    <div className="tickets-page">
      <div className="dashboard-header">
        <div className="dashboard-title">
          <h1>Security & Compliance Audit Trail</h1>
          <p>Complete immutable record of all agent interactions, AI intent decisions, and operational actions</p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="glass-panel filter-bar">
        <div className="filter-controls" style={{ width: '100%', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: 12 }}>
            <select
              className="select-filter"
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
            >
              <option value="">All Action Types</option>
              <option value="intent_detected">Intent Classification</option>
              <option value="ticket_created">Ticket Created</option>
              <option value="ticket_updated">Ticket Updated</option>
              <option value="escalation_triggered">Escalation Triggered</option>
              <option value="faq_searched">FAQ Search</option>
              <option value="vpn_troubleshoot_step">VPN Troubleshooting</option>
            </select>

            <select
              className="select-filter"
              value={actorFilter}
              onChange={(e) => setActorFilter(e.target.value)}
            >
              <option value="">All Actors</option>
              <option value="agent">AI Agent</option>
              <option value="employee">Employee</option>
              <option value="system">System</option>
            </select>
          </div>

          <button className="btn btn-secondary" onClick={fetchLogs}>
            Refresh Logs
          </button>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        <table className="custom-table">
          <thead>
            <tr>
              <th style={{ width: '40px' }}></th>
              <th>Timestamp</th>
              <th>Action Type</th>
              <th>Actor</th>
              <th>Target Entity</th>
              <th>Summary</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                  Loading audit trail...
                </td>
              </tr>
            ) : logs.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                  No audit log entries recorded.
                </td>
              </tr>
            ) : (
              logs.map((entry) => {
                const logId = entry.audit_id || entry._id;
                const isExpanded = expandedLogId === logId;

                return (
                  <React.Fragment key={logId}>
                    <tr 
                      onClick={() => toggleExpand(logId)} 
                      style={{ cursor: 'pointer', background: isExpanded ? 'rgba(59, 130, 246, 0.05)' : undefined }}
                    >
                      <td>
                        {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-secondary)' }}>
                        {formatDateTime(entry.timestamp)}
                      </td>
                      <td>
                        <span style={{ fontWeight: 600, color: '#e2e8f0' }}>
                          {entry.action_type}
                        </span>
                      </td>
                      <td>{getActorBadge(entry.actor)}</td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                        {entry.target_entity || 'N/A'}
                      </td>
                      <td style={{ color: 'var(--text-secondary)', maxWidth: 300, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {entry.details ? JSON.stringify(entry.details) : '—'}
                      </td>
                    </tr>

                    {isExpanded && (
                      <tr>
                        <td colSpan={6} style={{ background: 'rgba(10, 14, 23, 0.6)', padding: '16px 24px' }}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                            <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent-cyan)' }}>
                              RAW AUDIT PAYLOAD & METADATA
                            </div>
                            <pre style={{
                              background: 'rgba(0, 0, 0, 0.5)',
                              padding: '12px',
                              borderRadius: '8px',
                              fontFamily: 'var(--font-mono)',
                              fontSize: '12px',
                              color: '#a7f3d0',
                              overflowX: 'auto',
                              border: '1px solid var(--border-color)'
                            }}>
                              {JSON.stringify(entry, null, 2)}
                            </pre>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
