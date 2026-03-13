# Blue Plaques Map - Technical Architecture

## System Overview

Interactive web application for discovering and managing heritage blue plaques in Johannesburg. Supports both public browsing and authenticated admin content management.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Leaflet    │  │  Lightbox    │  │   Camera     │     │
│  │   Map UI     │  │   Carousel   │  │   Capture    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│           │                │                  │             │
│           └────────────────┴──────────────────┘             │
│                          │                                  │
│                    JavaScript API Client                    │
└──────────────────────────┼──────────────────────────────────┘
                           │ HTTP/JSON
┌──────────────────────────┼──────────────────────────────────┐
│                    Flask Backend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Routes     │  │   Error      │  │   Security   │     │
│  │   Handler    │  │   Handler    │  │   Headers    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│           │                │                  │             │
│           └────────────────┴──────────────────┘             │
│                          │                                  │
└──────────────────────────┼──────────────────────────────────┘
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                    Data Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   SQLite     │  │    Static    │  │   Uploads    │     │
│  │   Database   │  │    Images    │  │   Folder     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Runtime**: Python 3.13
- **Framework**: Flask 3.0.3
- **Database**: SQLite 3
- **Server**: Flask dev server (development), Gunicorn recommended (production)

### Frontend
- **Core**: HTML5, CSS3, ES6 JavaScript
- **Mapping**: Leaflet.js 1.9.4
- **Tiles**: OpenStreetMap
- **APIs**: Geolocation API, MediaDevices API

### Infrastructure
- **Hosting**: Render.com (configured via render.yaml)
- **Storage**: Local filesystem (static/images, static/uploads)
- **Port**: 5000

## Database Schema

### plaques
```sql
CREATE TABLE plaques (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT,
    image_url TEXT,
    location TEXT,
    description TEXT,
    local_image_path TEXT,
    local_html_path TEXT,
    geo_location TEXT,  -- JSON: {"lat": "...", "lon": "..."}
    address TEXT,
    categories TEXT,    -- Comma-separated
    to_review INTEGER DEFAULT 0
);

CREATE INDEX idx_geo_location ON plaques(geo_location);
```

### plaque_images
```sql
CREATE TABLE plaque_images (
    id INTEGER PRIMARY KEY,
    plaque_id INTEGER,
    image_url TEXT,
    local_image_path TEXT,
    image_title TEXT,
    image_order INTEGER,
    FOREIGN KEY (plaque_id) REFERENCES plaques(id)
);

CREATE INDEX idx_plaque_id ON plaque_images(plaque_id);
```

## API Endpoints

### Public Endpoints

#### GET /
Returns main application HTML.

#### GET /api/plaques
Returns all plaques with geo-location data.

**Response:**
```json
[
  {
    "id": 1,
    "title": "Plaque Title",
    "lat": -26.1780822,
    "lon": 28.0392237,
    "address": "Street Address",
    "categories": ["Category1", "Category2"],
    "description": "Description text",
    "mainImage": "static/images/image.jpg",
    "images": [
      {"path": "static/images/image.jpg", "title": "Image Title"}
    ],
    "url": "https://heritageportal.co.za/..."
  }
]
```

#### GET /static/<path>
Serves static files (images, data).

#### GET /favicon.svg
Returns application favicon.

### Admin Endpoints

⚠️ **WARNING**: Currently no authentication - client-side password only!

#### POST /api/plaques/<id>/report
Marks plaque for review.

**Request:** Empty POST
**Response:**
```json
{"success": true, "message": "Plaque marked for review"}
```

#### PUT /api/plaques/<id>/position
Updates plaque geo-location.

**Request:**
```json
{"lat": -26.178, "lon": 28.039}
```

**Response:**
```json
{"success": true}
```

#### POST /api/plaques
Creates new plaque with photo upload.

**Request:**
```json
{
  "title": "Plaque Title",
  "description": "Description",
  "address": "Address",
  "categories": "Category1, Category2",
  "lat": -26.178,
  "lon": 28.039,
  "photo": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{"success": true}
```

## Security Architecture

### Current Implementation
- Security headers (X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, HSTS)
- Debug mode controlled by environment variable
- Error logging without exposing internals
- HTTPS enforcement via HSTS header

### Critical Security Gaps
1. **No authentication** - Admin password hardcoded in client JavaScript
2. **No authorization** - Anyone can call admin endpoints
3. **No input validation** - Raw JSON accepted without sanitization
4. **No rate limiting** - Vulnerable to abuse
5. **No CSRF protection** - State-changing requests unprotected
6. **File upload risks** - No image validation, size limits, or sanitization

### Recommended Security Improvements
1. Implement JWT or session-based authentication
2. Add server-side authorization checks
3. Validate all inputs with Pydantic schemas
4. Add rate limiting (Flask-Limiter)
5. Implement CSRF tokens
6. Validate/resize uploaded images (Pillow)
7. Use environment variables for secrets
8. Add Content Security Policy headers

## Performance Considerations

### Current Optimizations
- Database indexes on geo_location and plaque_id
- Client-side filtering (no server round-trips)
- Browser caching of map tiles
- Lazy image loading

### Performance Bottlenecks
- All 386 plaques loaded on page load (~200KB JSON)
- No marker clustering (map cluttered at low zoom)
- No image optimization (some images >1MB)
- No CDN for static assets
- Inline CSS/JS (no minification)

### Recommended Improvements
1. Implement marker clustering (Leaflet.markercluster)
2. Lazy-load plaque data by viewport bounds
3. Optimize images (WebP format, responsive sizes)
4. Use CDN for static assets
5. Minify and bundle JS/CSS
6. Implement service worker for offline support
7. Add Redis caching layer

## Deployment Architecture

### Development
```bash
export DEBUG=True
python server.py
```

### Production (Current - Not Recommended)
```bash
python server.py  # Uses Flask dev server
```

### Production (Recommended)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

### Recommended Production Stack
```
Internet
    │
    ▼
┌─────────────────┐
│  Nginx (SSL)    │  - SSL termination
│  Reverse Proxy  │  - Static file serving
└────────┬────────┘  - Rate limiting
         │
         ▼
┌─────────────────┐
│   Gunicorn      │  - WSGI server
│   (4 workers)   │  - Process management
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Flask App      │  - Application logic
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQLite DB      │  - Data persistence
└─────────────────┘
```

## File Structure

```
blue_plaques/
├── server.py                 # Flask application
├── index.html                # Frontend (monolithic)
├── favicon.svg               # Application icon
├── requirements.txt          # Python dependencies
├── render.yaml              # Render.com deployment config
├── blue_plaques.db          # SQLite database (905KB)
├── static/
│   ├── images/              # 370 plaque images
│   └── uploads/             # User-uploaded images
├── docs/                    # Documentation
├── venv/                    # Python virtual environment
└── _bmad/                   # BMAD framework files
```

## Scalability Considerations

### Current Limitations
- SQLite not suitable for high concurrency
- No horizontal scaling capability
- File-based uploads don't scale
- No caching layer

### Migration Path for Scale
1. **Database**: SQLite → PostgreSQL
2. **File Storage**: Local → S3/Cloud Storage
3. **Caching**: Add Redis for API responses
4. **Search**: Add Elasticsearch for full-text search
5. **CDN**: CloudFlare for static assets
6. **Load Balancing**: Multiple Gunicorn instances behind Nginx

## Monitoring & Observability

### Current State
- Python logging to stdout
- No metrics collection
- No error tracking
- No performance monitoring

### Recommended Additions
1. **Logging**: Structured logging (JSON format)
2. **Metrics**: Prometheus + Grafana
3. **Error Tracking**: Sentry
4. **APM**: New Relic or DataDog
5. **Uptime Monitoring**: UptimeRobot
6. **Analytics**: Google Analytics or Plausible

## Testing Strategy

### Current State
❌ No tests

### Recommended Test Coverage
1. **Unit Tests**: Database queries, data transformations
2. **Integration Tests**: API endpoints
3. **E2E Tests**: User workflows (Playwright/Cypress)
4. **Load Tests**: Performance under load (Locust)
5. **Security Tests**: OWASP ZAP scans

## Version History

- **v1.0** (2026-02-27): Initial prototype with security fixes
- **v0.1** (2026-02-27): Original prototype

## Future Architecture Considerations

### Microservices Split (if needed)
- **Map Service**: Plaque data and geo-queries
- **Image Service**: Upload, processing, serving
- **Admin Service**: Content moderation
- **Auth Service**: User authentication

### API Versioning
- Implement `/api/v1/` prefix
- Maintain backward compatibility
- Document breaking changes

### Mobile App
- Consider React Native or Flutter
- Share API with web frontend
- Offline-first architecture with sync
