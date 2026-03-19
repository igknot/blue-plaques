# Blue Plaques Map - Project Overview

**Date:** March 19, 2026
**Type:** Multi-part (Frontend + Backend)
**Architecture:** Full-stack Web Application

## Executive Summary

Blue Plaques Map is an interactive web application for discovering and exploring Johannesburg's 386 heritage blue plaques. The application provides a map-based interface for browsing, searching, and filtering heritage sites, with features for user authentication, plaque tracking (visited/want-to-visit), and admin management.

## Quick Reference

| Attribute | Value |
|-----------|-------|
| **Project Type(s)** | Web (Frontend), Backend API |
| **Primary Language(s)** | TypeScript, Python |
| **Architecture Pattern** | Client-Server with REST API |
| **Repository Type** | Multi-part |
| **Parts** | 2 (frontend, backend) |

## Part Overview

### Frontend (Web)

| Category | Technology | Version |
|----------|------------|---------|
| Framework | React | 18.2.0 |
| Build Tool | Vite | 5.1.0 |
| Language | TypeScript | 5.3.3 |
| Styling | Tailwind CSS | 3.4.1 |
| State Management | Zustand | 4.5.0 |
| Data Fetching | TanStack React Query | 5.20.0 |
| Mapping | Leaflet + react-leaflet | 1.9.4 / 4.2.1 |
| HTTP Client | Axios | 1.6.7 |
| Testing | Vitest + Playwright | 1.2.2 / 1.42.0 |

**Root Path:** `frontend/`
**Entry Point:** `src/main.tsx`

### Backend (API)

| Category | Technology | Version |
|----------|------------|---------|
| Framework | FastAPI | 0.115.0 |
| Language | Python | 3.13 |
| Database | Supabase (PostgreSQL) | 2.13.0 |
| Auth | python-jose (JWT) + bcrypt | 3.3.0 / 5.0.0 |
| Cache | Redis | 5.2.0 |
| Server | Uvicorn + Gunicorn | 0.32.0 / 23.0.0 |
| Testing | pytest + pytest-asyncio | 8.3.0 / 0.24.0 |

**Root Path:** `backend/`
**Entry Point:** `app/main.py`

## Key Features

- **Interactive Map:** Leaflet-based map with marker clustering for 386 heritage plaques
- **Search & Filter:** Full-text search across title, description, address; category filtering
- **Nearby Discovery:** Geolocation-based plaque discovery within configurable radius
- **User Authentication:** Google OAuth via Supabase Auth
- **Plaque Tracking:** Mark plaques as visited or want-to-visit (authenticated users)
- **Admin Management:** CRUD operations for plaques and images (JWT-protected)
- **Image Gallery:** Lightbox viewer for plaque images
- **Responsive Design:** Mobile-friendly interface with Tailwind CSS

## Architecture Highlights

- **Separation of Concerns:** Clear frontend/backend separation with REST API communication
- **Database Abstraction:** Supabase client handles PostgreSQL via PostgREST API
- **Dual Client Pattern:** Public (anon key) and Admin (service role key) Supabase clients
- **Rate Limiting:** Redis-backed rate limiting middleware (60 req/min)
- **Static Serving:** Backend serves pre-built frontend in production

## Development Overview

### Prerequisites

- Python 3.13+
- Node.js 18+
- Docker (optional)
- Supabase project

### Quick Start

```bash
# Docker Compose (recommended)
docker compose up -d

# Manual - Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Manual - Frontend
cd frontend && npm install && npm run dev
```

### Testing

```bash
# Backend
cd backend && pytest tests/ -v

# Frontend
cd frontend && npm test        # Unit tests (Vitest)
cd frontend && npm run test:e2e # E2E tests (Playwright)
```

## Deployment

**Platform:** Leapcell
**Strategy:** Single service deployment - backend serves API + static frontend

| Setting | Value |
|---------|-------|
| Runtime | Python |
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port 8080` |
| Port | 8080 |

**Production URL:** https://blueplaques.leapcell.app

## Data Summary

- **386** heritage blue plaques
- **1,157** images
- **104** categories
- Data sourced from Heritage Portal

## Related Documentation

- [index.md](./index.md) - Master documentation index
- [architecture-frontend.md](./architecture-frontend.md) - Frontend architecture
- [architecture-backend.md](./architecture-backend.md) - Backend architecture
- [api-contracts.md](./api-contracts.md) - API endpoint documentation
- [data-models.md](./data-models.md) - Database schema
- [development-guide.md](./development-guide.md) - Development setup
- [USER_GUIDE.md](./USER_GUIDE.md) - End-user guide
