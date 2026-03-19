# Blue Plaques Map - Documentation Index

**Generated:** March 19, 2026
**Workflow:** Document Project v1.2.0
**Scan Level:** Deep

---

## Project Overview

| Attribute | Value |
|-----------|-------|
| **Type** | Multi-part (Frontend + Backend) |
| **Primary Language** | TypeScript, Python |
| **Architecture** | Full-stack Web Application |
| **Repository Type** | Multi-part |

### Quick Reference

| Part | Type | Tech Stack | Root Path |
|------|------|------------|-----------|
| **Frontend** | Web | React 18 + Vite + TypeScript + Tailwind | `frontend/` |
| **Backend** | API | FastAPI + Python 3.13 + Supabase | `backend/` |

### Key Metrics

- **386** heritage plaques
- **1,157** images
- **104** categories
- **12** API endpoints

---

## Generated Documentation

### Core Documents

- [Project Overview](./project-overview.md) - Executive summary, tech stack, key features
- [Source Tree Analysis](./source-tree-analysis.md) - Directory structure, critical paths

### Architecture

- [Frontend Architecture](./architecture-frontend.md) - React components, state management, routing
- [Backend Architecture](./architecture-backend.md) - FastAPI structure, middleware, database

### Technical Reference

- [API Contracts](./api-contracts.md) - REST API endpoints, request/response schemas
- [Data Models](./data-models.md) - Database schema, relationships, RLS policies

### Development

- [Development Guide](./development-guide.md) - Setup, workflow, testing, debugging

---

## Existing Documentation

- [User Guide](./USER_GUIDE.md) - End-user documentation for the application
- [README](../README.md) - Project overview and quick start

---

## Getting Started

### For Developers

1. Read the [Development Guide](./development-guide.md) for setup instructions
2. Review [Source Tree Analysis](./source-tree-analysis.md) to understand the codebase
3. Check [API Contracts](./api-contracts.md) for endpoint documentation

### For AI-Assisted Development

When creating a brownfield PRD or planning new features:

1. **UI-only features:** Reference [Frontend Architecture](./architecture-frontend.md)
2. **API-only features:** Reference [Backend Architecture](./architecture-backend.md)
3. **Full-stack features:** Reference both architectures + [API Contracts](./api-contracts.md)
4. **Database changes:** Reference [Data Models](./data-models.md)

### Quick Commands

```bash
# Start development (Docker)
docker compose up -d

# Start backend manually
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Start frontend manually
cd frontend && npm run dev

# Run backend tests
cd backend && pytest tests/ -v

# Run E2E tests
cd frontend && npm run test:e2e
```

---

## Document Versions

| Document | Last Updated | Status |
|----------|--------------|--------|
| project-overview.md | 2026-03-19 | ✅ Complete |
| architecture-frontend.md | 2026-03-19 | ✅ Complete |
| architecture-backend.md | 2026-03-19 | ✅ Complete |
| api-contracts.md | 2026-03-19 | ✅ Complete |
| data-models.md | 2026-03-19 | ✅ Complete |
| development-guide.md | 2026-03-19 | ✅ Complete |
| source-tree-analysis.md | 2026-03-19 | ✅ Complete |
| USER_GUIDE.md | 2026-02 | ✅ Existing |

---

## Production Information

**Live URL:** https://blueplaques.leapcell.app

**Deployment Platform:** Leapcell

**Data Source:** [Heritage Portal](https://heritageportal.co.za)
