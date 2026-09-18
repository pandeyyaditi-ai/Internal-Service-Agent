import React, { useState, useRef } from 'react';
import { Send, Sparkles } from 'lucide-react';

export default function ChatInput({ onSendMessage, disabled, placeholder }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!text.trim() || disabled) return;
    onSendMessage(text);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e) => {
    setText(e.target.value);
    // Auto grow textarea
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  const sendQuickPrompt = (prompt) => {
    if (disabled) return;
    onSendMessage(prompt);
  };

  return (
    <div className="chat-input-container">
      <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
        <button
          type="button"
          className="action-chip"
          onClick={() => sendQuickPrompt("My VPN is disconnected and won't reconnect")}
          disabled={disabled}
        >
          <Sparkles size={12} style={{ display: 'inline', marginRight: 4 }} />
          Diagnose VPN Issue
        </button>
        <button
          type="button"
          className="action-chip"
          onClick={() => sendQuickPrompt("How do I reset my company password?")}
          disabled={disabled}
        >
          Password Reset Guide
        </button>
        <button
          type="button"
          className="action-chip"
          onClick={() => sendQuickPrompt("Can you create a support ticket for my broken monitor?")}
          disabled={disabled}
        >
          Create Hardware Ticket
        </button>
        <button
          type="button"
          className="action-chip"
          onClick={() => sendQuickPrompt("I need to speak to a human IT agent")}
          disabled={disabled}
        >
          Escalate to Human
        </button>
      </div>

      <form onSubmit={handleSubmit} className="chat-input-form">
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || "Ask a question, diagnose VPN, or request a ticket..."}
          className="chat-textarea"
          disabled={disabled}
        />
        <button
          type="submit"
          className="chat-send-btn"
          disabled={disabled || !text.trim()}
          title="Send message (Enter)"
        >
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
