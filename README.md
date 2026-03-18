# Blue Plaques Map 🏛️

Interactive web application for discovering and exploring Johannesburg's 386 heritage blue plaques.

---

## Technology Stack

- **Backend**: Python 3.13 + FastAPI + Supabase Python Client
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **Mapping**: Leaflet.js + OpenStreetMap
- **Cache**: Redis (rate limiting)

---

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- Docker (optional)
- A [Supabase](https://supabase.com) project

### Docker Compose

```bash
# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your Supabase credentials (see Configuration below)

# Start all services
docker compose up -d
```

Backend runs on `http://localhost:8000`, frontend on `http://localhost:5173`.

### Manual Setup

#### Backend

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your Supabase credentials (see Configuration below)

# Run development server
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install

# Configure environment
cp .env.example .env
# Edit .env with your values

# Run development server
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies API requests to the backend on `http://localhost:8000`.

---

## Configuration

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Your Supabase project URL (e.g. `https://xxxxx.supabase.co`) |
| `SUPABASE_ANON_KEY` | Yes | Your Supabase anon/public key |
| `SECRET_KEY` | Yes | JWT signing key (min 32 chars) |
| `ALGORITHM` | No | JWT algorithm (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token expiry (default: `30`) |
| `REDIS_URL` | No | Redis URL for rate limiting (default: empty) |
| `DEBUG` | No | Enable debug mode / permissive CORS (default: `True`) |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes | Backend API URL (default: `http://localhost:8000/api/v1`) |
| `VITE_SUPABASE_URL` | No | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | No | Supabase anon key |

---

## API Endpoints

### Public

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/plaques` | List plaques (paginated, searchable, filterable) |
| `GET` | `/api/v1/plaques/{id}` | Get single plaque with images and categories |
| `GET` | `/api/v1/plaques/nearby?lat=&lng=&radius=` | Find plaques within radius (meters) |
| `GET` | `/api/v1/categories` | List categories with plaque counts |
| `GET` | `/api/v1/categories/{id}` | Get single category with plaque count |
| `GET` | `/health` | Health check |

### Admin (requires JWT auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | Login, returns JWT token |
| `POST` | `/api/v1/plaques` | Create plaque |
| `PUT` | `/api/v1/plaques/{id}` | Update plaque |
| `DELETE` | `/api/v1/plaques/{id}` | Delete plaque |
| `POST` | `/api/v1/images/plaques/{id}/images` | Upload image |
| `DELETE` | `/api/v1/images/{id}` | Delete image |

### Query Parameters for `GET /api/v1/plaques`

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `page_size` | int | 50 | Results per page (max 1000) |
| `search` | string | — | Search title, description, address |
| `category_ids` | string | — | Comma-separated category IDs to filter by |

---

## Project Structure

```
blue_plaques/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # Supabase client init
│   │   ├── api/
│   │   │   ├── deps.py          # Auth dependencies
│   │   │   └── v1/
│   │   │       ├── plaques.py   # Plaque CRUD + search + nearby
│   │   │       ├── categories.py
│   │   │       ├── images.py
│   │   │       └── auth.py
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── core/security.py     # JWT + password hashing
│   │   ├── middleware/           # Rate limiting
│   │   └── services/storage.py  # Local image storage
│   ├── tests/                   # Pytest test suite
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/          # Map, Search, Plaque, Gallery, Admin
│   │   ├── services/api.ts      # Axios API client
│   │   ├── stores/              # Zustand stores
│   │   ├── hooks/
│   │   └── types/
│   ├── package.json
│   ├── .env.example
│   └── vite.config.ts
└── docker-compose.yml           # Backend + Frontend + Redis
```

---

## Database

The app connects to Supabase via the PostgREST API (HTTPS) using the [Supabase Python client](https://github.com/supabase-community/supabase-py). No direct PostgreSQL connection is required.

### Tables

| Table | Description |
|-------|-------------|
| `plaques` | 386 heritage plaques with coordinates, descriptions |
| `images` | 1,157 plaque images with captions and display order |
| `categories` | 104 categories (e.g. Churches, Military, Homes) |
| `plaque_categories` | Many-to-many junction table |
| `users` | Admin users for authenticated operations |

### RLS Policies

- Public read access on `plaques`, `images`, `categories`, `plaque_categories`
- Users table restricted to authenticated users reading their own record

### RPC Functions

- `nearby_plaques(lat, lng, radius_m)` — Haversine distance search returning plaques within radius

---

## Data

- **386** heritage blue plaques across Johannesburg
- **1,157** images sourced from the [Heritage Portal](https://heritageportal.co.za)
- **104** categories
- Original data migrated from SQLite (`blue_plaques.db` kept as backup)

---

## Testing

```bash
cd backend
source venv/bin/activate
python -m pytest tests/ -v
```

---

## License

[License information to be added]
