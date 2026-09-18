import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import SupportChat from './pages/SupportChat';
import Tickets from './pages/Tickets';
import AuditTrail from './pages/AuditTrail';
import './styles/App.css';
import './styles/Chat.css';
import './styles/Dashboard.css';
import './styles/Ticket.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('App render error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 40, color: '#f87171' }}>
          <h2>Something went wrong loading this view.</h2>
          <pre style={{ background: '#1e293b', padding: 16, borderRadius: 8, color: '#fca5a5' }}>
            {this.state.error?.toString()}
          </pre>
          <button 
            className="btn btn-primary" 
            style={{ marginTop: 16 }} 
            onClick={() => window.location.reload()}
          >
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function App() {
  const currentEmployee = {
    employee_id: 'EMP-001',
    name: 'Sarah Connor',
    department: 'Engineering',
    role: 'Senior Software Engineer'
  };

  return (
    <div className="app-container">
      <Sidebar currentEmployee={currentEmployee} />
      <main className="main-content">
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/chat" element={<SupportChat />} />
            <Route path="/tickets" element={<Tickets />} />
            <Route path="/audit" element={<AuditTrail />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </ErrorBoundary>
      </main>
    </div>
  );
}
