# Frontend Architecture - Blue Plaques Map

**Part:** frontend
**Type:** Web Application
**Framework:** React 18 + Vite + TypeScript

## Technology Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| UI Framework | React | 18.2.0 | Component-based UI |
| Build Tool | Vite | 5.1.0 | Fast dev server & bundling |
| Language | TypeScript | 5.3.3 | Type safety |
| Styling | Tailwind CSS | 3.4.1 | Utility-first CSS |
| State Management | Zustand | 4.5.0 | Lightweight global state |
| Data Fetching | TanStack React Query | 5.20.0 | Server state management |
| Routing | React Router DOM | 6.22.0 | Client-side routing |
| Mapping | Leaflet + react-leaflet | 1.9.4 / 4.2.1 | Interactive maps |
| HTTP Client | Axios | 1.6.7 | API requests |
| Auth | Supabase JS | 2.99.2 | OAuth authentication |
| Unit Testing | Vitest | 1.2.2 | Fast unit tests |
| E2E Testing | Playwright | 1.42.0 | Browser automation |

## Architecture Pattern

**Component-Based Architecture** with:
- Functional components with hooks
- Zustand for global state (auth, map, user plaques)
- React Query for server state caching
- Axios for API communication

## Directory Structure

```
frontend/
├── src/
│   ├── components/           # React components
│   │   ├── Admin/           # Admin-only components
│   │   │   └── LoginPage.tsx
│   │   ├── Gallery/         # Image gallery
│   │   │   └── Lightbox.tsx
│   │   ├── Map/             # Map components
│   │   │   └── Map.tsx      # Main map view
│   │   ├── Plaque/          # Plaque display
│   │   │   └── PlaqueDetail.tsx
│   │   ├── Search/          # Search & filter
│   │   │   ├── FilterPanel.tsx
│   │   │   └── SearchBar.tsx
│   │   ├── ErrorBoundary.tsx
│   │   └── LoadingSpinner.tsx
│   ├── hooks/               # Custom React hooks
│   │   └── usePlaques.ts    # Plaque data fetching
│   ├── lib/                 # External integrations
│   │   └── supabase.ts      # Supabase client
│   ├── services/            # API layer
│   │   └── api.ts           # Axios client & endpoints
│   ├── stores/              # Zustand stores
│   │   ├── authStore.ts     # Authentication state
│   │   ├── mapStore.ts      # Map view state
│   │   └── userPlaqueStore.ts # User's visited/favorites
│   ├── types/               # TypeScript types
│   │   └── plaque.ts        # Domain types
│   ├── App.tsx              # Root component & routing
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── dist/                    # Build output
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── tsconfig.json
```

## Component Architecture

### Core Components

| Component | Path | Purpose |
|-----------|------|---------|
| `Map` | `components/Map/Map.tsx` | Main map view with markers, popups, user location |
| `PlaqueDetail` | `components/Plaque/PlaqueDetail.tsx` | Full plaque information page |
| `FilterPanel` | `components/Search/FilterPanel.tsx` | Category filter sidebar |
| `SearchBar` | `components/Search/SearchBar.tsx` | Text search input |
| `Lightbox` | `components/Gallery/Lightbox.tsx` | Full-screen image viewer |
| `LoginPage` | `components/Admin/LoginPage.tsx` | Admin login form |
| `ErrorBoundary` | `components/ErrorBoundary.tsx` | Error handling wrapper |

### Component Hierarchy

```
App
├── ErrorBoundary
│   └── QueryClientProvider
│       └── BrowserRouter
│           └── Routes
│               ├── / → Map
│               │      ├── SearchBar
│               │      ├── FilterPanel
│               │      ├── Markers (dynamic)
│               │      └── ConfirmMoveDialog (conditional)
│               ├── /plaque/:id → PlaqueDetail
│               │                  └── Lightbox (conditional)
│               └── /login → LoginPage
```

## State Management

### Zustand Stores

#### `authStore`
```typescript
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  init: () => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
}
```

#### `mapStore`
```typescript
interface MapState {
  center: [number, number];  // Default: Johannesburg
  zoom: number;              // Default: 12
  selectedPlaqueId: number | null;
  setCenter: (center: [number, number]) => void;
  setZoom: (zoom: number) => void;
  setSelectedPlaque: (id: number | null) => void;
}
```

#### `userPlaqueStore`
```typescript
interface UserPlaqueState {
  visitedIds: Set<number>;
  favoriteIds: Set<number>;
  toggleVisited: (userId: string, plaqueId: number) => void;
  toggleFavorite: (userId: string, plaqueId: number) => void;
  fetchUserPlaques: (userId: string) => Promise<void>;
  clear: () => void;
}
```

### React Query Usage

- **Query Keys:** `['plaques']`, `['plaque', id]`, `['categories']`
- **Caching:** Automatic with configurable stale time
- **Refetch:** Disabled on window focus for better UX

## API Integration

### Axios Client (`services/api.ts`)

```typescript
const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// JWT token injection
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
```

### API Methods

| Method | Endpoint | Description |
|--------|----------|-------------|
| `plaqueApi.list()` | GET /plaques | List with pagination, search, filter |
| `plaqueApi.get(id)` | GET /plaques/:id | Single plaque with images/categories |
| `plaqueApi.nearby()` | GET /plaques/nearby | Geolocation search |
| `plaqueApi.create()` | POST /plaques | Create (admin) |
| `plaqueApi.update()` | PUT /plaques/:id | Update (admin) |
| `plaqueApi.delete()` | DELETE /plaques/:id | Delete (admin) |
| `authApi.login()` | POST /auth/login | JWT login |

## Routing

| Path | Component | Description |
|------|-----------|-------------|
| `/` | `Map` | Main map view |
| `/plaque/:id` | `PlaqueDetail` | Plaque detail page |
| `/login` | `LoginPage` | Admin login |

## Build Configuration

### Vite Config (`vite.config.ts`)

```typescript
export default defineConfig({
  plugins: [react()],
  server: { port: 3000 },
  build: { outDir: '../backend/static/frontend' },
});
```

**Key Points:**
- Build output goes directly to backend's static folder
- Dev server runs on port 3000
- React plugin for JSX transformation

### Tailwind Config

- Custom color palette for plaque markers (blue, green, orange)
- Responsive breakpoints for mobile support
- PostCSS integration

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | No | Backend API URL (default: `/api/v1`) |
| `VITE_SUPABASE_URL` | No | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | No | Supabase anon key |
| `VITE_APP_VERSION` | No | App version for display |

## Testing Strategy

### Unit Tests (Vitest)
- Component rendering tests
- Hook behavior tests
- Store action tests

### E2E Tests (Playwright)
- Map interaction flows
- Search and filter functionality
- Authentication flows
- Plaque detail navigation

## Performance Considerations

- **Marker Clustering:** react-leaflet-cluster for handling 386+ markers
- **Query Caching:** React Query prevents redundant API calls
- **Code Splitting:** Vite's automatic chunk splitting
- **Image Optimization:** Lazy loading in gallery views
