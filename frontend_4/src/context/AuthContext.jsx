import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getAccessToken,
  getUserEmail,
  isTokenExpired,
  saveTokens,
  clearTokens,
  apiLogin,
  apiRegister,
  apiLogout,
} from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Check auth state on mount
  useEffect(() => {
    const token = getAccessToken();
    if (token && !isTokenExpired(token)) {
      setUser({ email: getUserEmail() });
    }
    setLoading(false);
  }, []);

  // Listen for auth:expired events (fired by api.js)
  useEffect(() => {
    const handler = () => {
      setUser(null);
      navigate('/login');
    };
    window.addEventListener('auth:expired', handler);
    return () => window.removeEventListener('auth:expired', handler);
  }, [navigate]);

  const login = useCallback(async (email, password) => {
    const data = await apiLogin(email, password);
    saveTokens(data.access_token, data.refresh_token);
    setUser({ email });
    navigate('/dashboard');
    return data;
  }, [navigate]);

  const register = useCallback(async (email, password) => {
    await apiRegister(email, password);
    // Auto-login after register
    return login(email, password);
  }, [login]);

  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
    navigate('/');
  }, [navigate]);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
