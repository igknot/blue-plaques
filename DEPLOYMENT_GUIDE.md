# Blue Plaques v2.0 - Deployment Guide

## Week 1 Complete ✅

### What's Been Built

**Backend (FastAPI)**
- ✅ Database models (Plaque, Image, Category, User)
- ✅ Pydantic schemas with validation
- ✅ JWT authentication system
- ✅ Public API endpoints (list, get, nearby)
- ✅ Admin API endpoints (create, update, delete)
- ✅ Image upload to R2
- ✅ Redis caching layer
- ✅ PostgreSQL + PostGIS setup

**Frontend (React + TypeScript)**
- ✅ Vite + React 18 setup
- ✅ TypeScript types
- ✅ Zustand stores (auth, map)
- ✅ TanStack Query hooks
- ✅ Leaflet map with clustering
- ✅ Tailwind CSS styling

**Migration**
- ✅ Data migration script (SQLite → PostgreSQL + R2)
- ✅ Handles 386 plaques + 1,157 images

---

## Next Steps: Deploy & Migrate

### 1. Set Up Infrastructure

#### Railway (PostgreSQL + Backend)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create project
railway init

# Add PostgreSQL
railway add postgresql

# Add Redis
railway add redis

# Deploy backend
cd backend
railway up
```

#### CloudFlare R2 (Image Storage)
1. Go to CloudFlare Dashboard
2. Create R2 bucket: `blue-plaques-images`
3. Get credentials:
   - Account ID
   - Access Key ID
   - Secret Access Key
4. Configure public access

#### Vercel (Frontend)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel
```

### 2. Configure Environment Variables

**Backend (.env)**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
R2_ACCOUNT_ID=your_account_id
R2_ACCESS_KEY_ID=your_key
R2_SECRET_ACCESS_KEY=your_secret
R2_BUCKET_NAME=blue-plaques-images
R2_PUBLIC_URL=https://images.blueplaques.co.za
SECRET_KEY=generate-with-openssl-rand-hex-32
ADMIN_EMAIL=admin@blueplaques.co.za
ADMIN_PASSWORD=secure-password-here
```

**Frontend (.env)**
```bash
VITE_API_URL=https://api.blueplaques.co.za/api/v1
```

### 3. Run Database Schema

```bash
# Connect to Railway PostgreSQL
railway connect postgresql

# Run schema
\i backend/schema.sql
```

### 4. Create Admin User

```python
# backend/create_admin.py
from app.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash
from app.config import settings

db = SessionLocal()
admin = User(
    email=settings.ADMIN_EMAIL,
    hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
    is_active=1,
    is_admin=1
)
db.add(admin)
db.commit()
print(f"Admin created: {admin.email}")
```

### 5. Run Data Migration

```bash
cd backend
python migrate_data.py
```

Expected output:
```
📦 Extracting plaques from SQLite...
✅ Extracted 386 plaques
📦 Extracting images from SQLite...
✅ Extracted 1,157 images
🚀 Migrating plaques to PostgreSQL...
✅ Migrated 386 plaques
🚀 Migrating images to R2 and PostgreSQL...
  📤 Uploaded 100/1157 images...
  📤 Uploaded 200/1157 images...
  ...
✅ Migrated 1,157 images (0 failed)
🔍 Verifying migration...
✅ Verification complete:
   Plaques: 386
   Images: 1,157
```

### 6. Test Deployment

**Backend Health Check**
```bash
curl https://api.blueplaques.co.za/health
# {"status":"healthy"}
```

**Test API**
```bash
curl https://api.blueplaques.co.za/api/v1/plaques?page=1&page_size=10
```

**Test Frontend**
```bash
open https://blueplaques.co.za
```

---

## Week 2-6 Roadmap

### Week 2: Polish API
- Add rate limiting
- Improve error handling
- Write comprehensive tests
- Add API documentation

### Week 3: Complete Frontend
- Search & filter UI
- Image gallery/lightbox
- Plaque detail page
- Mobile responsive design

### Week 4: Admin Dashboard
- Login page
- Plaque management UI
- Image upload interface
- Category management

### Week 5: Testing & Optimization
- E2E tests with Playwright
- Performance optimization
- Accessibility audit
- Security audit

### Week 6: Launch
- Final QA
- Monitoring setup (Sentry)
- Analytics (Plausible)
- Go live!

---

## Cost Estimate

### Monthly Costs
- Railway (PostgreSQL + Backend): $20/month
- CloudFlare R2: ~$5/month
- Vercel: Free tier
- **Total: ~$25/month**

### Annual Costs
- Infrastructure: $300/year
- Domain: $15/year
- Monitoring (Sentry): Free tier
- Analytics (Plausible): $108/year
- **Total: $423/year**

---

## Monitoring

### Sentry (Error Tracking)
```bash
# Backend
pip install sentry-sdk[fastapi]

# Frontend
npm install @sentry/react
```

### Plausible (Analytics)
Add to `frontend/index.html`:
```html
<script defer data-domain="blueplaques.co.za" src="https://plausible.io/js/script.js"></script>
```

---

## Backup Strategy

### Database Backups
Railway provides automatic daily backups. For additional safety:

```bash
# Manual backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restore
psql $DATABASE_URL < backup_20240312.sql
```

### Image Backups
R2 has built-in redundancy. For additional safety, sync to local:

```bash
aws s3 sync s3://blue-plaques-images ./backup/images --endpoint-url=https://...
```

---

## Support

- **Technical Issues**: Check logs in Railway dashboard
- **API Errors**: Check Sentry dashboard
- **Performance**: Check Railway metrics
- **Uptime**: Set up UptimeRobot (free)

---

## Success Metrics

After deployment, verify:
- [ ] All 386 plaques visible on map
- [ ] All 1,157 images loading from R2
- [ ] Search returns results
- [ ] Mobile responsive
- [ ] Admin login works
- [ ] API response time < 500ms
- [ ] Page load time < 2s
- [ ] Lighthouse score > 90

---

**Status**: Week 1 Complete - Ready for Deployment! 🚀
