/**
 * Bug Condition Exploration Test - Admin Email Login
 * 
 * Property 1: Bug Condition - Missing Email/Password Login Form
 * 
 * CRITICAL: This test MUST FAIL on unfixed code - failure confirms the bug exists
 * DO NOT attempt to fix the test or the code when it fails
 * 
 * This test encodes the expected behavior - it will validate the fix when it passes after implementation
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useAuthStore } from '../stores/authStore';

// Mock supabase
vi.mock('../lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn().mockResolvedValue({ data: { session: null } }),
      onAuthStateChange: vi.fn(),
      signInWithOAuth: vi.fn(),
      signOut: vi.fn(),
    },
  },
}));

describe('Bug Condition Exploration: Admin Email Login', () => {
  beforeEach(() => {
    // Reset the store state before each test
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      loading: true,
    });
  });

  describe('Property 1: Bug Condition - Missing loginWithEmail method', () => {
    it('should have loginWithEmail method in authStore', () => {
      const store = useAuthStore.getState();
      
      // This test will FAIL on unfixed code because loginWithEmail doesn't exist
      // When it passes after the fix, it confirms the bug is resolved
      expect(typeof store.loginWithEmail).toBe('function');
    });

    it('should have error state in authStore', () => {
      const store = useAuthStore.getState();
      
      // This test will FAIL on unfixed code because error state doesn't exist
      expect('error' in store).toBe(true);
    });

    it('should have clearError method in authStore', () => {
      const store = useAuthStore.getState();
      
      // This test will FAIL on unfixed code because clearError doesn't exist
      expect(typeof store.clearError).toBe('function');
    });
  });
});
