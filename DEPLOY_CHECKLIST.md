# Render Deployment Checklist

## Pre-Deploy
- [ ] Code pushed to GitHub
- [ ] `render.yaml` configured
- [ ] Backend env vars have defaults in `config.py`
- [ ] CORS allows Render frontend URL

## Deploy Steps

### 1. Create Render Account
- Sign up at https://render.com (free tier)
- Connect GitHub account

### 2. Deploy via Blueprint
- Dashboard → "New +" → "Blueprint"
- Select your GitHub repo
- Render reads `render.yaml` and creates:
  - PostgreSQL database
  - Backend service (FastAPI)
  - Frontend service (React static)

### 3. Configure Backend Environment
In backend service settings, add:
```
SECRET_KEY=<generate-with: openssl rand -hex 32>
ADMIN_EMAIL=your@email.com
ADMIN_PASSWORD=<secure-password>
ENVIRONMENT=production
DEBUG=False
```

Optional (for image uploads):
```
REDIS_URL=<redis-url>
R2_ACCOUNT_ID=<cloudflare-account>
R2_ACCESS_KEY_ID=<key>
R2_SECRET_ACCESS_KEY=<secret>
R2_BUCKET_NAME=blue-plaques
R2_PUBLIC_URL=https://your-bucket.r2.dev
```

### 4. Update Frontend API URL
In `render.yaml`, update:
```yaml
envVars:
  - key: VITE_API_URL
    value: https://YOUR-BACKEND-NAME.onrender.com/api/v1
```

Replace `YOUR-BACKEND-NAME` with actual backend service name.

### 5. Initialize Database
After backend deploys:
```bash
# Get shell access to backend service (Render dashboard → Shell)
cd backend
python -c "from app.database import engine; from app.models.plaque import Base; Base.metadata.create_all(bind=engine)"
```

### 6. Migrate Data
From local machine:
```bash
# Install psycopg2
pip install psycopg2-binary

# Get DATABASE_URL from Render dashboard
export DATABASE_URL="postgresql://..."

# Run migration
python migrate_to_postgres.py
```

### 7. Test Deployment
- Frontend: `https://YOUR-FRONTEND.onrender.com`
- Backend API: `https://YOUR-BACKEND.onrender.com/docs`
- Test: Search, filters, map markers, detail pages

## Post-Deploy

### Custom Domain (Optional)
- Render dashboard → Frontend service → Settings → Custom Domain
- Add your domain (e.g., blueplaques.co.za)
- Update DNS CNAME record

### Monitoring
- Render provides logs and metrics
- Free tier: Services sleep after 15min inactivity
- Upgrade to paid for always-on

## Troubleshooting

**Build fails:**
- Check logs in Render dashboard
- Verify `requirements.txt` and `package.json` are correct

**Database connection error:**
- Ensure `DATABASE_URL` is set (auto-configured by Render)
- Check database is running

**CORS error:**
- Update `allow_origins` in `backend/app/main.py`
- Add your frontend URL

**Frontend can't reach backend:**
- Verify `VITE_API_URL` in frontend env vars
- Check backend service is running
