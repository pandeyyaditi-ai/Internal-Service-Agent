import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../services/api';

export function useChat(employeeId = 'EMP-001') {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);

  // Load conversation list on mount
  const loadConversations = useCallback(async () => {
    try {
      const data = await api.getConversations(employeeId);
      setConversations(data || []);
    } catch (err) {
      console.warn('Could not load conversations:', err);
    }
  }, [employeeId]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // WebSocket Connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/api/chat/ws/${employeeId}`;

    let socket;
    try {
      socket = new WebSocket(wsUrl);

      socket.onopen = () => {
        setWsConnected(true);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.message) {
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now().toString(),
                role: data.role || 'assistant',
                content: data.message,
                timestamp: new Date().toISOString(),
                intent: data.intent,
                suggested_actions: data.suggested_actions,
                sources: data.sources,
                escalated: data.escalated,
                ticket: data.ticket,
              },
            ]);
            if (data.conversation_id) {
              setConversationId(data.conversation_id);
            }
          }
        } catch (e) {
          console.error('Error parsing WS message:', e);
        } finally {
          setLoading(false);
        }
      };

      socket.onerror = (err) => {
        console.warn('WebSocket connection error, fallback to REST API', err);
        setWsConnected(false);
      };

      socket.onclose = () => {
        setWsConnected(false);
      };

      wsRef.current = socket;
    } catch (e) {
      console.warn('Failed to initialize WebSocket, falling back to HTTP', e);
    }

    return () => {
      if (socket && socket.readyState === WebSocket.OPEN) {
        socket.close();
      }
    };
  }, [employeeId]);

  // Load a specific conversation
  const selectConversation = async (convId) => {
    setLoading(true);
    setConversationId(convId);
    try {
      const data = await api.getConversation(convId);
      if (data && data.messages) {
        setMessages(
          data.messages.map((m, idx) => ({
            id: idx.toString(),
            role: m.role,
            content: m.content,
            timestamp: m.timestamp,
            suggested_actions: m.suggested_actions,
            sources: m.sources,
          }))
        );
      }
    } catch (err) {
      console.error('Failed to load conversation details:', err);
    } finally {
      setLoading(false);
    }
  };

  // Start new conversation
  const startNewConversation = () => {
    setConversationId(null);
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content:
          "👋 Hello! I am your AI IT Service Agent. How can I help you today? You can ask about VPN issues, IT policies, software installation, or create and track support tickets.",
        timestamp: new Date().toISOString(),
      },
    ]);
  };

  // Initialize with welcome message if empty
  useEffect(() => {
    if (messages.length === 0 && !conversationId) {
      startNewConversation();
    }
  }, [conversationId, messages.length]);

  // Send message
  const sendMessage = async (text) => {
    if (!text || !text.trim() || loading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    // If WebSocket is active, prefer WS
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          message: text.trim(),
          conversation_id: conversationId,
        })
      );
    } else {
      // Fallback to HTTP POST
      try {
        const response = await api.sendMessage({
          employee_id: employeeId,
          message: text.trim(),
          conversation_id: conversationId,
        });

        if (response) {
          setMessages((prev) => [
            ...prev,
            {
              id: (Date.now() + 1).toString(),
              role: response.role || 'assistant',
              content: response.message,
              timestamp: new Date().toISOString(),
              intent: response.intent,
              suggested_actions: response.suggested_actions,
              sources: response.sources,
              escalated: response.escalated,
              ticket: response.ticket,
            },
          ]);

          if (response.conversation_id) {
            setConversationId(response.conversation_id);
          }
          loadConversations();
        }
      } catch (err) {
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: `⚠️ Sorry, an error occurred while processing your request: ${err.message}`,
            timestamp: new Date().toISOString(),
          },
        ]);
      } finally {
        setLoading(false);
      }
    }
  };

  return {
    messages,
    loading,
    wsConnected,
    conversationId,
    conversations,
    sendMessage,
    selectConversation,
    startNewConversation,
  };
}
