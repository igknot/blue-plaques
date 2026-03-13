#!/bin/bash
# Blue Plaques v2.0 - Deployment Script

set -e

echo "🚀 Blue Plaques v2.0 - Deployment"
echo "=================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo "✅ Prerequisites installed"
echo ""

# Railway setup
echo "📦 Setting up Railway..."
echo "1. Login to Railway"
railway login

echo "2. Create new project (or link existing)"
railway init

echo "3. Add PostgreSQL"
railway add --plugin postgresql

echo "4. Add Redis"
railway add --plugin redis

echo "5. Get database URL"
railway variables

echo ""
echo "⚠️  IMPORTANT: Copy the DATABASE_URL and REDIS_URL from above"
echo "   Update backend/.env with these values"
echo ""
read -p "Press Enter when you've updated backend/.env..."

# Deploy backend
echo ""
echo "📦 Deploying backend to Railway..."
cd backend
railway up

echo ""
echo "✅ Backend deployed!"
echo ""

# Get backend URL
BACKEND_URL=$(railway status --json | grep -o '"url":"[^"]*' | cut -d'"' -f4)
echo "Backend URL: $BACKEND_URL"

# Update frontend env
cd ../frontend
echo "VITE_API_URL=${BACKEND_URL}/api/v1" > .env

# Deploy frontend
echo ""
echo "📦 Deploying frontend to Vercel..."
vercel --prod

echo ""
echo "=================================="
echo "✅ Deployment Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Run database schema: railway run psql < backend/schema.sql"
echo "2. Create admin user: railway run python create_admin.py"
echo "3. Run migration: railway run python migrate_data.py"
echo ""
echo "Your app is live! 🎉"
