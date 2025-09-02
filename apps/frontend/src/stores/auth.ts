import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '../types/trading';
import { api } from '../lib/api';

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  setAuth: (token: string, refreshToken: string, user: User) => void;
  clearAuth: () => void;
  isAuthenticated: boolean;
  initializeAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      setAuth: (token, refreshToken, user) => {
        api.setToken(token);
        set({ token, refreshToken, user, isAuthenticated: true });
      },
      clearAuth: () => {
        api.clearToken();
        set({
          token: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
        });
      },
      initializeAuth: () => {
        const { token, refreshToken } = get();
        if (token) {
          api.setToken(token);
        }
        if (refreshToken) {
          api.setRefreshToken(refreshToken);
        }
      },
    }),
    {
      name: 'auth-storage',
      onRehydrateStorage: () => state => {
        // When store is rehydrated from localStorage, set the tokens in API client
        if (state?.token) {
          api.setToken(state.token);
        }
        if (state?.refreshToken) {
          api.setRefreshToken(state.refreshToken);
        }
      },
    }
  )
);
