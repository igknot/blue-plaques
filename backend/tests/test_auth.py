from unittest.mock import patch
from fastapi.testclient import TestClient
from tests.conftest import make_mock_supabase, MockQueryBuilder, SAMPLE_USER


def test_login_success():
    mock_sb = make_mock_supabase(
        table_responses={"users": MockQueryBuilder(data=[SAMPLE_USER])}
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.auth.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.post("/api/v1/auth/login", json={
            "email": "admin@test.com", "password": "testpass123"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


def test_login_wrong_password():
    mock_sb = make_mock_supabase(
        table_responses={"users": MockQueryBuilder(data=[SAMPLE_USER])}
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.auth.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.post("/api/v1/auth/login", json={
            "email": "admin@test.com", "password": "wrongpassword"
        })
        assert resp.status_code == 401


def test_login_user_not_found():
    mock_sb = make_mock_supabase(
        table_responses={"users": MockQueryBuilder(data=[])}
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.auth.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.post("/api/v1/auth/login", json={
            "email": "nobody@test.com", "password": "whatever"
        })
        assert resp.status_code == 401


def test_login_inactive_user():
    inactive_user = {**SAMPLE_USER, "is_active": 0}
    mock_sb = make_mock_supabase(
        table_responses={"users": MockQueryBuilder(data=[inactive_user])}
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.auth.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.post("/api/v1/auth/login", json={
            "email": "admin@test.com", "password": "testpass123"
        })
        assert resp.status_code == 403


def test_login_invalid_email(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "not-an-email", "password": "test"
    })
    assert resp.status_code == 422
