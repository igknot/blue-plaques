import { MapContainer, TileLayer, Marker, Popup, Tooltip, ZoomControl } from 'react-leaflet';
import { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { usePlaques } from '../../hooks/usePlaques';
import { useMapStore } from '../../stores/mapStore';
import { useAuthStore } from '../../stores/authStore';
import SearchBar from '../Search/SearchBar';
import FilterPanel from '../Search/FilterPanel';
import api from '../../services/api';
import type { Category } from '../../types/plaque';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet icon paths - use CDN for cross-platform compatibility
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const userIcon = L.icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="red" width="32" height="32">
      <circle cx="12" cy="12" r="8" fill="red" stroke="white" stroke-width="2"/>
      <circle cx="12" cy="12" r="3" fill="white"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 16],
});

export default function Map() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<number[]>([]);
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const { center, zoom } = useMapStore();
  const { isAuthenticated, logout } = useAuthStore();
  
  const { data, isLoading } = usePlaques({
    page_size: 1000,
    search: search || undefined,
    category_ids: selectedCategories.length > 0 ? selectedCategories.join(',') : undefined,
  });

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.get<Category[]>('/categories').then(res => res.data),
  });

  useEffect(() => {
    if (!navigator.geolocation) return;
    const id = navigator.geolocation.watchPosition(
      (position) => {
        setUserLocation([position.coords.latitude, position.coords.longitude]);
      },
      (error) => console.warn('Geolocation error:', error.code, error.message),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
    );
    return () => navigator.geolocation.clearWatch(id);
  }, []);

  const handleCategoryToggle = (categoryId: number) => {
    setSelectedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const handleClearAll = () => {
    setSelectedCategories([]);
  };

  const handleSelectAll = () => {
    setSelectedCategories(categories?.map(c => c.id) || []);
  };

  const markers = useMemo(() => {
    if (!data?.plaques) return [];
    return data.plaques.map((plaque) => (
      <Marker
        key={plaque.id}
        position={[plaque.latitude, plaque.longitude]}
      >
        <Tooltip direction="top" offset={[0, -20]} opacity={0.9}>
          <div className="text-sm font-medium">{plaque.title}</div>
        </Tooltip>
        <Popup>
          <div className="p-2">
            <h3 className="font-bold text-lg">{plaque.title}</h3>
            {plaque.address && <p className="text-sm text-gray-600">{plaque.address}</p>}
            {plaque.images?.[0] && (
              <img src={plaque.images[0].url} alt={plaque.title} className="mt-2 w-full h-32 object-cover rounded" />
            )}
            <button
              onClick={() => navigate(`/plaque/${plaque.id}`)}
              className="mt-2 text-blue-600 hover:underline text-sm"
            >
              View Details →
            </button>
          </div>
        </Popup>
      </Marker>
    ));
  }, [data?.plaques, navigate]);

  if (isLoading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading map...</p>
      </div>
    </div>
  );

  return (
    <div className="relative h-screen w-full">
      <SearchBar onSearch={setSearch} />
      <FilterPanel 
        selectedCategories={selectedCategories}
        onCategoryToggle={handleCategoryToggle}
        onClearAll={handleClearAll}
        onSelectAll={handleSelectAll}
      />
      <button
        onClick={() => isAuthenticated ? logout() : navigate('/login')}
        className="absolute top-4 right-16 z-[1000] bg-white px-3 py-1.5 rounded shadow text-sm font-medium hover:bg-gray-50"
      >
        {isAuthenticated ? 'Logout' : 'Admin'}
      </button>
      
      <MapContainer
        center={center}
        zoom={zoom}
        className="h-full w-full"
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        <ZoomControl position="bottomright" />
        {markers}
        {userLocation && (
          <Marker position={userLocation} icon={userIcon}>
            <Popup>You are here</Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
