import React from 'react';
import { User, Bot, AlertTriangle, CheckCircle2 } from 'lucide-react';
import SourceReference from './SourceReference';
import { formatRelativeTime } from '../utils/formatters';

export default function Message({ message, onActionClick }) {
  const isUser = message.role === 'user';

  // Render markdown-like text with paragraphs, lists, bolding and code blocks
  const renderFormattedContent = (content) => {
    if (!content) return null;

    const lines = content.split('\n');
    return lines.map((line, index) => {
      // Bold syntax **text**
      const formattedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

      // Check if bullet point
      if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
        return (
          <li 
            key={index}
            style={{ marginLeft: '18px', marginBottom: '4px' }}
            dangerouslySetInnerHTML={{ __html: formattedLine.replace(/^[-*]\s+/, '') }}
          />
        );
      }

      // Check if numbered list
      const numMatch = line.trim().match(/^(\d+)\.\s+(.*)/);
      if (numMatch) {
        return (
          <div 
            key={index} 
            style={{ marginLeft: '12px', marginBottom: '4px' }}
            dangerouslySetInnerHTML={{ __html: `<strong>${numMatch[1]}.</strong> ${numMatch[2]}` }}
          />
        );
      }

      if (line.trim() === '') {
        return <div key={index} style={{ height: '8px' }} />;
      }

      return (
        <p 
          key={index} 
          style={{ marginBottom: '6px' }}
          dangerouslySetInnerHTML={{ __html: formattedLine }} 
        />
      );
    });
  };

  return (
    <div className={`message-row ${isUser ? 'user' : 'assistant'}`}>
      <div className={`msg-avatar ${isUser ? 'user-avatar' : 'agent-avatar'}`}>
        {isUser ? <User size={18} /> : <Bot size={20} />}
      </div>

      <div className="msg-bubble-wrapper">
        <div className="message-bubble">
          {message.escalated && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 10px',
              marginBottom: '10px',
              background: 'rgba(239, 68, 68, 0.2)',
              border: '1px solid rgba(239, 68, 68, 0.4)',
              borderRadius: '6px',
              color: '#fca5a5',
              fontSize: '12px',
              fontWeight: '600'
            }}>
              <AlertTriangle size={14} />
              <span>Escalated to Human IT Support Agent</span>
            </div>
          )}

          {renderFormattedContent(message.content)}

          {message.ticket && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginTop: '10px',
              padding: '8px 12px',
              background: 'rgba(52, 211, 153, 0.15)',
              border: '1px solid rgba(52, 211, 153, 0.3)',
              borderRadius: '8px',
              color: '#34d399',
              fontSize: '13px'
            }}>
              <CheckCircle2 size={16} />
              <span>
                Ticket Created: <strong>{message.ticket.ticket_id || message.ticket}</strong>
              </span>
            </div>
          )}

          {message.sources && message.sources.length > 0 && (
            <SourceReference sources={message.sources} />
          )}

          {message.suggested_actions && message.suggested_actions.length > 0 && (
            <div className="chat-actions-wrapper">
              {message.suggested_actions.map((act, idx) => (
                <button
                  key={idx}
                  className="action-chip"
                  onClick={() => onActionClick && onActionClick(act)}
                >
                  {act}
                </button>
              ))}
            </div>
          )}
        </div>

        <span className="msg-timestamp">
          {message.timestamp ? formatRelativeTime(message.timestamp) : ''}
        </span>
      </div>
    </div>
  );
}
