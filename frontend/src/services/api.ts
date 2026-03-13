import axios from 'axios';
import type { Plaque, PlaqueListResponse } from '../types/plaque';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const plaqueApi = {
  list: (params?: { page?: number; page_size?: number; search?: string; category_ids?: string }) =>
    api.get<PlaqueListResponse>('/plaques', { params }),
  
  get: (id: number) =>
    api.get<Plaque>(`/plaques/${id}`),
  
  nearby: (lat: number, lng: number, radius?: number) =>
    api.get<Plaque[]>('/plaques/nearby', { params: { lat, lng, radius } }),
  
  create: (data: Partial<Plaque>) =>
    api.post<Plaque>('/plaques', data),
  
  update: (id: number, data: Partial<Plaque>) =>
    api.put<Plaque>(`/plaques/${id}`, data),
  
  delete: (id: number) =>
    api.delete(`/plaques/${id}`),
};

export const authApi = {
  login: (email: string, password: string) =>
    api.post<{ access_token: string; token_type: string }>('/auth/login', { email, password }),
};

export default api;
