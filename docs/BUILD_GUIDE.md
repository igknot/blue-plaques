# Blue Plaques Map v2.0 - Build Guide

**START HERE** when beginning the rebuild in a new session.

---

## Quick Context

**What**: Rebuilding Blue Plaques Map (heritage site discovery platform)  
**Why**: Current prototype has security vulnerabilities, needs modern stack  
**Key Constraint**: **PRESERVE ALL DATA** - 386 plaques + 1,157 images must be migrated  
**Timeline**: 6 weeks  
**Budget**: $20,000 development + $413/year infrastructure

---

## Essential Documents (Read in Order)

### 1. **PROJECT_SUMMARY.md** (15 min read)
**Purpose**: Understand current state and why we're rebuilding  
**Key Sections**:
- Current prototype analysis (ratings, strengths, weaknesses)
- Critical security issues (hardcoded password, no auth, no validation)
- Specification vs implementation gap
- Team recommendations

**Read this first** to understand the problem we're solving.

---

### 2. **REBUILD_SPECIFICATION.md** (30 min read)
**Purpose**: Complete technical specification for v2.0  
**Key Sections**:
- Technology stack (FastAPI + React + PostgreSQL + R2)
- Architecture overview (diagrams included)
- Database schema (normalized with PostGIS)
- API design (all endpoints documented)
- Frontend architecture (React components)
- Security implementation (JWT auth)
- Deployment configuration

**This is your primary reference** during development.

---

### 3. **DATA_MIGRATION_PLAN.md** (20 min read)
**Purpose**: Step-by-step guide to migrate existing data  
**Key Sections**:
- Extract data from SQLite (386 plaques, 1,157 images)
- Upload images to CloudFlare R2
- Insert into PostgreSQL
- Verification procedures
- Complete Python migration script

**Run this in Week 1** to preserve all existing content.

---

### 4. **IMPLEMENTATION_ROADMAP.md** (15 min read)
**Purpose**: Week-by-week development plan  
**Key Sections**:
- Week 1: Foundation & data migration
- Week 2: Core API development
- Week 3: Frontend foundation
- Week 4: Feature implementation
- Week 5: Admin features
- Week 6: Deployment & launch

**Use this to track progress** and stay on schedule.

---

## Quick Start Checklist

### Before You Start
- [ ] Read PROJECT_SUMMARY.md (understand the "why")
- [ ] Read REBUILD_SPECIFICATION.md (understand the "what")
- [ ] Read DATA_MIGRATION_PLAN.md (understand data preservation)
- [ ] Read IMPLEMENTATION_ROADMAP.md (understand the "when")

### Week 1 Setup
- [ ] Create GitHub repository
- [ ] Set up Railway (PostgreSQL + Redis)
- [ ] Set up CloudFlare R2 bucket
- [ ] Set up Vercel project
- [ ] Configure environment variables
- [ ] Run database schema migrations
- [ ] **Run data migration script** (preserve 386 plaques + 1,157 images)
- [ ] Verify all data migrated successfully

### Development
- [ ] Follow IMPLEMENTATION_ROADMAP.md week-by-week
- [ ] Reference REBUILD_SPECIFICATION.md for technical details
- [ ] Write tests as you build (TDD approach)
- [ ] Deploy to staging frequently

---

## Critical Principles

### 1. **Data Preservation is Paramount**
```
❌ DO NOT recreate the 386 plaques manually
❌ DO NOT re-scrape Heritage Portal
✅ DO run the migration script (DATA_MIGRATION_PLAN.md)
✅ DO verify all 386 plaques + 1,157 images migrated
✅ DO keep SQLite backup for 30 days
```

### 2. **Security First**
```
✅ Implement JWT auth from day 1
✅ Validate all inputs with Pydantic
✅ Never hardcode passwords
✅ Use environment variables for secrets
✅ Add rate limiting
```

### 3. **Test as You Build**
```
✅ Write unit tests for all API endpoints
✅ Write component tests for React components
✅ Write E2E tests for critical user flows
✅ Target 80%+ test coverage
```

### 4. **Mobile First**
```
✅ Design for mobile screens first
✅ Test on real mobile devices
✅ Optimize images for mobile bandwidth
✅ Use responsive breakpoints
```

---

## Technology Stack Reference

### Backend
```yaml
Language: Python 3.13
Framework: FastAPI 0.110+
Database: PostgreSQL 16 + PostGIS
Cache: Redis 7
Auth: JWT
ORM: SQLAlchemy 2.0
Validation: Pydantic v2
Testing: Pytest
```

### Frontend
```yaml
Framework: React 18 + TypeScript
Build: Vite
State: Zustand + TanStack Query
Styling: Tailwind CSS
Maps: React-Leaflet
Testing: Vitest + Playwright
```

### Infrastructure
```yaml
Frontend: Vercel
Backend: Railway
Database: Railway PostgreSQL
Storage: CloudFlare R2
CDN: CloudFlare
Monitoring: Sentry
Analytics: Plausible
```

---

## Key Files to Reference During Build

### Database Schema
**Location**: REBUILD_SPECIFICATION.md → "Database Schema" section  
**Use when**: Creating migrations, writing queries

### API Endpoints
**Location**: REBUILD_SPECIFICATION.md → "API Design" section  
**Use when**: Implementing backend routes

### Component Structure
**Location**: REBUILD_SPECIFICATION.md → "Frontend Architecture" section  
**Use when**: Creating React components

### Migration Script
**Location**: DATA_MIGRATION_PLAN.md → "Complete Migration Script" section  
**Use when**: Week 1 data migration

### Environment Variables
**Location**: REBUILD_SPECIFICATION.md → "Deployment Configuration" section  
**Use when**: Setting up infrastructure

---

## Common Questions

### Q: Do I need to recreate the plaque data?
**A**: NO! Run the migration script in DATA_MIGRATION_PLAN.md. All 386 plaques and 1,157 images will be automatically migrated from the existing SQLite database.

### Q: What if the migration fails?
**A**: The original SQLite database remains untouched. You can retry the migration or rollback. See DATA_MIGRATION_PLAN.md → "Rollback Plan".

### Q: Can I use different technologies?
**A**: The specification is optimized for the chosen stack. Changing technologies requires re-evaluating architecture, costs, and timeline. Discuss with team first.

### Q: What if I'm behind schedule?
**A**: Cut non-essential features (share links, advanced search, offline support). Focus on core functionality: browse, search, filter, view images.

### Q: Where do I deploy?
**A**: Frontend to Vercel, backend to Railway. Both have free tiers for development. See REBUILD_SPECIFICATION.md → "Deployment Configuration".

### Q: How do I test the migration?
**A**: Run migration on a copy of the database first. Verify counts match (386 plaques, 1,157 images). Check sample plaques. See DATA_MIGRATION_PLAN.md → "Verification".

---

## Support Documents (Reference as Needed)

### Original Prototype Analysis
- **FUNCTIONAL_SPEC.md** - Original specification (what was planned)
- **URGENT_FIXES.md** - Security fixes applied to prototype
- **USER_GUIDE.md** - How users interact with the map
- **ADMIN_GUIDE.md** - Admin features (for reference)
- **API_DOCUMENTATION.md** - Current API (being replaced)
- **TECHNICAL_ARCHITECTURE.md** - Current architecture (being replaced)
- **IMPROVEMENT_RECOMMENDATIONS.md** - Why we're rebuilding

**Note**: These document the OLD system. Use for context only, not as build instructions.

---

## Week-by-Week Focus

### Week 1: Foundation
**Primary Doc**: DATA_MIGRATION_PLAN.md  
**Goal**: Infrastructure setup + data migration  
**Success**: All 386 plaques + 1,157 images in PostgreSQL + R2

### Week 2: Backend
**Primary Doc**: REBUILD_SPECIFICATION.md (API Design section)  
**Goal**: All API endpoints working  
**Success**: Can CRUD plaques via API, tests passing

### Week 3: Frontend Foundation
**Primary Doc**: REBUILD_SPECIFICATION.md (Frontend Architecture section)  
**Goal**: Map with markers, basic UI  
**Success**: Can view plaques on map

### Week 4: Features
**Primary Doc**: IMPLEMENTATION_ROADMAP.md (Week 4)  
**Goal**: Search, filter, gallery, geolocation  
**Success**: All core features working

### Week 5: Admin
**Primary Doc**: IMPLEMENTATION_ROADMAP.md (Week 5)  
**Goal**: Admin dashboard and CRUD  
**Success**: Can manage plaques via UI

### Week 6: Launch
**Primary Doc**: IMPLEMENTATION_ROADMAP.md (Week 6)  
**Goal**: Deploy to production  
**Success**: Live at blueplaques.co.za

---

## Emergency Contacts

**Technical Questions**: Reference REBUILD_SPECIFICATION.md  
**Data Migration Issues**: Reference DATA_MIGRATION_PLAN.md  
**Schedule Concerns**: Reference IMPLEMENTATION_ROADMAP.md  
**Architecture Decisions**: Reference PROJECT_SUMMARY.md

---

## Success Criteria

At the end of 6 weeks, you should have:

✅ All 386 plaques migrated and accessible  
✅ All 1,157 images on CDN and loading  
✅ Working authentication (JWT)  
✅ Public API (browse, search, filter)  
✅ Admin API (CRUD operations)  
✅ React frontend (mobile-responsive)  
✅ 80%+ test coverage  
✅ Deployed to production  
✅ Monitoring active (Sentry)  
✅ Documentation updated  

---

## Final Checklist Before Starting

- [ ] I understand why we're rebuilding (read PROJECT_SUMMARY.md)
- [ ] I know the technical architecture (read REBUILD_SPECIFICATION.md)
- [ ] I know how to preserve data (read DATA_MIGRATION_PLAN.md)
- [ ] I have the week-by-week plan (read IMPLEMENTATION_ROADMAP.md)
- [ ] I have access to infrastructure (Railway, R2, Vercel)
- [ ] I have the SQLite database (blue_plaques.db)
- [ ] I have the images folder (static/images/)
- [ ] I'm ready to start Week 1! 🚀

---

## TL;DR - Absolute Minimum

If you only read ONE document: **REBUILD_SPECIFICATION.md**

If you only do ONE thing in Week 1: **Run the migration script** (DATA_MIGRATION_PLAN.md)

If you only remember ONE principle: **Preserve all 386 plaques + 1,157 images**

---

**Good luck! The BMAD team believes in you.** 🎯

**Questions?** Re-read the relevant document above or ask for clarification.
