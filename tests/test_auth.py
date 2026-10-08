import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select

from api import create_app
from conftest import PASSWORD, authenticate
from models import AccessSession, Player, User
from security import hash_token, verify_password


def test_register_login_me_logout_and_secure_storage(anonymous_client):
    client = anonymous_client
    account = authenticate(client, "  Koen  ")
    assert account == {"id": 1, "username": "Koen"}
    token = client.headers["Authorization"].split()[1]
    with client.app.state.session_factory() as session:
        user = session.get(User, account["id"])
        assert user.password_hash.startswith("$argon2id$")
        assert PASSWORD not in user.password_hash
        assert verify_password(PASSWORD, user.password_hash)
        stored = session.scalar(select(AccessSession))
        assert stored.token_hash == hash_token(token)
        assert stored.token_hash != token
        assert stored.expires_at > int(time.time())
    duplicate = client.post("/auth/register", json={"username": "KOEN", "password": PASSWORD})
    assert duplicate.status_code == 409
    assert client.post("/auth/logout").status_code == 204
    assert client.get("/auth/me").status_code == 401
    with client.app.state.session_factory() as session:
        assert session.scalar(select(AccessSession)) is None


@pytest.mark.parametrize("body", [
    {"username": "", "password": PASSWORD},
    {"username": "A", "password": "abc987"},
    {"username": "A", "password": "x" * 129},
    {"username": "A", "password": 12345678901},
    {"username": "A", "password": None},
    {"username": "A", "password": PASSWORD, "is_admin": True},
])
def test_invalid_registration_never_echoes_password(anonymous_client, body):
    response = anonymous_client.post("/auth/register", json=body)
    assert response.status_code == 422
    assert str(body["password"]) not in response.text
    assert all("input" not in error for error in response.json()["detail"])
    with anonymous_client.app.state.session_factory() as session:
        assert session.scalar(select(User)) is None


def test_wrong_login_and_token_errors(anonymous_client):
    client = anonymous_client
    authenticate(client)
    wrong = client.post("/auth/login", data={"username": "Tester", "password": "Wrong-password!"})
    missing = client.post("/auth/login", data={"username": "Nobody", "password": "Wrong-password!"})
    assert wrong.status_code == missing.status_code == 401
    assert wrong.json() == missing.json()
    for authorization in (None, "Bearer invalid", "Bearer " + "x" * 43, "Basic abc"):
        client.headers.pop("Authorization", None)
        if authorization:
            client.headers["Authorization"] = authorization
        response = client.get("/auth/me")
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"


def test_expired_token_and_account_deletion(client):
    token = client.headers["Authorization"].split()[1]
    with client.app.state.session_factory() as session:
        session.get(AccessSession, hash_token(token)).expires_at = int(time.time()) - 1
        session.commit()
    assert client.get("/auth/me").status_code == 401
    authenticate(client)
    with client.app.state.session_factory() as session:
        session.delete(session.scalar(select(User)))
        session.commit()
    assert client.get("/auth/me").status_code == 401


MUTATIONS = [
    ("post", "/players", {"username": "Unauthorized", "score": 0}),
    ("put", "/players/{player}", {"username": "Changed", "score": 100}),
    ("patch", "/players/{player}", {"score": 100}),
    ("delete", "/players/{player}", None),
    ("post", "/players/{player}/scores", {"score": 100}),
    ("patch", "/scores/{score}", {"score": 100}),
    ("delete", "/scores/{score}", None),
]


@pytest.mark.parametrize("method,path,body", MUTATIONS)
def test_every_mutation_requires_login(client, method, path, body):
    player = client.post("/players", json={"username": "Original", "score": 10}).json()
    score = client.get(f"/players/{player['id']}/scores").json()[0]
    client.headers.pop("Authorization")
    response = client.request(method, path.format(player=player["id"], score=score["id"]), json=body)
    assert response.status_code == 401
    assert client.get("/players").json() == [player]
    assert client.get("/scores").json() == [score]


@pytest.mark.parametrize("method,path,body", MUTATIONS[1:])
def test_every_existing_resource_mutation_requires_owner(client, method, path, body):
    owner = client.get("/auth/me").json()
    player = client.post("/players", json={"username": "Original", "score": 10}).json()
    score = client.get(f"/players/{player['id']}/scores").json()[0]
    authenticate(client, "OtherAccount")
    response = client.request(method, path.format(player=player["id"], score=score["id"]), json=body)
    assert response.status_code == 403
    assert client.get("/players").json() == [player]
    assert client.get("/scores").json() == [score]
    with client.app.state.session_factory() as session:
        assert session.get(Player, player["id"]).owner_id == owner["id"]


def test_owner_cannot_be_supplied_or_changed(client):
    owner = client.get("/auth/me").json()
    assert client.post("/players", json={"username": "A", "owner_id": 999}).status_code == 422
    player = client.post("/players", json={"username": "A"}).json()
    assert client.patch(f"/players/{player['id']}", json={"owner_id": 999}).status_code == 422
    with client.app.state.session_factory() as session:
        assert session.get(Player, player["id"]).owner_id == owner["id"]


def test_tokens_are_independent_and_persist_after_restart(tmp_path):
    db = tmp_path / "sessions.db"
    with TestClient(create_app(db, None)) as client:
        authenticate(client)
        first = client.headers["Authorization"]
        response = client.post("/auth/login", data={"username": "Tester", "password": PASSWORD})
        assert response.headers["cache-control"] == "no-store"
        assert response.json()["expires_in"] == 3600
        second = "Bearer " + response.json()["access_token"]
        assert first != second
        assert client.post("/auth/logout").status_code == 204
    with TestClient(create_app(db, None)) as client:
        assert client.get("/auth/me", headers={"Authorization": first}).status_code == 401
        assert client.get("/auth/me", headers={"Authorization": second}).status_code == 200


def test_existing_database_migration_and_local_ownership(tmp_path):
    project = Path(__file__).resolve().parents[1]
    db = tmp_path / "old.db"
    # Oude structuur uit sprint 4, zonder owner_id.
    with sqlite3.connect(db) as connection:
        connection.executescript("""
            CREATE TABLE players (id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(50) NOT NULL,
                                  username_key VARCHAR(100) NOT NULL UNIQUE);
            CREATE TABLE scores (id INTEGER PRIMARY KEY AUTOINCREMENT, player_id INTEGER NOT NULL
                                 REFERENCES players(id) ON DELETE CASCADE, score INTEGER NOT NULL);
            INSERT INTO players VALUES (12, 'Bestaand', 'bestaand');
            INSERT INTO scores VALUES (8, 12, 60);
        """)
    for _ in range(2):
        with TestClient(create_app(db, None)) as client:
            assert client.get("/players/12").json()["score"] == 60
    with TestClient(create_app(db, None)) as client:
        owner = authenticate(client)
        # De eerste registratie krijgt niet automatisch de oude spelers.
        assert client.patch("/players/12", json={"score": 80}).status_code == 403
        env = dict(os.environ, PLAYER_DATABASE=str(db), PYTHONIOENCODING="utf-8")
        result = subprocess.run([sys.executable, str(project / "assign_owner.py"),
                                 "--user", "Tester", "--all-unowned"],
                                capture_output=True, text=True, env=env, cwd=tmp_path, timeout=30)
        assert result.returncode == 0, result.stderr
        assert "1 speler(s) gekoppeld" in result.stdout
        assert client.patch("/players/12", json={"score": 80}).status_code == 200
        with client.app.state.session_factory() as session:
            assert session.get(Player, 12).owner_id == owner["id"]
        authenticate(client, "OtherAccount")
        takeover = subprocess.run([sys.executable, str(project / "assign_owner.py"),
                                   "--user", "OtherAccount", "--player-id", "12"],
                                  capture_output=True, text=True, env=env, cwd=tmp_path, timeout=30)
        assert takeover.returncode == 1
        assert "andere eigenaar" in takeover.stderr
        assert client.patch("/players/12", json={"score": 100}).status_code == 403
    with TestClient(create_app(db, None)) as client:
        authenticate(client)
        assert client.get("/players/12").json()["score"] == 80
        assert len(client.get("/players/12/scores").json()) == 2
        assert client.delete("/players/12").status_code == 204
        assert client.get("/scores").json() == []


def test_openapi_login_flow_and_public_reads(anonymous_client):
    client = anonymous_client
    schema = client.get("/openapi.json").json()
    scheme = schema["components"]["securitySchemes"]["OAuth2PasswordBearer"]
    assert scheme["flows"]["password"]["tokenUrl"] == "auth/login"
    paths = schema["paths"]
    assert paths["/players"]["post"]["security"]
    assert "security" not in paths["/players"]["get"]
    assert paths["/auth/me"]["get"]["security"]
    assert "application/x-www-form-urlencoded" in paths["/auth/login"]["post"]["requestBody"]["content"]
    assert "password_hash" not in str(schema["components"]["schemas"]["UserRead"])
    assert "password" not in str(schema["components"]["schemas"]["UserRead"])
    assert client.get("/leaderboard").status_code == 200
    assert client.get("/scores").status_code == 200
