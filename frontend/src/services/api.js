/**
 * API client service for communicating with the FastAPI backend.
 */

const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  try {
    const response = await fetch(url, { ...options, headers });
    const json = await response.json();

    if (!response.ok || json.success === false) {
      throw new Error(json.error || `HTTP error ${response.status}`);
    }

    return json.data;
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // Chat
  sendMessage: (payload) =>
    request('/chat/message', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  getConversations: (employeeId) =>
    request(`/chat/conversations/${employeeId}`),

  getConversation: (conversationId) =>
    request(`/chat/conversation/${conversationId}`),

  // Tickets
  getTickets: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.status) query.append('status', params.status);
    if (params.priority) query.append('priority', params.priority);
    if (params.category) query.append('category', params.category);
    if (params.employee_id) query.append('employee_id', params.employee_id);
    if (params.search) query.append('search', params.search);
    if (params.skip) query.append('skip', params.skip);
    if (params.limit) query.append('page_size', params.limit);
    if (params.page_size) query.append('page_size', params.page_size);
    if (params.page) query.append('page', params.page);
    const queryString = query.toString() ? `?${query.toString()}` : '';
    const data = await request(`/tickets${queryString}`);
    return Array.isArray(data) ? data : (data?.tickets || []);
  },

  getTicket: (ticketId) =>
    request(`/tickets/${ticketId}`),

  createTicket: (payload) =>
    request('/tickets', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateTicket: (ticketId, payload) =>
    request(`/tickets/${ticketId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    }),

  getTicketStats: () =>
    request('/tickets/stats'),

  // Audit Logs
  getAuditLogs: async (params = {}) => {
    const query = new URLSearchParams();
    if (params.action_type) query.append('action_type', params.action_type);
    if (params.actor) query.append('actor', params.actor);
    if (params.skip) query.append('skip', params.skip);
    if (params.limit) query.append('page_size', params.limit);
    if (params.page_size) query.append('page_size', params.page_size);
    if (params.page) query.append('page', params.page);
    const queryString = query.toString() ? `?${query.toString()}` : '';
    const data = await request(`/audit${queryString}`);
    return Array.isArray(data) ? data : (data?.logs || []);
  },

  getAuditEntry: (auditId) =>
    request(`/audit/${auditId}`),

  // Health
  getHealth: async () => {
    const response = await fetch('/health');
    return response.json();
  }
};
