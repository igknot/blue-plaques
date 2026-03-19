# Development Guide - Blue Plaques Map

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.13+ | Backend runtime |
| Node.js | 18+ | Frontend build |
| Docker | Latest | Containerized development |
| Supabase Account | — | Database & auth |

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone and configure
git clone <repository-url>
cd blue_plaques

# Set up environment
cp backend/.env.example backend/.env
# Edit backend/.env with your Supabase credentials

# Start all services
docker compose up -d

# View logs
docker compose logs -f
```

**Services:**
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Redis: localhost:6379

### Option 2: Manual Setup

#### Backend

```bash
# Create virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if needed

# Run development server
npm run dev
```

## Environment Configuration

### Backend (`backend/.env`)

```env
# Required
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SECRET_KEY=your-secret-key-min-32-chars

# Optional
SUPABASE_SERVICE_ROLE_KEY=eyJ...  # For admin operations
REDIS_URL=redis://localhost:6379   # For rate limiting
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=True
```

### Frontend (`frontend/.env`)

```env
# Optional - defaults work for local development
VITE_API_URL=http://localhost:8000/api/v1
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

## Development Workflow

### Backend Development

```bash
cd backend
source venv/bin/activate

# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=html

# Format code (if using black)
black app/

# Type checking (if using mypy)
mypy app/
```

### Frontend Development

```bash
cd frontend

# Development server with HMR
npm run dev

# Run unit tests
npm test

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI
npm run test:e2e:ui

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
blue_plaques/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Security, cache
│   │   ├── middleware/      # Rate limiting
│   │   ├── schemas/         # Pydantic models
│   │   ├── services/        # Business logic
│   │   ├── config.py        # Settings
│   │   ├── database.py      # Supabase clients
│   │   └── main.py          # FastAPI app
│   ├── static/
│   │   ├── frontend/        # Built frontend
│   │   └── images/          # Uploaded images
│   ├── tests/               # pytest tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── hooks/           # Custom hooks
│   │   ├── lib/             # External integrations
│   │   ├── services/        # API client
│   │   ├── stores/          # Zustand stores
│   │   ├── types/           # TypeScript types
│   │   ├── App.tsx          # Root component
│   │   └── main.tsx         # Entry point
│   ├── package.json
│   └── vite.config.ts
├── docs/                    # Documentation
├── tests/e2e/               # E2E tests
└── docker-compose.yml
```

## Common Tasks

### Adding a New API Endpoint

1. Create/update schema in `backend/app/schemas/`
2. Add route in `backend/app/api/v1/`
3. Register router in `backend/app/api/v1/__init__.py`
4. Add tests in `backend/tests/`
5. Update API documentation

### Adding a New Frontend Component

1. Create component in `frontend/src/components/`
2. Add types if needed in `frontend/src/types/`
3. Update routing in `App.tsx` if it's a page
4. Add tests

### Adding a New Zustand Store

1. Create store in `frontend/src/stores/`
2. Export from store file
3. Use in components with `useStoreName()`

### Database Changes

1. Update Supabase schema via dashboard
2. Update Pydantic schemas in `backend/app/schemas/`
3. Update TypeScript types in `frontend/src/types/`
4. Test with existing data

## Testing

### Backend Tests

```bash
cd backend
source venv/bin/activate

# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_plaques.py -v

# With coverage
pytest tests/ -v --cov=app

# Generate HTML coverage report
pytest tests/ -v --cov=app --cov-report=html
open htmlcov/index.html
```

### Frontend Tests

```bash
cd frontend

# Unit tests (Vitest)
npm test

# Watch mode
npm test -- --watch

# E2E tests (Playwright)
npm run test:e2e

# E2E with browser UI
npm run test:e2e:ui

# Specific E2E test
npx playwright test tests/e2e/map.spec.ts
```

## Debugging

### Backend

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use debugpy for VS Code
# pip install debugpy
# Add to main.py:
# import debugpy
# debugpy.listen(5678)
```

### Frontend

- React DevTools browser extension
- Zustand DevTools (built-in)
- React Query DevTools (add to App.tsx)
- Browser DevTools Network tab for API calls

## Code Style

### Backend (Python)

- Follow PEP 8
- Use type hints
- Docstrings for public functions
- Black for formatting (optional)

### Frontend (TypeScript)

- ESLint configuration in project
- Prettier for formatting
- Functional components with hooks
- TypeScript strict mode

## Git Workflow

### Pre-push Hook

The project has a pre-push hook that rebuilds the frontend:

```bash
# .git/hooks/pre-push
cd frontend && npm run build
git add backend/static/frontend/
```

This ensures the built frontend is always committed with code changes.

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch
- `feature/*` - New features
- `fix/*` - Bug fixes

## Deployment

### Local Production Build

```bash
# Build frontend
cd frontend
npm run build

# Run backend with built frontend
cd ../backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker Production

```bash
# Build images
docker compose -f docker-compose.prod.yml build

# Run
docker compose -f docker-compose.prod.yml up -d
```

### Leapcell Deployment

1. Push to main branch
2. Pre-push hook builds frontend to `backend/static/frontend/`
3. Leapcell detects changes and redeploys
4. Backend serves API + static frontend

## Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

**Supabase connection errors:**
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`
- Check Supabase project is active

**Rate limiting not working:**
- Ensure Redis is running
- Check `REDIS_URL` in `.env`

### Frontend Issues

**"Cannot find module" errors:**
```bash
rm -rf node_modules
npm install
```

**API calls failing:**
- Check `VITE_API_URL` in `.env`
- Ensure backend is running
- Check browser console for CORS errors

**Map not loading:**
- Check internet connection (map tiles from OpenStreetMap)
- Verify Leaflet CSS is imported

### Docker Issues

**Containers not starting:**
```bash
docker compose down
docker compose up -d --build
docker compose logs
```

**Port conflicts:**
- Check if ports 8000, 5173, 6379 are in use
- Modify ports in `docker-compose.yml`
