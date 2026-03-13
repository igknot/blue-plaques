"""Create admin user for Blue Plaques"""
from app.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash
from app.config import settings

def create_admin():
    db = SessionLocal()
    
    # Check if admin exists
    existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if existing:
        print(f"✅ Admin already exists: {settings.ADMIN_EMAIL}")
        return
    
    # Create admin
    admin = User(
        email=settings.ADMIN_EMAIL,
        hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
        is_active=1,
        is_admin=1
    )
    db.add(admin)
    db.commit()
    
    print(f"✅ Admin created: {settings.ADMIN_EMAIL}")
    print(f"   Password: {settings.ADMIN_PASSWORD}")
    print("")
    print("⚠️  IMPORTANT: Change this password after first login!")

if __name__ == "__main__":
    create_admin()
