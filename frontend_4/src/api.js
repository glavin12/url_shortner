/* ============================================================
   API Layer — Handles all backend communication
   Token storage, auto-refresh, and auth error handling
   ============================================================ */

const API_BASE = 'https://pretty-laughter-production.up.railway.app';

/* --- Token helpers --- */
export function getAccessToken() {
  return localStorage.getItem('access_token');
}

export function getRefreshToken() {
  return localStorage.getItem('refresh_token');
}

export function getUserEmail() {
  const token = getAccessToken();
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.sub;
  } catch {
    return null;
  }
}

export function saveTokens(access, refresh) {
  localStorage.setItem('access_token', access);
  if (refresh) localStorage.setItem('refresh_token', refresh);
}

export function clearTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

export function isTokenExpired(token) {
  if (!token) return true;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

/* --- Core fetch wrapper --- */
async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const headers = { ...options.headers };

  if (options.auth !== false) {
    let token = getAccessToken();

    // Auto-refresh if expired
    if (isTokenExpired(token)) {
      const refreshed = await tryRefreshToken();
      if (!refreshed) {
        clearTokens();
        window.dispatchEvent(new Event('auth:expired'));
        throw new Error('Session expired. Please log in again.');
      }
      token = getAccessToken();
    }

    headers['Authorization'] = `Bearer ${token}`;
  }

  if (options.json !== undefined) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.json);
  }

  const res = await fetch(url, {
    ...options,
    headers,
    json: undefined,
  });

  if (res.status === 401) {
    clearTokens();
    window.dispatchEvent(new Event('auth:expired'));
    throw new Error('Unauthorized. Please log in again.');
  }

  if (res.status === 429) {
    throw new Error('Too many requests. Please slow down.');
  }

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Request failed (${res.status})`);
  }

  const text = await res.text();
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

/* --- Token refresh --- */
async function tryRefreshToken() {
  const refresh = getRefreshToken();
  if (!refresh || isTokenExpired(refresh)) return false;

  try {
    const res = await fetch(`${API_BASE}/refresh_token`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${refresh}`,
      },
    });

    if (!res.ok) return false;

    const data = await res.json();
    saveTokens(data.access_token, null);
    return true;
  } catch {
    return false;
  }
}

/* ============================================================
   AUTH API
   ============================================================ */
export async function apiRegister(email, password) {
  return apiFetch('/register', {
    method: 'POST',
    json: { email, password },
    auth: false,
  });
}

export async function apiLogin(email, password) {
  return apiFetch('/login', {
    method: 'POST',
    json: { email, password },
    auth: false,
  });
}

export async function apiLogout() {
  const refresh = getRefreshToken();
  if (!refresh) return;

  try {
    await fetch(`${API_BASE}/logout`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${refresh}`,
      },
    });
  } catch {
    // Ignore errors, we're logging out anyway
  }
  clearTokens();
}

/* ============================================================
   URL SHORTENER API
   ============================================================ */
export async function apiShortenUrl(url, customAlias = null) {
  const body = { url };
  if (customAlias) {
    body.custom_alias = customAlias;
  }
  return apiFetch('/shortner', {
    method: 'POST',
    json: body,
  });
}

export async function apiGetAllUrls(email, page = 1, size = 10) {
  return apiFetch(`/${email}/get_all_urls?page=${page}&size=${size}`);
}

export async function apiDeleteUrl(shortUrl) {
  return apiFetch(`/delete/${shortUrl}`, {
    method: 'DELETE',
  });
}

export async function apiDeleteAllUrls(email) {
  return apiFetch(`/${email}/delete_all_urls`, {
    method: 'DELETE',
  });
}

export async function apiGetAnalytics(shortUrl, page = 1, size = 10) {
  return apiFetch(`/analytics/${shortUrl}?page=${page}&size=${size}`);
}
