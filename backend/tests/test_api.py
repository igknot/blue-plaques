import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, Plaque, Category
from app.core.security import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def admin_token(client):
    # Create admin user
    db = TestingSessionLocal()
    admin = User(
        email="admin@test.com",
        hashed_password=get_password_hash("admin123"),
        is_active=1,
        is_admin=1
    )
    db.add(admin)
    db.commit()
    db.close()
    
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    return response.json()["access_token"]

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_list_plaques_empty(client):
    response = client.get("/api/v1/plaques")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["plaques"] == []

def test_create_plaque_unauthorized(client):
    response = client.post("/api/v1/plaques", json={
        "title": "Test Plaque",
        "latitude": -26.2041,
        "longitude": 28.0473
    })
    assert response.status_code == 403

def test_create_plaque_authorized(client, admin_token):
    response = client.post(
        "/api/v1/plaques",
        json={
            "title": "Test Plaque",
            "description": "Test description",
            "latitude": -26.2041,
            "longitude": 28.0473,
            "address": "Johannesburg"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Plaque"
    assert data["latitude"] == -26.2041

def test_get_plaque(client, admin_token):
    # Create plaque
    create_response = client.post(
        "/api/v1/plaques",
        json={
            "title": "Test Plaque",
            "latitude": -26.2041,
            "longitude": 28.0473
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    plaque_id = create_response.json()["id"]
    
    # Get plaque
    response = client.get(f"/api/v1/plaques/{plaque_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Plaque"

def test_update_plaque(client, admin_token):
    # Create plaque
    create_response = client.post(
        "/api/v1/plaques",
        json={
            "title": "Original Title",
            "latitude": -26.2041,
            "longitude": 28.0473
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    plaque_id = create_response.json()["id"]
    
    # Update plaque
    response = client.put(
        f"/api/v1/plaques/{plaque_id}",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

def test_delete_plaque(client, admin_token):
    # Create plaque
    create_response = client.post(
        "/api/v1/plaques",
        json={
            "title": "To Delete",
            "latitude": -26.2041,
            "longitude": 28.0473
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    plaque_id = create_response.json()["id"]
    
    # Delete plaque
    response = client.delete(
        f"/api/v1/plaques/{plaque_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Verify deleted
    get_response = client.get(f"/api/v1/plaques/{plaque_id}")
    assert get_response.status_code == 404

def test_login_invalid_credentials(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "wrong@test.com",
        "password": "wrong"
    })
    assert response.status_code == 401

def test_search_plaques(client, admin_token):
    # Create test plaques
    client.post(
        "/api/v1/plaques",
        json={"title": "Nelson Mandela House", "latitude": -26.2041, "longitude": 28.0473},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    client.post(
        "/api/v1/plaques",
        json={"title": "Desmond Tutu House", "latitude": -26.2041, "longitude": 28.0473},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Search
    response = client.get("/api/v1/plaques?search=Mandela")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert "Mandela" in data["plaques"][0]["title"]
