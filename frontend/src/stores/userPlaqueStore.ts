import { create } from 'zustand';
import { supabase } from '../lib/supabase';

interface UserPlaqueState {
  visitedIds: Set<number>;
  favoriteIds: Set<number>;
  loading: boolean;
  fetchUserPlaques: (userId: string) => Promise<void>;
  toggleVisited: (userId: string, plaqueId: number) => Promise<void>;
  toggleFavorite: (userId: string, plaqueId: number) => Promise<void>;
  clear: () => void;
}

export const useUserPlaqueStore = create<UserPlaqueState>((set, get) => ({
  visitedIds: new Set(),
  favoriteIds: new Set(),
  loading: false,

  fetchUserPlaques: async (userId) => {
    set({ loading: true });
    const [visited, favorites] = await Promise.all([
      supabase.from('visited_plaques').select('plaque_id').eq('user_id', userId),
      supabase.from('favorites').select('plaque_id').eq('user_id', userId),
    ]);
    set({
      visitedIds: new Set((visited.data ?? []).map((r) => r.plaque_id)),
      favoriteIds: new Set((favorites.data ?? []).map((r) => r.plaque_id)),
      loading: false,
    });
  },

  toggleVisited: async (userId, plaqueId) => {
    const { visitedIds, favoriteIds } = get();
    if (visitedIds.has(plaqueId)) {
      await supabase.from('visited_plaques').delete().eq('user_id', userId).eq('plaque_id', plaqueId);
      const next = new Set(visitedIds);
      next.delete(plaqueId);
      set({ visitedIds: next });
    } else {
      await supabase.from('visited_plaques').insert({ user_id: userId, plaque_id: plaqueId });
      // Remove from favorites if marking as visited
      if (favoriteIds.has(plaqueId)) {
        await supabase.from('favorites').delete().eq('user_id', userId).eq('plaque_id', plaqueId);
        const nextFav = new Set(favoriteIds);
        nextFav.delete(plaqueId);
        set({ favoriteIds: nextFav });
      }
      set({ visitedIds: new Set(visitedIds).add(plaqueId) });
    }
  },

  toggleFavorite: async (userId, plaqueId) => {
    const { favoriteIds } = get();
    if (favoriteIds.has(plaqueId)) {
      await supabase.from('favorites').delete().eq('user_id', userId).eq('plaque_id', plaqueId);
      const next = new Set(favoriteIds);
      next.delete(plaqueId);
      set({ favoriteIds: next });
    } else {
      await supabase.from('favorites').insert({ user_id: userId, plaque_id: plaqueId });
      set({ favoriteIds: new Set(favoriteIds).add(plaqueId) });
    }
  },

  clear: () => set({ visitedIds: new Set(), favoriteIds: new Set() }),
}));
