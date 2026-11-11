from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database import SessionLocal
from app.models import User

NEW_USER = {
    "username": "alex",
    "email": "alex@example.com",
    "password": "a-secure-password",
}


def test_user_registration(client: TestClient) -> None:
    response = client.post("/auth/register", json=NEW_USER)

    assert response.status_code == 201
    assert response.json()["username"] == NEW_USER["username"]
    assert response.json()["email"] == NEW_USER["email"]
    assert "password" not in response.json()
    assert "hashed_password" not in response.json()

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == NEW_USER["email"]))
        assert user is not None
        assert user.hashed_password != NEW_USER["password"]
        assert user.hashed_password.startswith("$argon2")


def test_duplicate_user_registration_returns_conflict(client: TestClient) -> None:
    assert client.post("/auth/register", json=NEW_USER).status_code == 201

    duplicate = {**NEW_USER, "username": "different-name"}
    response = client.post("/auth/register", json=duplicate)

    assert response.status_code == 409
    assert response.json()["detail"] == "An account with this email already exists"


def test_user_login_returns_bearer_token(client: TestClient) -> None:
    client.post("/auth/register", json=NEW_USER)

    response = client.post(
        "/auth/login",
        json={"email": NEW_USER["email"], "password": NEW_USER["password"]},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_invalid_login_credentials_are_rejected(client: TestClient) -> None:
    client.post("/auth/register", json=NEW_USER)

    response = client.post(
        "/auth/login",
        json={"email": NEW_USER["email"], "password": "incorrect-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
