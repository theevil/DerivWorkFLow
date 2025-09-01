import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UserResponse } from '@deriv-workflow/shared';
import { api } from '../lib/api';

interface AuthState {
  user: UserResponse | null;
  token: string | null;
  setAuth: (token: string, user: UserResponse) => void;
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
