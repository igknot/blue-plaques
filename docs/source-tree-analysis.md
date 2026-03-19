# Source Tree Analysis - Blue Plaques Map

## Project Root Structure

```
blue_plaques/
├── backend/                 # Python FastAPI backend (Part: backend)
├── frontend/                # React TypeScript frontend (Part: frontend)
├── docs/                    # Project documentation
├── tests/                   # E2E tests
│   └── e2e/                 # Playwright E2E tests
├── _bmad/                   # BMAD framework files
├── .kiro/                   # Kiro IDE configuration
├── .agents/                 # Agent skills
├── docker-compose.yml       # Docker orchestration
├── README.md                # Project overview
├── blue_plaques.db          # SQLite backup (legacy)
├── playwright.config.ts     # Playwright configuration
└── setup.sh                 # Setup script
```

## Backend Structure (Part: backend)

```
backend/
├── app/                     # Application code
│   ├── api/                 # API layer
│   │   ├── v1/              # API version 1
│   │   │   ├── __init__.py  # Router aggregation
│   │   │   ├── auth.py      # POST /auth/login
│   │   │   ├── plaques.py   # Plaque CRUD endpoints
│   │   │   ├── categories.py # Category endpoints
│   │   │   └── images.py    # Image upload/delete
│   │   └── deps.py          # Dependency injection (auth)
│   ├── core/                # Core utilities
│   │   ├── cache.py         # Redis client
│   │   └── security.py      # JWT + bcrypt utilities
│   ├── middleware/          # HTTP middleware
│   │   └── rate_limit.py    # Rate limiting (60 req/min)
│   ├── schemas/             # Pydantic models
│   │   ├── __init__.py      # Schema exports
│   │   ├── auth.py          # Token, UserLogin
│   │   └── plaque.py        # Plaque, Image, Category schemas
│   ├── services/            # Business logic
│   │   └── storage.py       # Image storage service
│   ├── config.py            # ⚙️ Settings (pydantic-settings)
│   ├── database.py          # 🔌 Supabase client initialization
│   └── main.py              # 🚀 FastAPI app entry point
├── static/                  # Static files
│   ├── frontend/            # Built React app (production)
│   │   ├── assets/          # JS/CSS bundles
│   │   └── index.html       # SPA entry
│   └── images/              # Uploaded plaque images
├── tests/                   # pytest test suite
│   ├── conftest.py          # Test fixtures
│   ├── test_auth.py         # Auth endpoint tests
│   ├── test_categories.py   # Category endpoint tests
│   ├── test_health.py       # Health check tests
│   ├── test_plaques.py      # Plaque endpoint tests
│   └── test_production.py   # Production config tests
├── venv/                    # Python virtual environment
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container definition
├── .env                     # Environment variables (gitignored)
└── .env.example             # Environment template
```

### Key Backend Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app, middleware, static serving |
| `app/config.py` | Environment configuration via pydantic-settings |
| `app/database.py` | Supabase client (public + admin) |
| `app/api/v1/plaques.py` | Main CRUD + search + nearby endpoints |
| `app/core/security.py` | JWT creation/verification, password hashing |
| `app/middleware/rate_limit.py` | Redis-backed rate limiting |

## Frontend Structure (Part: frontend)

```
frontend/
├── src/                     # Source code
│   ├── components/          # React components
│   │   ├── Admin/           # Admin-only components
│   │   │   └── LoginPage.tsx
│   │   ├── Gallery/         # Image gallery
│   │   │   └── Lightbox.tsx # Full-screen image viewer
│   │   ├── Map/             # Map components
│   │   │   └── Map.tsx      # 🗺️ Main map view
│   │   ├── Plaque/          # Plaque display
│   │   │   └── PlaqueDetail.tsx # Plaque detail page
│   │   ├── Search/          # Search & filter
│   │   │   ├── FilterPanel.tsx  # Category filter sidebar
│   │   │   └── SearchBar.tsx    # Text search input
│   │   ├── ErrorBoundary.tsx    # Error handling
│   │   └── LoadingSpinner.tsx   # Loading indicator
│   ├── hooks/               # Custom React hooks
│   │   └── usePlaques.ts    # Plaque data fetching hook
│   ├── lib/                 # External integrations
│   │   └── supabase.ts      # Supabase client for auth
│   ├── services/            # API layer
│   │   └── api.ts           # 🔌 Axios client + endpoints
│   ├── stores/              # Zustand state stores
│   │   ├── authStore.ts     # Authentication state
│   │   ├── mapStore.ts      # Map view state
│   │   └── userPlaqueStore.ts # User's visited/favorites
│   ├── types/               # TypeScript definitions
│   │   └── plaque.ts        # Domain types
│   ├── App.tsx              # 🚀 Root component + routing
│   ├── main.tsx             # Entry point
│   ├── index.css            # Global styles (Tailwind)
│   └── vite-env.d.ts        # Vite type declarations
├── public/                  # Static assets
├── dist/                    # Build output (dev)
├── node_modules/            # npm dependencies
├── package.json             # npm configuration
├── package-lock.json        # Dependency lock
├── vite.config.ts           # ⚙️ Vite configuration
├── tailwind.config.js       # Tailwind CSS config
├── postcss.config.js        # PostCSS config
├── tsconfig.json            # TypeScript config
├── tsconfig.node.json       # Node TypeScript config
├── Dockerfile               # Production container
├── Dockerfile.dev           # Development container
├── nginx.conf               # Nginx config (if used)
├── vercel.json              # Vercel deployment config
├── .env                     # Environment variables
└── .env.example             # Environment template
```

### Key Frontend Files

| File | Purpose |
|------|---------|
| `src/App.tsx` | Root component, React Query provider, routing |
| `src/main.tsx` | React DOM render entry point |
| `src/components/Map/Map.tsx` | Main map with markers, popups, user location |
| `src/services/api.ts` | Axios client with JWT interceptor |
| `src/stores/authStore.ts` | Supabase auth state management |
| `vite.config.ts` | Build config, output to backend/static |

## Integration Points

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Map.tsx   │───▶│   api.ts    │───▶│ authStore   │     │
│  │             │    │ (Axios)     │    │ (Supabase)  │     │
│  └─────────────┘    └──────┬──────┘    └─────────────┘     │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │ HTTP /api/v1/*
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                        Backend                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   main.py   │───▶│  routers    │───▶│ database.py │     │
│  │  (FastAPI)  │    │ (v1/*.py)   │    │ (Supabase)  │     │
│  └─────────────┘    └─────────────┘    └──────┬──────┘     │
│                                                │             │
└────────────────────────────────────────────────┼─────────────┘
                                                 │ PostgREST
                                                 ▼
                                        ┌─────────────────┐
                                        │    Supabase     │
                                        │   PostgreSQL    │
                                        └─────────────────┘
```

## Critical Directories

| Directory | Part | Purpose |
|-----------|------|---------|
| `backend/app/api/v1/` | backend | REST API endpoints |
| `backend/app/schemas/` | backend | Request/response models |
| `backend/static/frontend/` | backend | Production frontend build |
| `frontend/src/components/` | frontend | React UI components |
| `frontend/src/stores/` | frontend | Global state management |
| `frontend/src/services/` | frontend | API client layer |

## Entry Points

| Part | File | Command |
|------|------|---------|
| Backend | `backend/app/main.py` | `uvicorn app.main:app` |
| Frontend | `frontend/src/main.tsx` | `npm run dev` |
| Tests (Backend) | `backend/tests/` | `pytest tests/` |
| Tests (E2E) | `tests/e2e/` | `npm run test:e2e` |
