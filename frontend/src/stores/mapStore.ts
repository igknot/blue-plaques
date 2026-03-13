import { create } from 'zustand';

interface MapState {
  center: [number, number];
  zoom: number;
  selectedPlaqueId: number | null;
  setCenter: (center: [number, number]) => void;
  setZoom: (zoom: number) => void;
  setSelectedPlaque: (id: number | null) => void;
}

export const useMapStore = create<MapState>((set) => ({
  center: [-26.2041, 28.0473], // Johannesburg
  zoom: 12,
  selectedPlaqueId: null,
  setCenter: (center) => set({ center }),
  setZoom: (zoom) => set({ zoom }),
  setSelectedPlaque: (id) => set({ selectedPlaqueId: id }),
}));
