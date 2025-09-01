import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../types/trading';
import { api } from '../lib/api';

interface AuthState {
  user: User | null;
  token: string | null;
  setAuth: (token: string, user: User) => void;
  clearAuth: () => void;
  isAuthenticated: boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setAuth: (token, user) => {
        api.setToken(token);
        set({ token, user, isAuthenticated: true });
      },
      clearAuth: () => {
        api.clearToken();
        set({ token: null, user: null, isAuthenticated: false });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
