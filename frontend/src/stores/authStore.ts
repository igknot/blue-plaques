import { create } from 'zustand';
import { supabase } from '../lib/supabase';
import { authApi } from '../services/api';
import type { User } from '@supabase/supabase-js';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  loading: boolean;
  error: string | null;
  init: () => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  loginWithEmail: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
}

function parseJwtClaims(token: string): Record<string, unknown> | null {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch { return null; }
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isAdmin: false,
  loading: true,
  error: null,

  init: async () => {
    // Check for existing JWT token from email login
    const token = localStorage.getItem('token');
    if (token) {
      const claims = parseJwtClaims(token);
      set({ isAuthenticated: true, isAdmin: !!claims?.is_admin, loading: false });
      return;
    }

    // Check for Supabase session (Google OAuth)
    const { data: { session } } = await supabase.auth.getSession();
    set({ user: session?.user ?? null, isAuthenticated: !!session, loading: false });

    supabase.auth.onAuthStateChange((_event, session) => {
      set({ user: session?.user ?? null, isAuthenticated: !!session, loading: false });
    });
  },

  loginWithGoogle: async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: window.location.origin },
    });
  },

  loginWithEmail: async (email: string, password: string) => {
    set({ error: null });
    try {
      const response = await authApi.login(email, password);
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      const claims = parseJwtClaims(access_token);
      set({ isAuthenticated: true, isAdmin: !!claims?.is_admin, error: null });
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Login failed. Please check your credentials.';
      set({ error: message });
      throw err;
    }
  },

  logout: async () => {
    // Clear JWT token from localStorage
    localStorage.removeItem('token');
    // Also sign out from Supabase (for Google OAuth users)
    await supabase.auth.signOut();
    set({ user: null, isAuthenticated: false, isAdmin: false });
  },

  clearError: () => {
    set({ error: null });
  },
}));
