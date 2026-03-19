import { MapContainer, TileLayer, Marker, Popup, Tooltip, ZoomControl } from 'react-leaflet';
import { useState, useMemo, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { usePlaques } from '../../hooks/usePlaques';
import { useMapStore } from '../../stores/mapStore';
import { useAuthStore } from '../../stores/authStore';
import { useUserPlaqueStore } from '../../stores/userPlaqueStore';
import { plaqueApi } from '../../services/api';
import SearchBar from '../Search/SearchBar';
import FilterPanel from '../Search/FilterPanel';
import api from '../../services/api';
import type { Category, Plaque } from '../../types/plaque';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet icon paths
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

function makeSvgIcon(color: string) {
  return L.icon({
    iconUrl: 'data:image/svg+xml;base64,' + btoa(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 25 41" width="25" height="41">
        <path d="M12.5 0C5.6 0 0 5.6 0 12.5C0 21.9 12.5 41 12.5 41S25 21.9 25 12.5C25 5.6 19.4 0 12.5 0z" fill="${color}" stroke="#fff" stroke-width="1.5"/>
        <circle cx="12.5" cy="12.5" r="5" fill="#fff"/>
      </svg>
    `),
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    shadowSize: [41, 41],
  });
}

const blueIcon = makeSvgIcon('#2563eb');
const greenIcon = makeSvgIcon('#16a34a');
const orangeIcon = makeSvgIcon('#ea580c');

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

interface ConfirmMoveDialogProps {
  plaque: Plaque;
  newLat: number;
  newLng: number;
  onConfirm: () => void;
  onCancel: () => void;
}

function ConfirmMoveDialog({ plaque, newLat, newLng, onConfirm, onCancel }: ConfirmMoveDialogProps) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-[2000]" onClick={onCancel}>
      <div className="bg-white rounded-lg p-6 max-w-sm mx-4 shadow-xl" onClick={e => e.stopPropagation()}>
        <h3 className="font-bold text-lg mb-2">Move Plaque?</h3>
        <p className="text-gray-600 mb-1">"{plaque.title}"</p>
        <p className="text-sm text-gray-500 mb-4">
          New position: {newLat.toFixed(6)}, {newLng.toFixed(6)}
        </p>
        <div className="flex gap-3 justify-end">
          <button onClick={onCancel} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">Cancel</button>
          <button onClick={onConfirm} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Confirm</button>
        </div>
      </div>
    </div>
  );
}

function DraggableMarker({ plaque, icon, onDragEnd, markerRefs, children }: { plaque: Plaque; icon: L.Icon; onDragEnd: (lat: number, lng: number) => void; markerRefs: React.MutableRefObject<Map<number, L.Marker>>; children: React.ReactNode }) {
  const setRef = useCallback((marker: L.Marker | null) => {
    if (marker) markerRefs.current.set(plaque.id, marker);
    else markerRefs.current.delete(plaque.id);
  }, [plaque.id, markerRefs]);

  const handleDragEnd = useCallback((e: L.DragEndEvent) => {
    const { lat, lng } = e.target.getLatLng();
    onDragEnd(lat, lng);
  }, [onDragEnd]);

  return (
    <Marker ref={setRef} position={[plaque.latitude, plaque.longitude]} icon={icon} draggable eventHandlers={{ dragend: handleDragEnd }}>
      {children}
    </Marker>
  );
}

function PlaqueActions({ plaque }: { plaque: Plaque }) {
  const { user } = useAuthStore();
  const { visitedIds, favoriteIds, toggleVisited, toggleFavorite } = useUserPlaqueStore();
  if (!user) return null;

  const isVisited = visitedIds.has(plaque.id);
  const isFavorite = favoriteIds.has(plaque.id);

  return (
    <div className="flex gap-2 mt-2">
      <button
        onClick={(e) => { e.stopPropagation(); toggleVisited(user.id, plaque.id); }}
        className={`text-xs px-2 py-1 rounded ${isVisited ? 'bg-green-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-green-50'}`}
      >
        {isVisited ? '✓ Visited' : 'Mark Visited'}
      </button>
      <button
        onClick={(e) => { e.stopPropagation(); toggleFavorite(user.id, plaque.id); }}
        className={`text-xs px-2 py-1 rounded ${isFavorite ? 'bg-orange-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-orange-50'}`}
      >
        {isFavorite ? '★ Want to Visit' : '☆ Want to Visit'}
      </button>
    </div>
  );
}

export default function Map() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<number[]>([]);
  const [userLocation, setUserLocation] = useState<[number, number] | null>(null);
  const [pendingMove, setPendingMove] = useState<{ plaque: Plaque; lat: number; lng: number } | null>(null);
  const markerRefs = useRef(new window.Map<number, L.Marker>());
  const { center, zoom } = useMapStore();
  const { user, isAuthenticated, logout, loginWithGoogle, init } = useAuthStore();
  const { visitedIds, favoriteIds, fetchUserPlaques, clear } = useUserPlaqueStore();

  // Init auth on mount
  useEffect(() => { init(); }, [init]);

  // Fetch user plaques when logged in
  useEffect(() => {
    if (user) fetchUserPlaques(user.id);
    else clear();
  }, [user, fetchUserPlaques, clear]);

  const confirmMove = async () => {
    if (!pendingMove) return;
    try {
      await plaqueApi.update(pendingMove.plaque.id, { latitude: pendingMove.lat, longitude: pendingMove.lng });
      queryClient.invalidateQueries({ queryKey: ['plaques'] });
    } catch (e) {
      console.error('Failed to move plaque:', e);
    }
    setPendingMove(null);
  };

  const cancelMove = () => {
    if (pendingMove) {
      const marker = markerRefs.current.get(pendingMove.plaque.id);
      if (marker) marker.setLatLng([pendingMove.plaque.latitude, pendingMove.plaque.longitude]);
    }
    setPendingMove(null);
  };
  
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
      (position) => setUserLocation([position.coords.latitude, position.coords.longitude]),
      (error) => console.warn('Geolocation error:', error.code, error.message),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
    );
    return () => navigator.geolocation.clearWatch(id);
  }, []);

  const handleCategoryToggle = (categoryId: number) => {
    setSelectedCategories(prev =>
      prev.includes(categoryId) ? prev.filter(id => id !== categoryId) : [...prev, categoryId]
    );
  };

  const handleClearAll = () => setSelectedCategories([]);
  const handleSelectAll = () => setSelectedCategories(categories?.map(c => c.id) || []);

  const getIcon = useCallback((plaqueId: number) => {
    if (visitedIds.has(plaqueId)) return greenIcon;
    if (favoriteIds.has(plaqueId)) return orangeIcon;
    return blueIcon;
  }, [visitedIds, favoriteIds]);

  const markers = useMemo(() => {
    if (!data?.plaques) return [];
    return data.plaques.map((plaque) => {
      const icon = getIcon(plaque.id);
      const popupContent = (
        <>
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
              <div className="mt-2 flex items-center gap-3">
                <button onClick={() => navigate(`/plaque/${plaque.id}`)} className="text-blue-600 hover:underline text-sm">
                  View Details →
                </button>
                {isAuthenticated && userLocation && (
                  <button
                    onClick={() => setPendingMove({ plaque, lat: userLocation[0], lng: userLocation[1] })}
                    className="text-orange-600 hover:underline text-sm"
                  >
                    Move Here ↗
                  </button>
                )}
              </div>
              <PlaqueActions plaque={plaque} />
            </div>
          </Popup>
        </>
      );

      if (isAuthenticated) {
        return (
          <DraggableMarker key={plaque.id} plaque={plaque} icon={icon} markerRefs={markerRefs} onDragEnd={(lat, lng) => setPendingMove({ plaque, lat, lng })}>
            {popupContent}
          </DraggableMarker>
        );
      }
      return (
        <Marker key={plaque.id} position={[plaque.latitude, plaque.longitude]} icon={icon}>
          {popupContent}
        </Marker>
      );
    });
  }, [data?.plaques, navigate, isAuthenticated, userLocation, getIcon]);

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

      {/* Auth button + user info */}
      <div className="absolute top-4 right-16 z-[1000] flex items-center gap-2">
        {user && (
          <div className="bg-white px-3 py-1.5 rounded shadow text-sm flex items-center gap-2">
            {user.user_metadata?.avatar_url && (
              <img src={user.user_metadata.avatar_url} alt="" className="w-6 h-6 rounded-full" />
            )}
            <span className="text-gray-700 hidden sm:inline">{user.user_metadata?.full_name || user.email}</span>
            <span className="text-xs text-green-600 font-medium">{visitedIds.size}/{data?.total ?? '?'}</span>
          </div>
        )}
        <button
          onClick={() => isAuthenticated ? logout() : loginWithGoogle()}
          className="bg-white px-3 py-1.5 rounded shadow text-sm font-medium hover:bg-gray-50"
        >
          {isAuthenticated ? 'Logout' : 'Login'}
        </button>
      </div>

      {/* Legend */}
      {user && (
        <div className="absolute bottom-8 left-4 z-[1000] bg-white rounded shadow px-3 py-2 text-xs space-y-1">
          <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-blue-600 inline-block"></span> Not visited</div>
          <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-green-600 inline-block"></span> Visited</div>
          <div className="flex items-center gap-2"><span className="w-3 h-3 rounded-full bg-orange-600 inline-block"></span> Want to visit</div>
        </div>
      )}

      {/* Version */}
      <div className={`absolute ${user ? 'bottom-28' : 'bottom-8'} left-4 z-[1000] text-[10px] text-gray-400`}>
        v{import.meta.env.VITE_APP_VERSION || 'dev'}
      </div>
      <MapContainer center={center} zoom={zoom} className="h-full w-full" zoomControl={false}>
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

      {pendingMove && (
        <ConfirmMoveDialog
          plaque={pendingMove.plaque}
          newLat={pendingMove.lat}
          newLng={pendingMove.lng}
          onConfirm={confirmMove}
          onCancel={cancelMove}
        />
      )}
    </div>
  );
}
