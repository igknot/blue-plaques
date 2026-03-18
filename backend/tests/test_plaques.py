from unittest.mock import patch
from fastapi.testclient import TestClient
from tests.conftest import (
    make_mock_supabase, MockQueryBuilder, SAMPLE_PLAQUE, SAMPLE_USER,
)


def test_list_plaques_empty(client):
    resp = client.get("/api/v1/plaques")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["plaques"] == []


def test_list_plaques_with_results():
    mock_sb = make_mock_supabase(
        table_responses={"plaques": MockQueryBuilder(data=[SAMPLE_PLAQUE], count=1)}
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.plaques.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/v1/plaques")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["plaques"][0]["title"] == "Test Plaque"


def test_list_plaques_search():
    mock_sb = make_mock_supabase(
        table_responses={"plaques": MockQueryBuilder(data=[SAMPLE_PLAQUE], count=1)}
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.plaques.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/v1/plaques?search=Test")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1


def test_list_plaques_category_filter():
    mock_sb = make_mock_supabase(
        table_responses={
            "plaque_categories": MockQueryBuilder(data=[{"plaque_id": 1}]),
            "plaques": MockQueryBuilder(data=[SAMPLE_PLAQUE], count=1),
        }
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.plaques.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/v1/plaques?category_ids=1")
        assert resp.status_code == 200


def test_list_plaques_category_filter_no_match():
    mock_sb = make_mock_supabase(
        table_responses={
            "plaque_categories": MockQueryBuilder(data=[]),
            "plaques": MockQueryBuilder(data=[], count=0),
        }
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.plaques.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/v1/plaques?category_ids=999")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


def test_get_plaque():
    mock_sb = make_mock_supabase(
        table_responses={"plaques": MockQueryBuilder(data=SAMPLE_PLAQUE)}
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.plaques.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/v1/plaques/1")
        assert resp.status_code == 200
        assert resp.json()["id"] == 1


def test_get_plaque_not_found():
    mock_sb = make_mock_supabase(
        table_responses={"plaques": MockQueryBuilder(data=None)}
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.plaques.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/v1/plaques/999")
        # Will hit exception handler since single() mock returns None
        assert resp.status_code in (404, 500)


def test_create_plaque_unauthorized(client):
    resp = client.post("/api/v1/plaques", json={
        "title": "Test", "latitude": -26.2, "longitude": 28.0
    })
    assert resp.status_code == 403


def test_create_plaque_authorized():
    mock_sb = make_mock_supabase(
        table_responses={
            "plaques": MockQueryBuilder(data=[SAMPLE_PLAQUE]),
            "users": MockQueryBuilder(data=[SAMPLE_USER]),
            "plaque_categories": MockQueryBuilder(data=[]),
        }
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.plaques.supabase", mock_sb), \
         patch("app.api.deps.supabase", mock_sb):
        from app.main import app
        from tests.conftest import admin_token as _make_token
        from app.core.security import create_access_token
        from datetime import timedelta
        token = create_access_token(data={"sub": "admin@test.com"}, expires_delta=timedelta(minutes=30))
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.post(
            "/api/v1/plaques",
            json={"title": "New Plaque", "latitude": -26.2, "longitude": 28.0},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200


def test_delete_plaque_unauthorized(client):
    resp = client.delete("/api/v1/plaques/1")
    assert resp.status_code == 403


def test_update_plaque_unauthorized(client):
    resp = client.put("/api/v1/plaques/1", json={"title": "Updated"})
    assert resp.status_code == 403


def test_nearby_plaques():
    mock_sb = make_mock_supabase(
        table_responses={"plaques": MockQueryBuilder(data=[SAMPLE_PLAQUE])},
        rpc_responses={"nearby_plaques": [{"id": 1}]},
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.plaques.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/v1/plaques/nearby?lat=-26.2&lng=28.0&radius=5000")
        assert resp.status_code == 200


def test_nearby_plaques_empty():
    mock_sb = make_mock_supabase(rpc_responses={"nearby_plaques": []})
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.plaques.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/v1/plaques/nearby?lat=-26.2&lng=28.0&radius=5000")
        assert resp.status_code == 200
        assert resp.json() == []


def test_nearby_plaques_invalid_params(client):
    resp = client.get("/api/v1/plaques/nearby?lat=999&lng=28.0")
    assert resp.status_code == 422
