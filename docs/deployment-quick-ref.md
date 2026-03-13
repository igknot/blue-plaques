# Deployment Quick Reference

## Current Deployment

**Platform:** Render  
**URL:** https://blue-plaques.onrender.com  
**Status:** Production  
**Last Deploy:** 2026-03-13

## Services

| Service | Type | URL | Status |
|---------|------|-----|--------|
| Frontend | Static Site | https://blue-plaques.onrender.com | ✅ |
| Backend | Web Service | https://blue-plaques.onrender.com/api/v1 | ✅ |
| Database | PostgreSQL | Internal | ✅ |

## Quick Commands

### Deploy
```bash
git push origin main  # Auto-deploys
```

### Check Status
```bash
curl https://blue-plaques.onrender.com/api/v1/plaques?page_size=1
```

### View Logs
Dashboard → Service → Logs

### Rollback
Dashboard → Service → Deploys → Select previous → Redeploy

## Environment Variables

### Backend (Required)
```
DATABASE_URL=<auto-configured>
SECRET_KEY=<generate-with: openssl rand -hex 32>
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=<secure-password>
ENVIRONMENT=production
DEBUG=False
```

### Frontend
```
VITE_API_URL=https://blue-plaques.onrender.com/api/v1
```

## Common Issues

### Build Fails
- Check `.python-version` is `3.11.9`
- Verify `frontend/src/vite-env.d.ts` exists
- Test locally with pre-push hook

### Service Won't Start
- Check start command in dashboard
- Backend: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- View logs for errors

### Database Issues
- Verify `DATABASE_URL` is set
- Check database service is running
- Run migration if needed: `python migrate_to_postgres.py`

## Links

- Dashboard: https://dashboard.render.com
- API Docs: https://blue-plaques.onrender.com/docs
- GitHub: https://github.com/igknot/blue-plaques
- Full Docs: [./deployment.md](./deployment.md)
