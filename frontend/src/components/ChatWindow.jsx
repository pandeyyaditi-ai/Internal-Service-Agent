import React, { useEffect, useRef } from 'react';
import Message from './Message';
import { Bot } from 'lucide-react';

export default function ChatWindow({ messages, loading, onActionClick }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="messages-container">
      {messages.map((msg) => (
        <Message 
          key={msg.id || Math.random()} 
          message={msg} 
          onActionClick={onActionClick}
        />
      ))}

      {loading && (
        <div className="message-row assistant">
          <div className="msg-avatar agent-avatar">
            <Bot size={20} />
          </div>
          <div className="msg-bubble-wrapper">
            <div className="message-bubble typing-bubble">
              <div className="typing-dot" />
              <div className="typing-dot" />
              <div className="typing-dot" />
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} style={{ height: 1 }} />
    </div>
  );
}
