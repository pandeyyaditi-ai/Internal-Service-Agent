import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  MessageSquare, 
  Ticket, 
  ShieldCheck, 
  Bot, 
  Sparkles 
} from 'lucide-react';

export default function Sidebar({ currentEmployee }) {
  const emp = currentEmployee || {
    name: 'Sarah Connor',
    role: 'Senior Engineer',
    department: 'Engineering',
    employee_id: 'EMP-001',
  };

  return (
    <aside className="sidebar">
      <div>
        <div className="sidebar-header">
          <div className="brand-icon">
            <Bot size={24} />
          </div>
          <div className="brand-info">
            <h1>AutoIT Agent</h1>
            <span><Sparkles size={11} style={{ display: 'inline', marginRight: 3 }} /> Internal Service</span>
          </div>
        </div>

        <nav className="nav-links">
          <NavLink 
            to="/" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            end
          >
            <LayoutDashboard size={18} />
            <span>Dashboard</span>
          </NavLink>

          <NavLink 
            to="/chat" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <MessageSquare size={18} />
            <span>Support Chat</span>
          </NavLink>

          <NavLink 
            to="/tickets" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Ticket size={18} />
            <span>Tickets</span>
          </NavLink>

          <NavLink 
            to="/audit" 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <ShieldCheck size={18} />
            <span>Audit Trail</span>
          </NavLink>
        </nav>
      </div>

      <div className="sidebar-footer">
        <div className="employee-badge">
          <div className="avatar">
            {emp.name.split(' ').map(n => n[0]).join('')}
          </div>
          <div className="emp-details">
            <span className="emp-name">{emp.name}</span>
            <span className="emp-role">{emp.role} • {emp.employee_id}</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
