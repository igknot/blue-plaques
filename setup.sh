#!/bin/bash
# Blue Plaques v2.0 - Quick Start Script

set -e

echo "=================================================="
echo "Blue Plaques v2.0 - Quick Start"
echo "=================================================="
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.13+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL client not found. You'll need it for database setup."
fi

echo "✅ Prerequisites OK"
echo ""

# Backend setup
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

echo "  Activating virtual environment..."
source venv/bin/activate

echo "  Installing dependencies..."
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo "  Creating .env file..."
    cp .env.example .env
    echo "  ⚠️  Please edit backend/.env with your credentials"
fi

cd ..
echo "✅ Backend setup complete"
echo ""

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "  Installing dependencies..."
    npm install
fi

if [ ! -f ".env" ]; then
    echo "  Creating .env file..."
    echo "VITE_API_URL=http://localhost:8000/api/v1" > .env
fi

cd ..
echo "✅ Frontend setup complete"
echo ""

# Instructions
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure environment variables:"
echo "   - Edit backend/.env with your database and R2 credentials"
echo ""
echo "2. Set up database:"
echo "   psql \$DATABASE_URL -f backend/schema.sql"
echo ""
echo "3. Create admin user:"
echo "   cd backend && python -c \"from app.database import SessionLocal; from app.models import User; from app.core.security import get_password_hash; from app.config import settings; db = SessionLocal(); admin = User(email=settings.ADMIN_EMAIL, hashed_password=get_password_hash(settings.ADMIN_PASSWORD), is_active=1, is_admin=1); db.add(admin); db.commit(); print(f'Admin created: {admin.email}')\""
echo ""
echo "4. Run data migration:"
echo "   cd backend && python migrate_data.py"
echo ""
echo "5. Start development servers:"
echo "   Terminal 1: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "   Terminal 2: cd frontend && npm run dev"
echo ""
echo "6. Visit:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "=================================================="
echo "For deployment instructions, see DEPLOYMENT_GUIDE.md"
echo "=================================================="
