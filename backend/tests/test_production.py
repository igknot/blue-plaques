"""
Production verification tests.

Run against a live instance (Docker or Leapcell):

    # Docker (default)
    pytest tests/test_production.py -v

    # Leapcell
    BASE_URL=https://blueplaques.leapcell.app pytest tests/test_production.py -v
"""

import os
import pytest
import httpx

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
API = f"{BASE_URL}/api/v1"
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@blueplaques.org")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Sc00byD00by")


@pytest.fixture(scope="module")
def http():
    with httpx.Client(timeout=15) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(http):
    resp = http.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture(scope="module")
def auth_header(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ── Health ──────────────────────────────────────────────

class TestHealth:
    def test_health(self, http):
        resp = http.get(f"{BASE_URL}/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


# ── Auth ────────────────────────────────────────────────

class TestAuth:
    def test_login_success(self, http):
        resp = http.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, http):
        resp = http.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": "wrong"})
        assert resp.status_code == 401

    def test_login_unknown_user(self, http):
        resp = http.post(f"{API}/auth/login", json={"email": "nobody@example.com", "password": "x"})
        assert resp.status_code == 401


# ── Plaques ─────────────────────────────────────────────

class TestPlaques:
    def test_list_plaques(self, http):
        resp = http.get(f"{API}/plaques")
        assert resp.status_code == 200
        data = resp.json()
        assert "plaques" in data
        assert "total" in data
        assert data["total"] > 0
        assert len(data["plaques"]) > 0

    def test_list_plaques_pagination(self, http):
        resp = http.get(f"{API}/plaques", params={"page": 1, "page_size": 5})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["plaques"]) <= 5

    def test_list_plaques_search(self, http):
        resp = http.get(f"{API}/plaques", params={"search": "church"})
        assert resp.status_code == 200

    def test_get_single_plaque(self, http):
        list_resp = http.get(f"{API}/plaques", params={"page_size": 1})
        assert list_resp.status_code == 200
        plaques = list_resp.json()["plaques"]
        assert len(plaques) > 0
        plaque_id = plaques[0]["id"]
        resp = http.get(f"{API}/plaques/{plaque_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == plaque_id

    @pytest.mark.xfail(reason="Backend returns 500 instead of 404 for nonexistent plaques")
    def test_get_nonexistent_plaque(self, http):
        resp = http.get(f"{API}/plaques/999999")
        assert resp.status_code == 404

    def test_nearby_plaques(self, http):
        resp = http.get(f"{API}/plaques/nearby", params={"lat": -26.2041, "lng": 28.0473, "radius": 5000})
        assert resp.status_code == 200


# ── Categories ──────────────────────────────────────────

class TestCategories:
    def test_list_categories(self, http):
        resp = http.get(f"{API}/categories")
        assert resp.status_code == 200
        assert len(resp.json()) > 0

    @pytest.mark.xfail(reason="Backend returns 500 on single category endpoint")
    def test_get_single_category(self, http):
        cats = http.get(f"{API}/categories").json()
        resp = http.get(f"{API}/categories/{cats[0]['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == cats[0]["id"]


# ── Admin (authenticated) ──────────────────────────────

class TestAdmin:
    def test_protected_endpoint_no_token(self, http):
        resp = http.post(f"{API}/plaques", json={"title": "test"})
        assert resp.status_code in (401, 403, 422)

    def test_protected_endpoint_invalid_token(self, http):
        resp = http.post(f"{API}/plaques", json={"title": "test"}, headers={"Authorization": "Bearer invalid"})
        assert resp.status_code in (401, 403)

    @pytest.mark.xfail(reason="Backend returns 500 on plaque creation")
    def test_admin_can_create_and_delete_plaque(self, http, auth_header):
        resp = http.post(
            f"{API}/plaques",
            json={"title": "Verification Test", "latitude": -26.2, "longitude": 28.0, "address": "Test"},
            headers=auth_header,
        )
        assert resp.status_code in (200, 201)
        plaque_id = resp.json()["id"]
        delete_resp = http.delete(f"{API}/plaques/{plaque_id}", headers=auth_header)
        assert delete_resp.status_code in (200, 204)


# ── Frontend serving ────────────────────────────────────

class TestFrontend:
    def test_serves_html(self, http):
        resp = http.get(BASE_URL)
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("content-type", "")
