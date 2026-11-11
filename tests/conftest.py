import os

# Test requests use a throwaway in-memory database and a test-only signing key.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET_KEY"] = "pytest-only-secret-key-not-for-real-use-123456"

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import Employee, User


@pytest.fixture
def client():
    """Provide an API client with a clean, isolated test database."""
    with TestClient(app) as test_client:
        with SessionLocal() as db:
            db.query(Employee).delete()
            db.query(User).delete()
            db.commit()

        yield test_client

        with SessionLocal() as db:
            db.query(Employee).delete()
            db.query(User).delete()
            db.commit()


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    """Register a test user and return its bearer-token authorization header."""
    response = client.post(
        "/auth/register",
        json={
            "username": "test-user",
            "email": "test@example.com",
            "password": "test-password-123",
        },
    )
    assert response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "test-password-123",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
