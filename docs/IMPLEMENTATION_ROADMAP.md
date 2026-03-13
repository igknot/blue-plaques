# Implementation Roadmap

**Timeline**: 6 weeks  
**Team**: 2 developers (1 backend, 1 frontend)  
**Budget**: ~$12,000

---

## Week 1: Foundation & Data Migration

### Backend Setup (Days 1-2)
- [ ] Create GitHub repository
- [ ] Set up Railway project (PostgreSQL + Redis)
- [ ] Set up CloudFlare R2 bucket
- [ ] Initialize FastAPI project structure
- [ ] Configure environment variables
- [ ] Set up database schema (run SQL migrations)
- [ ] Configure Alembic for future migrations

**Deliverable**: Empty backend with database ready

### Data Migration (Days 3-4)
- [ ] Run migration script (DATA_MIGRATION_PLAN.md)
- [ ] Upload all 1,157 images to R2
- [ ] Verify all 386 plaques in PostgreSQL
- [ ] Test sample queries
- [ ] Document migration results

**Deliverable**: All data migrated and verified

### Authentication (Day 5)
- [ ] Implement JWT auth endpoints
- [ ] Create admin user
- [ ] Test login/logout flow
- [ ] Add auth middleware

**Deliverable**: Working authentication system

---

## Week 2: Core API Development

### Public Endpoints (Days 1-2)
- [ ] `GET /api/v1/plaques` (list with pagination)
- [ ] `GET /api/v1/plaques/:id` (single plaque)
- [ ] `GET /api/v1/plaques/nearby` (geo query)
- [ ] `GET /api/v1/categories` (list categories)
- [ ] Add Redis caching
- [ ] Write unit tests

**Deliverable**: Public API working

### Admin Endpoints (Days 3-4)
- [ ] `POST /api/v1/plaques` (create)
- [ ] `PUT /api/v1/plaques/:id` (update)
- [ ] `POST /api/v1/plaques/:id/images` (upload)
- [ ] `DELETE /api/v1/images/:id` (delete)
- [ ] Add authorization checks
- [ ] Write unit tests

**Deliverable**: Admin API working

### Documentation (Day 5)
- [ ] Generate OpenAPI docs (automatic with FastAPI)
- [ ] Test all endpoints with Postman
- [ ] Write API usage examples
- [ ] Deploy to Railway staging

**Deliverable**: API deployed and documented

---

## Week 3: Frontend Foundation

### Project Setup (Day 1)
- [ ] Initialize Vite + React + TypeScript
- [ ] Configure Tailwind CSS
- [ ] Set up React Router
- [ ] Configure TanStack Query
- [ ] Set up Zustand stores
- [ ] Create folder structure

**Deliverable**: Empty frontend with routing

### Core Components (Days 2-3)
- [ ] Map component (React-Leaflet)
- [ ] Marker clustering
- [ ] Plaque popup component
- [ ] Search bar component
- [ ] Filter panel component
- [ ] Loading spinner
- [ ] Error boundary

**Deliverable**: Basic map with markers

### State Management (Day 4)
- [ ] Auth store (Zustand)
- [ ] Map store (Zustand)
- [ ] Filter store (Zustand)
- [ ] API client (Axios)
- [ ] React Query hooks

**Deliverable**: State management working

### Styling (Day 5)
- [ ] Design system (colors, spacing, typography)
- [ ] Responsive layout
- [ ] Mobile-first CSS
- [ ] Dark mode support (optional)

**Deliverable**: Styled components

---

## Week 4: Feature Implementation

### Search & Filter (Days 1-2)
- [ ] Real-time search
- [ ] Category filtering
- [ ] Bulk select/clear
- [ ] URL state sync (query params)
- [ ] Empty states

**Deliverable**: Search and filter working

### Image Gallery (Day 3)
- [ ] Lightbox component
- [ ] Keyboard navigation
- [ ] Touch gestures (mobile)
- [ ] Image lazy loading
- [ ] Captions

**Deliverable**: Image gallery working

### Geolocation (Day 4)
- [ ] "Find Near Me" button
- [ ] User location marker
- [ ] Permission handling
- [ ] Error states

**Deliverable**: Geolocation working

### Testing (Day 5)
- [ ] Component tests (Vitest)
- [ ] E2E tests (Playwright)
- [ ] Accessibility audit
- [ ] Browser compatibility testing

**Deliverable**: Tests passing

---

## Week 5: Admin Features

### Admin Dashboard (Days 1-2)
- [ ] Login page
- [ ] Dashboard layout
- [ ] Plaque list view
- [ ] Report queue
- [ ] Statistics

**Deliverable**: Admin dashboard

### Plaque Management (Days 3-4)
- [ ] Create plaque form
- [ ] Edit plaque form
- [ ] Image upload (drag & drop)
- [ ] Image reordering
- [ ] Delete confirmation
- [ ] Form validation

**Deliverable**: CRUD operations working

### Testing & Polish (Day 5)
- [ ] Admin workflow testing
- [ ] Error handling
- [ ] Loading states
- [ ] Success messages
- [ ] Audit logging

**Deliverable**: Admin features complete

---

## Week 6: Deployment & Launch

### Performance Optimization (Days 1-2)
- [ ] Code splitting
- [ ] Image optimization
- [ ] Bundle size analysis
- [ ] Lighthouse audit (score >90)
- [ ] Load testing (k6)

**Deliverable**: Optimized application

### Deployment (Day 3)
- [ ] Deploy frontend to Vercel
- [ ] Deploy backend to Railway production
- [ ] Configure custom domain
- [ ] Set up SSL certificates
- [ ] Configure CDN

**Deliverable**: Production deployment

### Monitoring & Analytics (Day 4)
- [ ] Set up Sentry error tracking
- [ ] Configure Plausible analytics
- [ ] Set up uptime monitoring
- [ ] Create runbook for incidents
- [ ] Set up automated backups

**Deliverable**: Monitoring active

### Launch (Day 5)
- [ ] Final QA testing
- [ ] User acceptance testing
- [ ] Create launch announcement
- [ ] Update documentation
- [ ] Go live! 🚀

**Deliverable**: Public launch

---

## Post-Launch (Week 7+)

### Immediate (Week 7)
- [ ] Monitor error rates
- [ ] Fix critical bugs
- [ ] Gather user feedback
- [ ] Performance tuning

### Short-Term (Weeks 8-12)
- [ ] Share links feature
- [ ] User favorites (localStorage)
- [ ] Advanced search (fuzzy)
- [ ] Print-friendly view

### Medium-Term (Months 4-6)
- [ ] Offline support (PWA)
- [ ] Route planning
- [ ] Multi-language support
- [ ] Mobile app (React Native)

---

## Resource Allocation

### Backend Developer (Week 1-2)
- Database setup & migration
- API development
- Authentication
- Testing

### Frontend Developer (Week 3-4)
- React setup
- Component development
- State management
- Feature implementation

### Both Developers (Week 5-6)
- Admin features
- Testing
- Deployment
- Launch preparation

---

## Risk Mitigation

### Technical Risks

**Risk**: Data migration fails  
**Mitigation**: Test migration on copy first, keep SQLite backup

**Risk**: Performance issues with 386 markers  
**Mitigation**: Implement clustering, test with 1000+ markers

**Risk**: Image upload failures  
**Mitigation**: Implement retry logic, show progress

### Schedule Risks

**Risk**: Features take longer than estimated  
**Mitigation**: Cut non-essential features, focus on MVP

**Risk**: Bugs delay launch  
**Mitigation**: Allocate buffer time in Week 6

---

## Success Criteria

### Technical
- [ ] All 386 plaques migrated successfully
- [ ] All 1,157 images accessible via CDN
- [ ] API response time <500ms (p95)
- [ ] Page load time <2s (p95)
- [ ] Lighthouse score >90
- [ ] Zero critical security vulnerabilities
- [ ] 80%+ test coverage

### Functional
- [ ] Users can browse all plaques
- [ ] Search returns relevant results
- [ ] Filters work correctly
- [ ] Images load and display properly
- [ ] Geolocation works on mobile
- [ ] Admin can add/edit plaques
- [ ] Admin can upload images

### User Experience
- [ ] Mobile-responsive design
- [ ] Intuitive navigation
- [ ] Fast and smooth interactions
- [ ] Clear error messages
- [ ] Accessible (WCAG AA)

---

## Budget Breakdown

### Development (6 weeks)
- Backend Developer: 120 hours × $100/hr = $12,000
- Frontend Developer: 120 hours × $100/hr = $12,000
- **Total Development**: $24,000

### Infrastructure (Annual)
- Railway (PostgreSQL + Backend): $20/month = $240/year
- Vercel (Frontend): Free tier
- CloudFlare R2: $0.015/GB storage + $0.36/million requests ≈ $50/year
- CloudFlare CDN: Free tier
- Domain: $15/year
- Sentry: Free tier (up to 5k events/month)
- Plausible: $9/month = $108/year
- **Total Infrastructure**: $413/year

### Total First Year
- Development: $24,000 (one-time)
- Infrastructure: $413 (recurring)
- **Total**: $24,413

### Ongoing (Year 2+)
- Infrastructure: $413/year
- Maintenance: 10 hours/month × $100/hr = $12,000/year
- **Total**: $12,413/year

---

## Comparison: Rebuild vs Fix Prototype

| Aspect | Fix Prototype | Rebuild |
|--------|--------------|---------|
| **Timeline** | 4 weeks | 6 weeks |
| **Cost** | $7,400 | $24,000 |
| **Security** | Patched | Built-in |
| **Scalability** | Limited | High |
| **Maintainability** | Low | High |
| **Test Coverage** | Added later | Built-in |
| **Type Safety** | None | Full |
| **Modern Stack** | No | Yes |
| **Technical Debt** | High | Low |

**Recommendation**: Rebuild is 2x cost but 10x better long-term investment.

---

## Next Steps

1. **Approve specification** and budget
2. **Hire developers** (or assign team)
3. **Set up infrastructure** (Railway, R2, Vercel)
4. **Start Week 1** (foundation & migration)
5. **Weekly check-ins** to track progress
6. **Launch in 6 weeks** 🚀
