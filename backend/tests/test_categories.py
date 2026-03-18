from unittest.mock import patch
from fastapi.testclient import TestClient
from tests.conftest import make_mock_supabase, MockQueryBuilder, SAMPLE_CATEGORY


def test_list_categories():
    mock_sb = make_mock_supabase(
        table_responses={
            "categories": MockQueryBuilder(data=[SAMPLE_CATEGORY]),
            "plaque_categories": MockQueryBuilder(data=[{"category_id": 1}, {"category_id": 1}]),
        }
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.categories.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/v1/categories")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["name"] == "People"
        assert data[0]["plaque_count"] == 2


def test_list_categories_empty():
    mock_sb = make_mock_supabase(
        table_responses={
            "categories": MockQueryBuilder(data=[]),
            "plaque_categories": MockQueryBuilder(data=[]),
        }
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.categories.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/v1/categories")
        assert resp.status_code == 200
        assert resp.json() == []


def test_get_category():
    mock_sb = make_mock_supabase(
        table_responses={
            "categories": MockQueryBuilder(data=[SAMPLE_CATEGORY]),
            "plaque_categories": MockQueryBuilder(data=[], count=5),
        }
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.categories.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/v1/categories/1")
        assert resp.status_code == 200
        assert resp.json()["name"] == "People"
        assert resp.json()["plaque_count"] == 5


def test_get_category_not_found():
    mock_sb = make_mock_supabase(
        table_responses={"categories": MockQueryBuilder(data=[])}
    )
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.categories.supabase", mock_sb):
        from app.main import app
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/v1/categories/999")
        assert resp.status_code == 404
