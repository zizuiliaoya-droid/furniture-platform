import { create } from 'zustand';
import { authService } from '../services/authService';

interface User {
  id: number;
  username: string;
  display_name: string;
  role: 'ADMIN' | 'STAFF';
  is_active: boolean;
}

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  isAuthenticated: !!localStorage.getItem('token'),

  login: async (username, password) => {
    const { data } = await authService.login(username, password);
    localStorage.setItem('token', data.token);
    localStorage.setItem('user', JSON.stringify(data.user));
    set({ token: data.token, user: data.user, isAuthenticated: true });
  },

  logout: async () => {
    try { await authService.logout(); } catch {}
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ token: null, user: null, isAuthenticated: false });
  },

  checkAuth: async () => {
    try {
      const { data } = await authService.getMe();
      localStorage.setItem('user', JSON.stringify(data));
      set({ user: data, isAuthenticated: true });
    } catch {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      set({ token: null, user: null, isAuthenticated: false });
    }
  },
}));
