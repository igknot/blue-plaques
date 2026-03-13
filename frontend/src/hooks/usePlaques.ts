import { useQuery } from '@tanstack/react-query';
import { plaqueApi } from '../services/api';

export const usePlaques = (params?: { page?: number; page_size?: number; search?: string; category_ids?: string }) => {
  return useQuery({
    queryKey: ['plaques', params],
    queryFn: () => plaqueApi.list(params).then(res => res.data),
    placeholderData: (previousData) => previousData,
  });
};

export const usePlaque = (id: number) => {
  return useQuery({
    queryKey: ['plaque', id],
    queryFn: () => plaqueApi.get(id).then(res => res.data),
    enabled: !!id,
  });
};

export const useNearbyPlaques = (lat: number, lng: number, radius?: number) => {
  return useQuery({
    queryKey: ['plaques', 'nearby', lat, lng, radius],
    queryFn: () => plaqueApi.nearby(lat, lng, radius).then(res => res.data),
    enabled: !!lat && !!lng,
  });
};
