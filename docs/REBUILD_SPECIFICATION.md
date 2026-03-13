# Blue Plaques Map - Rebuild Specification

**Version**: 2.0  
**Date**: March 12, 2026  
**Status**: Planning  
**Team**: BMAD Analysis Team

---

## Executive Summary

This specification outlines a complete rebuild of the Blue Plaques Map using modern technologies while **preserving all 386 existing plaques and 1,157 images**. The rebuild addresses critical security vulnerabilities, improves maintainability, and provides a scalable foundation for growth.

**Key Principle**: **Data preservation is paramount** - all existing content will be migrated, not recreated.

---

## Goals & Non-Goals

### Goals ✅

1. **Preserve Data**: Migrate all 386 plaques and 1,157 images without loss
2. **Security**: Production-ready authentication and authorization
3. **Scalability**: Handle 10,000+ plaques and 100,000+ users
4. **Maintainability**: Modern, testable, documented codebase
5. **Performance**: <2s page load, <500ms API responses
6. **Mobile-First**: Excellent mobile experience

### Non-Goals ❌

1. **NOT recreating data** - existing content will be migrated
2. **NOT changing core features** - map, search, filter remain
3. **NOT adding social features** - out of scope for v2.0
4. **NOT building mobile app** - web-first approach

---

## Technology Stack

### Backend

```yaml
Language: Python 3.13
Framework: FastAPI 0.110+
Database: PostgreSQL 16 + PostGIS
Cache: Redis 7
Task Queue: Celery (for image processing)
Auth: JWT with refresh tokens
ORM: SQLAlchemy 2.0
Validation: Pydantic v2
Testing: Pytest + Pytest-asyncio
```

**Why FastAPI over Flask**:
- Built-in validation (Pydantic)
- Async by default (better performance)
- Auto-generated OpenAPI docs
- Type safety
- Modern Python features

### Frontend

```yaml
Framework: React 18 + TypeScript
Build Tool: Vite
State Management: Zustand
Data Fetching: TanStack Query (React Query)
Styling: Tailwind CSS
Maps: React-Leaflet + Leaflet.markercluster
Forms: React Hook Form + Zod
Testing: Vitest + Playwright
```

**Why React + TypeScript**:
- Component reusability
- Type safety prevents bugs
- Large ecosystem
- Excellent mobile support
- Easy to test

### Infrastructure

```yaml
Frontend Hosting: Vercel (or Netlify)
Backend Hosting: Railway (or Render)
Database: Railway PostgreSQL
Storage: CloudFlare R2 (S3-compatible)
CDN: CloudFlare
Monitoring: Sentry
Analytics: Plausible
CI/CD: GitHub Actions
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CloudFlare CDN                            │
│              (Static Assets + Images)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼────────┐              ┌────────▼────────┐
│  Vercel        │              │  Railway        │
│  (Frontend)    │◄────────────►│  (Backend)      │
│                │   API Calls  │                 │
│  React SPA     │              │  FastAPI        │
└────────────────┘              └────────┬────────┘
                                         │
                         ┌───────────────┼───────────────┐
                         │               │               │
                  ┌──────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
                  │ PostgreSQL │  │   Redis   │  │ R2 Storage│
                  │  + PostGIS │  │  (Cache)  │  │  (Images) │
                  └────────────┘  └───────────┘  └───────────┘
```

### Key Architectural Decisions

**1. Separate Frontend & Backend**
- Frontend: Static SPA deployed to Vercel
- Backend: API-only service on Railway
- Communication: REST API with JWT auth

**2. PostgreSQL with PostGIS**
- Proper relational database (vs SQLite)
- PostGIS for efficient geo queries
- Supports concurrent users
- ACID compliance

**3. Cloud Storage for Images**
- CloudFlare R2 (S3-compatible, cheaper than S3)
- CDN for global performance
- Automatic image optimization
- Scales infinitely

**4. Redis for Caching**
- Cache API responses (5-minute TTL)
- Session storage
- Rate limiting counters

---

## Database Schema

### Core Tables

```sql
-- Plaques table
CREATE TABLE plaques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    address VARCHAR(300),
    location GEOGRAPHY(POINT, 4326),  -- PostGIS
    heritage_portal_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    is_published BOOLEAN DEFAULT true,
    view_count INTEGER DEFAULT 0
);

-- Categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50)
);

-- Junction table for many-to-many
CREATE TABLE plaque_categories (
    plaque_id UUID REFERENCES plaques(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (plaque_id, category_id)
);

-- Images table
CREATE TABLE images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plaque_id UUID REFERENCES plaques(id) ON DELETE CASCADE,
    storage_key VARCHAR(500) NOT NULL,  -- R2 key
    cdn_url TEXT NOT NULL,
    title VARCHAR(200),
    display_order INTEGER DEFAULT 0,
    width INTEGER,
    height INTEGER,
    file_size INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users table (for admin)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    role VARCHAR(50) DEFAULT 'viewer',  -- admin, moderator, viewer
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Reports table
CREATE TABLE plaque_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plaque_id UUID REFERENCES plaques(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, reviewed, resolved
    reported_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    notes TEXT
);

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    changes JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_plaques_location ON plaques USING GIST(location);
CREATE INDEX idx_plaques_published ON plaques(is_published) WHERE is_published = true;
CREATE INDEX idx_images_plaque ON images(plaque_id);
CREATE INDEX idx_reports_status ON plaque_reports(status) WHERE status = 'pending';
CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_created ON audit_log(created_at DESC);
```

### Migration from SQLite

**Data preserved**:
- ✅ All 386 plaque records
- ✅ All 1,157 image records
- ✅ All categories
- ✅ All descriptions and metadata

**Data transformations**:
- `geo_location` JSON → PostGIS `GEOGRAPHY` type
- Comma-separated categories → junction table
- Local file paths → R2 storage keys
- Add UUIDs (keep old IDs in migration mapping)

---

## API Design

### Authentication Endpoints

```
POST   /api/v1/auth/register          # Admin registration (invite-only)
POST   /api/v1/auth/login             # Login (returns JWT)
POST   /api/v1/auth/refresh           # Refresh access token
POST   /api/v1/auth/logout            # Logout (invalidate token)
GET    /api/v1/auth/me                # Get current user
```

### Public Endpoints

```
GET    /api/v1/plaques                # List plaques (paginated, filtered)
GET    /api/v1/plaques/:id            # Get single plaque
GET    /api/v1/plaques/nearby         # Find nearby plaques (lat, lon, radius)
GET    /api/v1/categories             # List all categories
GET    /api/v1/search                 # Full-text search
```

### Admin Endpoints (Auth Required)

```
POST   /api/v1/plaques                # Create plaque
PUT    /api/v1/plaques/:id            # Update plaque
DELETE /api/v1/plaques/:id            # Delete plaque
POST   /api/v1/plaques/:id/images     # Upload image
DELETE /api/v1/images/:id             # Delete image
GET    /api/v1/reports                # List reports
PUT    /api/v1/reports/:id            # Update report status
```

### Example Request/Response

```http
GET /api/v1/plaques?category=homes&limit=20&offset=0

Response 200 OK:
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Tutu House",
      "description": "Home of Archbishop Desmond Tutu...",
      "address": "6309 Vilakazi Street, Orlando West, Soweto",
      "location": {
        "lat": -26.1780822,
        "lon": 28.0392237
      },
      "categories": [
        {"id": 1, "name": "Homes, Mansions", "slug": "homes"}
      ],
      "images": [
        {
          "id": "...",
          "url": "https://cdn.example.com/plaques/...",
          "title": "Front view",
          "width": 1200,
          "height": 800
        }
      ],
      "heritagePortalUrl": "https://heritageportal.co.za/...",
      "createdAt": "2026-01-15T10:30:00Z",
      "updatedAt": "2026-02-20T14:22:00Z"
    }
  ],
  "pagination": {
    "total": 386,
    "limit": 20,
    "offset": 0,
    "hasMore": true
  }
}
```

---

## Frontend Architecture

### Component Structure

```
src/
├── components/
│   ├── map/
│   │   ├── Map.tsx                  # Main map component
│   │   ├── PlaqueMarker.tsx         # Individual marker
│   │   ├── MarkerCluster.tsx        # Clustering logic
│   │   └── UserLocationMarker.tsx   # Blue dot
│   ├── plaque/
│   │   ├── PlaqueCard.tsx           # Plaque preview card
│   │   ├── PlaquePopup.tsx          # Map popup
│   │   ├── PlaqueDetail.tsx         # Full detail view
│   │   └── ImageGallery.tsx         # Lightbox gallery
│   ├── search/
│   │   ├── SearchBar.tsx
│   │   ├── FilterPanel.tsx
│   │   └── CategoryFilter.tsx
│   ├── admin/
│   │   ├── PlaqueForm.tsx
│   │   ├── ImageUpload.tsx
│   │   └── ReportQueue.tsx
│   └── common/
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Modal.tsx
│       └── LoadingSpinner.tsx
├── pages/
│   ├── HomePage.tsx
│   ├── MapPage.tsx
│   ├── PlaqueDetailPage.tsx
│   └── AdminDashboard.tsx
├── services/
│   ├── api.ts                       # API client
│   ├── auth.ts                      # Auth service
│   └── storage.ts                   # LocalStorage wrapper
├── stores/
│   ├── authStore.ts                 # Zustand auth state
│   ├── mapStore.ts                  # Map state
│   └── filterStore.ts               # Filter state
├── hooks/
│   ├── usePlaques.ts                # React Query hook
│   ├── useAuth.ts                   # Auth hook
│   └── useGeolocation.ts            # Geolocation hook
├── types/
│   └── index.ts                     # TypeScript types
└── utils/
    ├── distance.ts                  # Geo calculations
    └── format.ts                    # Formatting helpers
```

### State Management

**Zustand for Global State**:
```typescript
// stores/authStore.ts
import create from 'zustand';

interface AuthState {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  login: async (email, password) => {
    const { user, token } = await authService.login(email, password);
    localStorage.setItem('token', token);
    set({ user, token });
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null });
  }
}));
```

**React Query for Server State**:
```typescript
// hooks/usePlaques.ts
import { useQuery } from '@tanstack/react-query';

export const usePlaques = (filters: PlaqueFilters) => {
  return useQuery({
    queryKey: ['plaques', filters],
    queryFn: () => api.getPlaques(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
```

---

## Security Implementation

### JWT Authentication

```python
# backend/app/auth.py
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": user_id, "exp": expire, "type": "access"},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def verify_token(token: str) -> str:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload["sub"]
```

### Authorization Middleware

```python
# backend/app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(
    token: str = Depends(security)
) -> User:
    try:
        user_id = verify_token(token.credentials)
        user = await user_service.get_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=401)
        return user
    except:
        raise HTTPException(status_code=401)

async def require_admin(
    user: User = Depends(get_current_user)
) -> User:
    if user.role not in ["admin", "moderator"]:
        raise HTTPException(status_code=403)
    return user
```

### Input Validation

```python
# backend/app/schemas.py
from pydantic import BaseModel, Field, validator

class PlaqueCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=5000)
    address: str | None = Field(None, max_length=300)
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    category_ids: list[int] = Field(..., min_items=1)
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

---

## Performance Optimizations

### Backend Caching

```python
# backend/app/cache.py
import redis
import json
from functools import wraps

redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))

def cache(ttl: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{json.dumps(kwargs)}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache(ttl=300)
async def get_plaques(filters: dict):
    # Database query
    pass
```

### Frontend Optimizations

```typescript
// Lazy loading routes
const MapPage = lazy(() => import('./pages/MapPage'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'));

// Image lazy loading
<img 
  src={plaque.thumbnailUrl} 
  loading="lazy"
  alt={plaque.title}
/>

// React Query caching
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
    },
  },
});
```

---

## Testing Strategy

### Backend Tests

```python
# tests/test_plaques.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_plaques(client: AsyncClient):
    response = await client.get("/api/v1/plaques")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "pagination" in data

@pytest.mark.asyncio
async def test_create_plaque_requires_auth(client: AsyncClient):
    response = await client.post("/api/v1/plaques", json={...})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_create_plaque_validates_coordinates(admin_client: AsyncClient):
    response = await admin_client.post("/api/v1/plaques", json={
        "title": "Test",
        "lat": 999,  # Invalid
        "lon": 28.0
    })
    assert response.status_code == 422
```

### Frontend Tests

```typescript
// tests/Map.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { Map } from '../components/map/Map';

test('renders map with plaques', async () => {
  render(<Map />);
  
  await waitFor(() => {
    expect(screen.getByTestId('map-container')).toBeInTheDocument();
  });
  
  const markers = screen.getAllByTestId('plaque-marker');
  expect(markers.length).toBeGreaterThan(0);
});
```

### E2E Tests

```typescript
// e2e/map.spec.ts
import { test, expect } from '@playwright/test';

test('user can search for plaques', async ({ page }) => {
  await page.goto('/');
  await page.fill('[data-testid="search-input"]', 'Tutu');
  await page.waitForTimeout(500);
  
  const markers = await page.$$('[data-testid="plaque-marker"]');
  expect(markers.length).toBeLessThan(386);
});
```

---

**Continued in Part 2...**


---

## Deployment Configuration

### Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@host:5432/blue_plaques
REDIS_URL=redis://host:6379
JWT_SECRET_KEY=<generate-secure-key>
R2_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
R2_ACCESS_KEY=<r2-access-key>
R2_SECRET_KEY=<r2-secret-key>
R2_BUCKET=blue-plaques
CDN_BASE_URL=https://cdn.blueplaques.co.za
SENTRY_DSN=<sentry-dsn>
ENVIRONMENT=production
```

```bash
# Frontend (.env)
VITE_API_URL=https://api.blueplaques.co.za
VITE_SENTRY_DSN=<sentry-dsn>
VITE_PLAUSIBLE_DOMAIN=blueplaques.co.za
```

### Railway Configuration

```toml
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

### Vercel Configuration

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://api.blueplaques.co.za/api/:path*" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ]
}
```

---

## Monitoring & Observability

### Sentry Configuration

```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT"),
    traces_sample_rate=0.1,
    integrations=[FastApiIntegration()]
)
```

```typescript
// frontend/src/main.tsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  tracesSampleRate: 0.1,
});
```

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }
```

---

## Documentation

### API Documentation (Auto-Generated)

FastAPI automatically generates OpenAPI docs at:
- `/docs` - Swagger UI
- `/redoc` - ReDoc UI
- `/openapi.json` - OpenAPI schema

### User Documentation

All existing documentation remains valid:
- USER_GUIDE.md (update URLs)
- ADMIN_GUIDE.md (update auth flow)
- API_DOCUMENTATION.md (regenerate from OpenAPI)

---

## Cost Estimates

### Development (One-Time)

| Task | Hours | Cost |
|------|-------|------|
| Backend setup & migration | 40 | $4,000 |
| API development | 40 | $4,000 |
| Frontend development | 60 | $6,000 |
| Testing & QA | 30 | $3,000 |
| Deployment & launch | 20 | $2,000 |
| Documentation | 10 | $1,000 |
| **Total** | **200** | **$20,000** |

### Infrastructure (Annual)

| Service | Cost |
|---------|------|
| Railway (PostgreSQL + Backend) | $240/year |
| CloudFlare R2 (storage + bandwidth) | $50/year |
| Vercel (frontend) | Free |
| CloudFlare CDN | Free |
| Domain | $15/year |
| Sentry | Free tier |
| Plausible Analytics | $108/year |
| **Total** | **$413/year** |

### Ongoing Maintenance

| Task | Hours/Month | Cost/Year |
|------|-------------|-----------|
| Bug fixes | 5 | $6,000 |
| Feature updates | 3 | $3,600 |
| Content moderation | 2 | $2,400 |
| **Total** | **10** | **$12,000** |

---

## Success Metrics

### Technical Metrics

- **Uptime**: >99.9%
- **API Response Time**: <500ms (p95)
- **Page Load Time**: <2s (p95)
- **Error Rate**: <0.1%
- **Test Coverage**: >80%
- **Lighthouse Score**: >90

### Business Metrics

- **Monthly Active Users**: 1,000 (Month 1) → 10,000 (Month 12)
- **Plaques Viewed per Session**: >3
- **Time on Site**: >2 minutes
- **Return Visitor Rate**: >30%
- **Search Usage**: >40%
- **Mobile Traffic**: >60%

### Content Metrics

- **Total Plaques**: 386 (launch) → 500 (Year 1)
- **Total Images**: 1,157 (launch) → 1,500 (Year 1)
- **User Reports**: <5% of plaques
- **Admin Response Time**: <48 hours

---

## Rollout Strategy

### Phase 1: Soft Launch (Week 6)
- Deploy to production
- Share with 10 beta testers
- Monitor errors and performance
- Fix critical issues

### Phase 2: Limited Launch (Week 7)
- Announce to heritage community
- Share on social media
- Monitor user feedback
- Iterate based on feedback

### Phase 3: Public Launch (Week 8)
- Press release
- Tourism board outreach
- SEO optimization
- Full marketing push

---

## Maintenance Plan

### Daily
- Monitor error rates (Sentry)
- Check uptime (UptimeRobot)
- Review user reports

### Weekly
- Review analytics (Plausible)
- Moderate new content
- Deploy bug fixes

### Monthly
- Security updates
- Performance review
- Feature planning
- Backup verification

### Quarterly
- User survey
- Competitive analysis
- Roadmap review
- Infrastructure optimization

---

## Future Enhancements (Post-Launch)

### Phase 2 (Months 2-3)
- Share links with social preview
- User favorites (localStorage)
- Advanced search (fuzzy matching)
- Print-friendly view

### Phase 3 (Months 4-6)
- Offline support (PWA)
- Route planning
- Export to PDF
- Email notifications

### Phase 4 (Months 7-12)
- Multi-language support
- User accounts (optional)
- Community contributions
- Mobile app (React Native)

---

## Conclusion

This rebuild specification provides a complete roadmap for modernizing the Blue Plaques Map while **preserving all 386 plaques and 1,157 images**. The new platform will be:

✅ **Secure** - Production-ready authentication and authorization  
✅ **Scalable** - PostgreSQL + cloud storage handles growth  
✅ **Maintainable** - Modern stack with tests and documentation  
✅ **Performant** - <2s load time, <500ms API responses  
✅ **Mobile-First** - Excellent mobile experience  

**Timeline**: 6 weeks  
**Cost**: $20,000 development + $413/year infrastructure  
**Team**: 2 developers  

**Next Steps**:
1. Review and approve specification
2. Set up infrastructure accounts
3. Begin Week 1 (foundation & migration)
4. Launch in 6 weeks 🚀

---

**Related Documents**:
- [DATA_MIGRATION_PLAN.md](DATA_MIGRATION_PLAN.md) - Detailed migration steps
- [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md) - Week-by-week plan
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Current state analysis
