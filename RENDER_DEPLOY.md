# Blue Plaques - Render Deployment

## Prerequisites
1. GitHub account
2. Render account (free tier works)
3. Push code to GitHub repo

## Step 1: Prepare Database Migration

The app uses SQLite locally but needs PostgreSQL for Render. Create migration script:

```bash
# Export SQLite data to SQL
sqlite3 blue_plaques.db .dump > data_export.sql
```

## Step 2: Push to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 3: Deploy on Render

1. Go to https://render.com/
2. Click "New +" → "Blueprint"
3. Connect your GitHub repo
4. Render will detect `render.yaml` and create:
   - PostgreSQL database
   - Backend web service (FastAPI)
   - Frontend static site (React)

## Step 4: Configure Environment Variables

Render auto-configures `DATABASE_URL`. Add these manually in backend service:

```
SECRET_KEY=<generate-random-string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=<secure-password>
ENVIRONMENT=production
DEBUG=False
REDIS_URL=<optional-redis-url>
R2_ACCOUNT_ID=<cloudflare-r2-account>
R2_ACCESS_KEY_ID=<r2-key>
R2_SECRET_ACCESS_KEY=<r2-secret>
R2_BUCKET_NAME=blue-plaques
R2_PUBLIC_URL=https://your-r2-url.com
```

## Step 5: Import Data to PostgreSQL

After database is created:

1. Get database connection string from Render dashboard
2. Connect via psql or pgAdmin
3. Run migrations:
```bash
# SSH into backend service or use Render shell
cd backend
alembic upgrade head
```

4. Import data (convert SQLite dump to PostgreSQL format first)

## Step 6: Update Frontend API URL

Frontend env var is set in `render.yaml`:
```yaml
VITE_API_URL: https://blue-plaques-backend.onrender.com
```

Update with your actual backend URL.

## Step 7: Deploy

Render auto-deploys on git push. Manual deploy:
- Go to each service → "Manual Deploy" → "Deploy latest commit"

## URLs

After deployment:
- Frontend: `https://blue-plaques-frontend.onrender.com`
- Backend: `https://blue-plaques-backend.onrender.com`
- API Docs: `https://blue-plaques-backend.onrender.com/docs`

## Notes

- Free tier: Services sleep after 15min inactivity (cold start ~30s)
- Database: 90-day retention on free tier
- Upgrade to paid for always-on services
