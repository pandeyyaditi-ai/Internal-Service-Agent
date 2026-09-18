import React from 'react';
import { useChat } from '../hooks/useChat';
import ChatWindow from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';
import { 
  Plus, 
  Bot, 
  ShieldAlert 
} from 'lucide-react';
import { formatRelativeTime } from '../utils/formatters';

export default function SupportChat() {
  const {
    messages,
    loading,
    wsConnected,
    conversationId,
    conversations,
    sendMessage,
    selectConversation,
    startNewConversation,
  } = useChat('EMP-001');

  const handleEscalateQuick = () => {
    sendMessage("I need to speak to a human IT engineer directly. Please escalate this.");
  };

  return (
    <div className="chat-page">
      {/* Conversations Drawer */}
      <div className="chat-history-sidebar">
        <div className="chat-history-header">
          <h2>Conversations</h2>
          <button 
            className="btn btn-primary" 
            style={{ padding: '6px 12px', fontSize: '13px' }}
            onClick={startNewConversation}
          >
            <Plus size={14} />
            <span>New Chat</span>
          </button>
        </div>

        <div className="conversation-list">
          {conversations.length === 0 ? (
            <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
              No previous conversations
            </div>
          ) : (
            conversations.map((c) => (
              <div
                key={c.conversation_id}
                className={`conversation-item ${c.conversation_id === conversationId ? 'active' : ''}`}
                onClick={() => selectConversation(c.conversation_id)}
              >
                <div className="conversation-preview">
                  {c.last_message || 'IT Support Session'}
                </div>
                <div className="conversation-meta">
                  <span>{c.intent ? c.intent.replace('_', ' ') : 'General'}</span>
                  <span>{c.updated_at ? formatRelativeTime(c.updated_at) : ''}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="chat-main">
        <div className="chat-topbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div className="brand-icon" style={{ width: 34, height: 34 }}>
              <Bot size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: '15px', fontWeight: '700' }}>IT Service Helpdesk Agent</h2>
              <div className="agent-status-badge">
                <div 
                  className="status-dot" 
                  style={{ background: wsConnected ? '#10b981' : '#38bdf8' }} 
                />
                <span>{wsConnected ? 'Realtime WebSocket Active' : 'AI Assistant Ready (HTTP)'}</span>
              </div>
            </div>
          </div>

          <button 
            className="btn btn-secondary" 
            style={{ fontSize: '13px', padding: '6px 14px', gap: '6px' }}
            onClick={handleEscalateQuick}
          >
            <ShieldAlert size={14} style={{ color: '#f87171' }} />
            <span>Request Human Agent</span>
          </button>
        </div>

        <ChatWindow 
          messages={messages} 
          loading={loading} 
          onActionClick={(actionText) => sendMessage(actionText)}
        />

        <ChatInput 
          onSendMessage={sendMessage} 
          disabled={loading} 
        />
      </div>
    </div>
  );
}
