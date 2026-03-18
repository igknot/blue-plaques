import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.core.security import create_access_token, get_password_hash
from datetime import timedelta


class MockResponse:
    """Mock Supabase API response."""
    def __init__(self, data=None, count=None):
        self.data = data or []
        self.count = count if count is not None else 0


class MockQueryBuilder:
    """Mock Supabase query builder that supports chaining."""
    def __init__(self, data=None, count=None):
        self._data = data or []
        self._count = count
        self._single = False

    def single(self):
        self._single = True
        return self

    def execute(self):
        data = self._data
        if self._single and isinstance(data, list):
            data = data[0] if data else None
        return MockResponse(data, self._count)

    def __getattr__(self, name):
        """Any other chained method returns self."""
        return lambda *args, **kwargs: self


def make_mock_supabase(table_responses=None, rpc_responses=None):
    """Create a mock supabase client with configurable responses.

    Args:
        table_responses: dict mapping table_name to MockQueryBuilder or response data
        rpc_responses: dict mapping rpc_name to response data
    """
    mock = MagicMock()
    table_responses = table_responses or {}
    rpc_responses = rpc_responses or {}

    def table_side_effect(name):
        if name in table_responses:
            val = table_responses[name]
            if isinstance(val, MockQueryBuilder):
                return val
            return MockQueryBuilder(data=val)
        return MockQueryBuilder()

    def rpc_side_effect(name, params=None):
        if name in rpc_responses:
            return MockQueryBuilder(data=rpc_responses[name])
        return MockQueryBuilder()

    mock.table.side_effect = table_side_effect
    mock.rpc.side_effect = rpc_side_effect
    return mock


SAMPLE_PLAQUE = {
    "id": 1,
    "title": "Test Plaque",
    "description": "A test plaque",
    "inscription": None,
    "latitude": -26.2041,
    "longitude": 28.0473,
    "address": "Johannesburg",
    "year_erected": 2000,
    "organization": None,
    "source_url": None,
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00",
    "images": [],
    "categories": [],
}

SAMPLE_CATEGORY = {
    "id": 1,
    "name": "People",
    "slug": "people",
    "description": "Notable individuals",
}

SAMPLE_USER = {
    "id": 1,
    "email": "admin@test.com",
    "hashed_password": get_password_hash("testpass123"),
    "is_active": 1,
    "is_admin": 1,
}


@pytest.fixture
def admin_token():
    return create_access_token(
        data={"sub": "admin@test.com"},
        expires_delta=timedelta(minutes=30),
    )


@pytest.fixture
def auth_header(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def client():
    """TestClient with supabase mocked to return empty by default."""
    mock_sb = make_mock_supabase()
    with patch("app.database.supabase", mock_sb), \
         patch("app.api.v1.plaques.supabase", mock_sb), \
         patch("app.api.v1.categories.supabase", mock_sb), \
         patch("app.api.v1.auth.supabase", mock_sb), \
         patch("app.api.v1.images.supabase", mock_sb), \
         patch("app.api.deps.supabase", mock_sb):
        from app.main import app
        yield TestClient(app, raise_server_exceptions=False)
