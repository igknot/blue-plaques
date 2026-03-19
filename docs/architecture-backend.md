# Backend Architecture - Blue Plaques Map

**Part:** backend
**Type:** REST API
**Framework:** FastAPI + Python 3.13

## Technology Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| Framework | FastAPI | 0.115.0 | Async REST API |
| Language | Python | 3.13 | Runtime |
| Database | Supabase | 2.13.0 | PostgreSQL via PostgREST |
| Validation | Pydantic | 2.10.3 | Request/response schemas |
| Settings | pydantic-settings | 2.6.1 | Environment config |
| Auth | python-jose | 3.3.0 | JWT tokens |
| Password | bcrypt | 5.0.0 | Password hashing |
| Cache | Redis | 5.2.0 | Rate limiting |
| Server | Uvicorn | 0.32.0 | ASGI server |
| Production | Gunicorn | 23.0.0 | Process manager |
| Testing | pytest | 8.3.0 | Test framework |
| HTTP Client | httpx | 0.28.0 | Async HTTP for tests |

## Architecture Pattern

**Layered Architecture** with:
- API Layer (routers)
- Service Layer (business logic)
- Data Layer (Supabase client)
- Schema Layer (Pydantic models)

## Directory Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py    # Router aggregation
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── plaques.py     # Plaque CRUD + search
│   │   │   ├── categories.py  # Category endpoints
│   │   │   └── images.py      # Image upload/delete
│   │   └── deps.py            # Dependency injection
│   ├── core/
│   │   ├── cache.py           # Redis client
│   │   └── security.py        # JWT + password utils
│   ├── middleware/
│   │   └── rate_limit.py      # Rate limiting middleware
│   ├── schemas/
│   │   ├── __init__.py        # Schema exports
│   │   ├── auth.py            # Auth schemas
│   │   └── plaque.py          # Domain schemas
│   ├── services/
│   │   └── storage.py         # Image storage service
│   ├── config.py              # Settings management
│   ├── database.py            # Supabase clients
│   └── main.py                # FastAPI app entry
├── static/
│   ├── frontend/              # Built frontend (production)
│   └── images/                # Uploaded images
├── tests/
│   ├── conftest.py            # Test fixtures
│   ├── test_auth.py
│   ├── test_categories.py
│   ├── test_health.py
│   ├── test_plaques.py
│   └── test_production.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

## API Design

### Router Structure

```
/api
└── /v1
    ├── /auth
    │   └── POST /login
    ├── /plaques
    │   ├── GET /              # List (paginated, searchable)
    │   ├── GET /nearby        # Geolocation search
    │   ├── GET /{id}          # Single plaque
    │   ├── POST /             # Create (admin)
    │   ├── PUT /{id}          # Update (admin)
    │   └── DELETE /{id}       # Delete (admin)
    ├── /categories
    │   ├── GET /              # List with counts
    │   └── GET /{id}          # Single category
    └── /images
        ├── POST /plaques/{id}/images  # Upload (admin)
        └── DELETE /{id}               # Delete (admin)
```

### Authentication Flow

1. User submits email/password to `POST /auth/login`
2. Backend verifies against `users` table in Supabase
3. On success, returns JWT access token
4. Client includes token in `Authorization: Bearer <token>` header
5. Protected endpoints use `get_admin_user` dependency

### Authorization

```python
# deps.py
def get_admin_user(token: str = Depends(oauth2_scheme)):
    # Decode JWT, verify signature
    # Fetch user from Supabase
    # Return user or raise 401/403
```

## Database Integration

### Dual Client Pattern

```python
# database.py

# Public client - subject to RLS policies
supabase: Client = create_client(
    settings.SUPABASE_URL, 
    settings.SUPABASE_ANON_KEY
)

# Admin client - bypasses RLS for write operations
supabase_admin: Client = create_client(
    settings.SUPABASE_URL, 
    settings.SUPABASE_SERVICE_ROLE_KEY
)
```

**Usage:**
- `supabase` → Public reads (list, get, search)
- `supabase_admin` → Admin writes (create, update, delete)

### Query Patterns

```python
# List with pagination and search
query = supabase.table("plaques").select(PLAQUE_SELECT)
if search:
    query = query.or_(f"title.ilike.%{search}%,...")
resp = query.range(offset, offset + page_size - 1).execute()

# Nearby search via RPC
rpc_resp = supabase.rpc("nearby_plaques", {
    "lat": lat, "lng": lng, "radius_m": radius
}).execute()
```

## Middleware

### Rate Limiting

```python
class RateLimitMiddleware:
    def __init__(self, app, requests_per_minute: int = 60):
        self.app = app
        self.rpm = requests_per_minute
        self.redis = Redis.from_url(settings.REDIS_URL)
    
    async def __call__(self, scope, receive, send):
        # Check rate limit per IP
        # Return 429 if exceeded
```

### CORS

```python
allowed_origins = ["*"] if settings.DEBUG else ["https://blueplaques.co.za"]
app.add_middleware(CORSMiddleware, 
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

## Schema Design

### Request/Response Models

```python
class PlaqueBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    # ... more fields

class PlaqueCreate(PlaqueBase):
    category_ids: List[int] = []

class PlaqueResponse(PlaqueBase):
    id: int
    created_at: datetime
    updated_at: datetime
    images: List[ImageResponse] = []
    categories: List[CategoryResponse] = []
```

## Configuration

### Settings (`config.py`)

```python
class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    REDIS_URL: str = ""
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = True

    class Config:
        env_file = ".env"
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_ANON_KEY` | Yes | Supabase anon/public key |
| `SUPABASE_SERVICE_ROLE_KEY` | No | Service role key for admin ops |
| `REDIS_URL` | No | Redis URL for rate limiting |
| `SECRET_KEY` | Yes | JWT signing key (min 32 chars) |
| `ALGORITHM` | No | JWT algorithm (default: HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Token expiry (default: 30) |
| `DEBUG` | No | Enable debug mode (default: True) |

## Static File Serving

```python
# main.py
static_dir = Path(__file__).parent.parent / "static"
frontend_dir = static_dir / "frontend"

# Mount asset directories
app.mount("/assets", StaticFiles(directory=frontend_dir / "assets"))
app.mount("/static", StaticFiles(directory=static_dir))

# Catch-all for SPA routing
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith("api/"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return FileResponse(frontend_dir / "index.html")
```

## Error Handling

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "path": str(request.url)}
    )
```

## Testing Strategy

### Test Structure

```python
# conftest.py
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    # Generate test JWT token
    return {"Authorization": f"Bearer {token}"}
```

### Test Categories

| File | Coverage |
|------|----------|
| `test_health.py` | Health check endpoint |
| `test_plaques.py` | Plaque CRUD operations |
| `test_categories.py` | Category endpoints |
| `test_auth.py` | Authentication flow |
| `test_production.py` | Production config validation |

### Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
pytest tests/ -v --cov=app  # With coverage
```

## Deployment

### Docker

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production (Leapcell)

```bash
# Build command
pip install -r requirements.txt

# Start command
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## Performance Considerations

- **Connection Pooling:** Supabase client handles connection management
- **Rate Limiting:** Redis-backed to prevent abuse
- **Async Operations:** FastAPI's async support for I/O-bound operations
- **Query Optimization:** Selective column fetching, pagination
