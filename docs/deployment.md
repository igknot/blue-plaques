# Blue Plaques - Render Deployment

## Overview
The Blue Plaques application is deployed on Render using a Blueprint configuration that manages:
- PostgreSQL database
- FastAPI backend (Python)
- React frontend (static site)

**Live URL:** https://blue-plaques.onrender.com

## Architecture

```
┌─────────────────────────────────────────┐
│  Frontend (Static Site)                 │
│  https://blue-plaques.onrender.com      │
│  - React + TypeScript + Vite            │
│  - Leaflet maps                         │
└──────────────┬──────────────────────────┘
               │ API calls
               ▼
┌─────────────────────────────────────────┐
│  Backend (Web Service)                  │
│  https://blue-plaques.onrender.com      │
│  - FastAPI + Python 3.11.9              │
│  - Uvicorn server                       │
└──────────────┬──────────────────────────┘
               │ SQL queries
               ▼
┌─────────────────────────────────────────┐
│  Database (PostgreSQL)                  │
│  - 390 heritage plaques                 │
│  - Images, categories, metadata         │
└─────────────────────────────────────────┘
```

## Deployment Configuration

### Files
- `render.yaml` - Blueprint configuration
- `.python-version` - Python 3.11.9 (required for dependencies)
- `frontend/src/vite-env.d.ts` - TypeScript types for Vite env vars

### Services

#### 1. Backend Service
- **Name:** blue-plaques-backend
- **Type:** Web Service
- **Runtime:** Python 3.11.9
- **Build:** `pip install -r backend/requirements.txt`
- **Start:** `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  - `DATABASE_URL` - Auto-configured from database
  - `SECRET_KEY` - JWT secret (set manually)
  - `ADMIN_EMAIL` - Admin user email
  - `ADMIN_PASSWORD` - Admin user password
  - `ENVIRONMENT=production`
  - `DEBUG=False`

#### 2. Frontend Service
- **Name:** blue-plaques-frontend
- **Type:** Static Site
- **Build:** `cd frontend && npm install && npm run build`
- **Publish:** `frontend/dist`
- **Environment Variables:**
  - `VITE_API_URL=https://blue-plaques.onrender.com/api/v1`

#### 3. Database
- **Name:** blue-plaques-db
- **Type:** PostgreSQL
- **Database:** blue_plaques
- **User:** blue_plaques_user

## Deployment Process

### Initial Setup

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Create Render Services**
   - Go to https://dashboard.render.com
   - New → Blueprint
   - Connect GitHub repo
   - Render reads `render.yaml` and creates all services

3. **Configure Environment Variables**
   Backend service → Settings → Environment:
   ```
   SECRET_KEY=<generate-with: openssl rand -hex 32>
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=<secure-password>
   ENVIRONMENT=production
   DEBUG=False
   ```

4. **Initialize Database**
   After first deploy, run migration:
   ```bash
   # From local machine with DATABASE_URL from Render
   python migrate_to_postgres.py
   ```

### Continuous Deployment

Every `git push` triggers auto-deploy:
1. Render detects new commit
2. Builds backend (installs Python deps)
3. Builds frontend (npm install + build)
4. Deploys both services
5. Services restart with new code

### Manual Deploy
Dashboard → Service → Manual Deploy → "Deploy latest commit"

## Database Migration

### From SQLite to PostgreSQL

```bash
# 1. Get DATABASE_URL from Render dashboard
export DATABASE_URL="postgresql://user:pass@host/db"

# 2. Run migration script
python migrate_to_postgres.py

# 3. Verify data
psql $DATABASE_URL -c "SELECT COUNT(*) FROM plaques;"
```

## Monitoring

### Logs
- Dashboard → Service → Logs
- Real-time streaming
- Filter by error/warning/info

### Metrics
- Dashboard → Service → Metrics
- CPU, memory, request rate
- Response times

### Health Check
- Backend: https://blue-plaques.onrender.com/docs
- Frontend: https://blue-plaques.onrender.com

## Troubleshooting

### Build Fails

**Python version mismatch:**
- Ensure `.python-version` contains `3.11.9`
- Check `render.yaml` has `PYTHON_VERSION: 3.11.9`

**Dependency errors:**
- Update `backend/requirements.txt` with compatible versions
- Test locally: `pip install -r backend/requirements.txt`

**Frontend build fails:**
- Check `frontend/src/vite-env.d.ts` exists
- Test locally: `cd frontend && npm run build`

### Runtime Errors

**Database connection fails:**
- Verify `DATABASE_URL` is set (auto-configured)
- Check database service is running

**CORS errors:**
- Update `backend/app/main.py` allowed_origins
- Add frontend URL to CORS list

**API not reachable:**
- Verify `VITE_API_URL` in frontend env vars
- Check backend service is running
- Test: `curl https://blue-plaques.onrender.com/api/v1/plaques`

### Performance

**Cold starts (free tier):**
- Services sleep after 15min inactivity
- First request takes ~30s to wake up
- Upgrade to paid tier for always-on

**Slow queries:**
- Check database indexes
- Monitor query performance in logs
- Consider caching with Redis

## Costs

### Free Tier
- 750 hours/month per service
- Services sleep after 15min inactivity
- PostgreSQL: 90-day retention, 1GB storage
- Bandwidth: 100GB/month

### Paid Tier
- Always-on services
- More CPU/memory
- Longer database retention
- Custom domains with SSL

## Security

### Environment Variables
- Never commit secrets to git
- Use Render dashboard to set sensitive vars
- Rotate `SECRET_KEY` periodically

### Database
- Render manages SSL connections
- Automatic backups (paid tier)
- Connection pooling enabled

### CORS
- Production: Whitelist specific domains
- Development: Allow all origins (`DEBUG=True`)

## Rollback

### To Previous Version
1. Dashboard → Service → Deploys
2. Find working deploy
3. Click "Redeploy"

### Via Git
```bash
git revert <commit-hash>
git push
```

## Custom Domain (Optional)

1. Dashboard → Frontend Service → Settings
2. Add Custom Domain
3. Update DNS:
   ```
   CNAME blueplaques.co.za -> blue-plaques.onrender.com
   ```
4. SSL auto-configured by Render

## Backup & Recovery

### Database Backup
```bash
# Export from Render
pg_dump $DATABASE_URL > backup.sql

# Restore
psql $DATABASE_URL < backup.sql
```

### Code Backup
- GitHub is source of truth
- All code versioned in git
- Render deploys from GitHub

## Support

- Render Docs: https://render.com/docs
- Status: https://status.render.com
- Community: https://community.render.com
