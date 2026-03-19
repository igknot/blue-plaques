/**
 * Preservation Property Tests - Admin Email Login
 * 
 * Property 2: Preservation - Google OAuth and Session Management
 * 
 * IMPORTANT: Follow observation-first methodology
 * These tests capture the existing behavior that MUST be preserved after the fix
 * 
 * Run on UNFIXED code first to confirm baseline behavior
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useAuthStore } from '../stores/authStore';
import { supabase } from '../lib/supabase';

// Mock supabase
vi.mock('../lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: null } }),
      onAuthStateChange: vi.fn(),
      signInWithOAuth: vi.fn().mockResolvedValue({ data: {}, error: null }),
      signOut: vi.fn().mockResolvedValue({ error: null }),
    },
  },
}));

describe('Preservation Property Tests: Google OAuth and Session Management', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset the store state before each test
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      loading: true,
    });
  });

  describe('Requirement 3.1: Google OAuth login continues to work', () => {
    it('loginWithGoogle should call supabase.auth.signInWithOAuth with provider google', async () => {
      const store = useAuthStore.getState();
      
      await store.loginWithGoogle();
      
      expect(supabase.auth.signInWithOAuth).toHaveBeenCalledWith({
        provider: 'google',
        options: { redirectTo: 'http://localhost:3000' },
      });
    });

    it('loginWithGoogle should be a function', () => {
      const store = useAuthStore.getState();
      expect(typeof store.loginWithGoogle).toBe('function');
    });
  });

  describe('Requirement 3.2: Logout continues to work', () => {
    it('logout should call supabase.auth.signOut', async () => {
      const store = useAuthStore.getState();
      
      await store.logout();
      
      expect(supabase.auth.signOut).toHaveBeenCalled();
    });

    it('logout should clear auth state', async () => {
      // Set authenticated state first
      useAuthStore.setState({
        user: { id: 'test-user' } as any,
        isAuthenticated: true,
        loading: false,
      });
      
      const store = useAuthStore.getState();
      await store.logout();
      
      const newState = useAuthStore.getState();
      expect(newState.user).toBeNull();
      expect(newState.isAuthenticated).toBe(false);
    });
  });

  describe('Requirement 3.3: Session restoration continues to work', () => {
    it('init should call supabase.auth.getSession', async () => {
      const store = useAuthStore.getState();
      
      await store.init();
      
      expect(supabase.auth.getSession).toHaveBeenCalled();
    });

    it('init should set up onAuthStateChange listener', async () => {
      const store = useAuthStore.getState();
      
      await store.init();
      
      expect(supabase.auth.onAuthStateChange).toHaveBeenCalled();
    });

    it('init should set loading to false after completion', async () => {
      const store = useAuthStore.getState();
      
      await store.init();
      
      const newState = useAuthStore.getState();
      expect(newState.loading).toBe(false);
    });
  });

  describe('State structure preservation', () => {
    it('should have user state', () => {
      const store = useAuthStore.getState();
      expect('user' in store).toBe(true);
    });

    it('should have isAuthenticated state', () => {
      const store = useAuthStore.getState();
      expect('isAuthenticated' in store).toBe(true);
    });

    it('should have loading state', () => {
      const store = useAuthStore.getState();
      expect('loading' in store).toBe(true);
    });
  });
});
