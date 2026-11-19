const ApiClient = {
  getToken() {
    return localStorage.getItem('cp_token');
  },

  getUser() {
    const raw = localStorage.getItem('cp_user');
    return raw ? JSON.parse(raw) : null;
  },

  setSession(token, user) {
    localStorage.setItem('cp_token', token);
    localStorage.setItem('cp_user', JSON.stringify(user));
  },

  clearSession() {
    localStorage.removeItem('cp_token');
    localStorage.removeItem('cp_user');
  },

  async request(endpoint, options = {}) {
    const headers = options.headers || {};
    const token = this.getToken();

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.detail || `Request failed (${response.status})`);
    }
    return data;
  },

  // Auth
  login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  register(name, email, password) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  },

  // Complaints
  async getComplaints(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v && v !== 'all') query.append(k, v);
    });
    const qs = query.toString() ? `?${query.toString()}` : '';

    try {
      return await this.request(`/complaints${qs}`);
    } catch (err) {
      if (CONFIG.USE_MOCK_FALLBACK) {
        let list = [...CONFIG.MOCK_COMPLAINTS];
        if (params.category_id && params.category_id !== 'all') {
          list = list.filter((c) => String(c.category_id) === String(params.category_id));
        }
        if (params.status && params.status !== 'all') {
          list = list.filter((c) => c.status === params.status);
        }
        return list;
      }
      throw err;
    }
  },

  async getComplaintById(id) {
    try {
      return await this.request(`/complaints/${id}`);
    } catch (err) {
      if (CONFIG.USE_MOCK_FALLBACK) {
        const found = CONFIG.MOCK_COMPLAINTS.find((c) => String(c.complaint_id) === String(id));
        if (found) return found;
      }
      throw err;
    }
  },

  createComplaint(formData) {
    return this.request('/complaints', {
      method: 'POST',
      body: formData,
    });
  },

  voteComplaint(id) {
    return this.request(`/complaints/${id}/vote`, {
      method: 'POST',
    });
  },

  reopenComplaint(id) {
    return this.request(`/complaints/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status: 'reopened' }),
    });
  },

  async getAnalytics() {
    try {
      return await this.request('/analytics');
    } catch (err) {
      if (CONFIG.USE_MOCK_FALLBACK) {
        return CONFIG.MOCK_ANALYTICS;
      }
      throw err;
    }
  },
};