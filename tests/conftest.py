from fastapi.testclient import TestClient
import pytest

from api import create_app

PASSWORD = "Testwachtwoord-2026!"


def authenticate(client, username="Tester"):
    response = client.post("/auth/register", json={"username": username, "password": PASSWORD})
    assert response.status_code in (201, 409), response.text
    login = client.post("/auth/login", data={"username": username, "password": PASSWORD})
    assert login.status_code == 200, login.text
    client.headers["Authorization"] = f"Bearer {login.json()['access_token']}"
    return client.get("/auth/me").json()


@pytest.fixture
def anonymous_client(tmp_path):
    with TestClient(create_app(tmp_path / "test.db", seed_file=None)) as client:
        yield client


@pytest.fixture
def client(anonymous_client):
    authenticate(anonymous_client)
    return anonymous_client
