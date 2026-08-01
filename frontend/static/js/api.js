const API_BASE = '/api';

const Auth = {
  getAccess() { return localStorage.getItem('access'); },
  getRefresh() { return localStorage.getItem('refresh'); },
  getUser() {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  },
  setSession(access, refresh, user) {
    localStorage.setItem('access', access);
    if (refresh) localStorage.setItem('refresh', refresh);
    if (user) localStorage.setItem('user', JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user');
  },
  isLoggedIn() { return !!this.getAccess(); },
  requireLogin() {
    if (!this.isLoggedIn()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
  },
};

async function apiFetch(path, options = {}) {
  const opts = { ...options };
  opts.headers = { ...(options.headers || {}) };

  const isFormData = opts.body instanceof FormData;
  if (!isFormData && opts.body && typeof opts.body !== 'string') {
    opts.body = JSON.stringify(opts.body);
    opts.headers['Content-Type'] = 'application/json';
  }

  const access = Auth.getAccess();
  if (access) opts.headers['Authorization'] = `Bearer ${access}`;

  let response = await fetch(`${API_BASE}${path}`, opts);

  if (response.status === 401 && Auth.getRefresh()) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      opts.headers['Authorization'] = `Bearer ${Auth.getAccess()}`;
      response = await fetch(`${API_BASE}${path}`, opts);
    }
  }

  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json') ? await response.json() : null;

  if (!response.ok) {
    const error = new Error(extractErrorMessage(data) || `Request failed (${response.status})`);
    error.status = response.status;
    error.data = data;
    throw error;
  }
  return data;
}

async function tryRefreshToken() {
  try {
    const res = await fetch(`${API_BASE}/auth/login/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: Auth.getRefresh() }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    Auth.setSession(data.access, null, null);
    return true;
  } catch {
    return false;
  }
}

function extractErrorMessage(data) {
  if (!data) return null;
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  if (data.non_field_errors) return data.non_field_errors.join(' ');
  const firstKey = Object.keys(data)[0];
  if (firstKey) {
    const value = data[firstKey];
    return `${firstKey}: ${Array.isArray(value) ? value.join(' ') : value}`;
  }
  return null;
}

function showToast(message, type = 'error', duration = 4000) {
  const container = document.getElementById('toast-container');
  if (!container) {
    // Fallback if a page forgets the container - still surface the message.
    window.alert(message);
    return;
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add('show'));
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 200);
  }, duration);
}

function showLoadError(mount, err, placeholder = 'Unable to load this data.') {
  if (mount) mount.innerHTML = `<p class="muted">${placeholder}</p>`;
  showToast(err.message || placeholder, 'error');
}

function renderNav() {
  const mount = document.getElementById('site-nav');
  if (!mount) return;
  const user = Auth.getUser();

  let links = `<a href="products.html">Products</a>`;
  if (user) {
    if (user.role === 'user') {
      links += `<a href="cart.html">Cart</a><a href="orders.html">My Orders</a>`;
    } else if (user.role === 'admin') {
      links += `<a href="vendor.html">Vendor Dashboard</a>`;
    } else if (user.role === 'super_admin') {
      links += `<a href="admin-dashboard.html">Admin Dashboard</a>`;
    }
    links += `<span class="muted">Hi, ${user.username} (${user.role})</span>`;
    links += `<button class="btn secondary" id="logout-btn">Logout</button>`;
  } else {
    links += `<a href="login.html">Login</a><a href="register.html" class="btn">Register</a>`;
  }
  mount.innerHTML = links;

  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      Auth.clear();
      window.location.href = 'login.html';
    });
  }
}

document.addEventListener('DOMContentLoaded', renderNav);
