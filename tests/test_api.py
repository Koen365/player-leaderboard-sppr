import json
import os
from pathlib import Path
import subprocess
import sys

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from api import create_app
from database import initialize_database, make_engine


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path / "test.db", seed_file=None)) as client:
        yield client


def add(client, username="Testspeler", score=0):
    response = client.post("/players", json={"username": username, "score": score})
    assert response.status_code == 201, response.text
    assert response.headers["location"] == f"/players/{response.json()['id']}"
    return response.json()


def test_player_crud_and_leaderboard(client):
    assert client.get("/").json()["status"] == "ok"
    assert client.get("/players").json() == []
    first = add(client, "  Alpha  ", 10)
    second = add(client, "Beta", 80)
    assert first["username"] == "Alpha"
    path = f"/players/{first['id']}"
    assert client.get(path).json() == first
    assert len(client.get("/players").json()) == 2
    assert [p["id"] for p in client.get("/leaderboard").json()] == [second["id"], first["id"]]
    changed = client.patch(path, json={"username": "Alpha2"})
    assert changed.status_code == 200
    assert changed.json()["score"] == 10
    changed = client.put(path, json={"username": "Alpha3", "score": 80})
    assert changed.status_code == 200
    assert changed.json() == {"id": first["id"], "username": "Alpha3", "score": 80}
    assert [p["id"] for p in client.get("/leaderboard").json()] == [first["id"], second["id"]]
    score_ids = [s["id"] for s in client.get(path + "/scores").json()]
    deleted = client.delete(path)
    assert deleted.status_code == 204 and deleted.content == b""
    assert client.get(path).status_code == 404
    for score_id in score_ids:
        assert client.get(f"/scores/{score_id}").status_code == 404
    # Een verwijderd id wordt niet opnieuw uitgegeven.
    assert add(client, "Gamma")["id"] > second["id"]


def test_scores_history_correction_and_delete(client):
    player = add(client, score=20)
    path = f"/players/{player['id']}"
    initial_score = client.get(path + "/scores").json()[0]
    added = client.post(path + "/scores", json={"score": 100})
    assert added.status_code == 201
    score_path = added.headers["location"]
    assert client.get(score_path).json() == added.json()
    assert added.json()["player_id"] == player["id"]
    assert client.get(path).json()["score"] == 100
    assert len(client.get("/scores").json()) == 2
    assert client.patch(score_path, json={"score": 5}).status_code == 200
    assert client.get(path).json()["score"] == 5
    removed = client.delete(score_path)
    assert removed.status_code == 204 and removed.content == b""
    assert client.get(path).json()["score"] == 20
    assert client.delete(f"/scores/{initial_score['id']}").status_code == 204
    assert client.get(path).json()["score"] == 0


@pytest.mark.parametrize("body", [
    {}, {"username": ""}, {"username": "   "}, {"username": "x" * 51},
    {"username": None}, {"username": 12}, {"username": "A", "id": 3},
    {"username": "A", "score": -1}, {"username": "A", "score": 1.5},
    {"username": "A", "score": True}, {"username": "A", "score": "100"},
    {"username": "A", "score": 2147483648}, {"username": "A", "score": None},
])
def test_invalid_player_input(client, body):
    assert client.post("/players", json=body).status_code == 422
    assert client.get("/players").json() == []


@pytest.mark.parametrize("body", [{"username": None}, {"score": None}, {"score": -2}, {"id": 9}])
def test_invalid_patch_does_not_change_data(client, body):
    player = add(client, score=40)
    path = f"/players/{player['id']}"
    assert client.patch(path, json=body).status_code == 422
    assert client.get(path).json() == player


def test_empty_patch_put_required_fields_and_duplicates(client):
    player = add(client, "Straße", 30)
    path = f"/players/{player['id']}"
    assert client.post("/players", json={"username": " STRASSE "}).status_code == 409
    other = add(client, "Other", 10)
    assert client.patch(f"/players/{other['id']}", json={"username": "straße", "score": 90}).status_code == 409
    assert client.get(f"/players/{other['id']}").json() == other
    assert len(client.get(f"/players/{other['id']}/scores").json()) == 1
    assert client.patch(path, json={}).status_code == 400
    assert client.put(path, json={"username": "Name"}).status_code == 422
    assert client.get(path).json() == player


@pytest.mark.parametrize("method,path,body", [
    ("get", "/players/999", None), ("delete", "/players/999", None),
    ("patch", "/players/999", {"score": 1}),
    ("put", "/players/999", {"username": "A", "score": 1}),
    ("get", "/players/999/scores", None), ("post", "/players/999/scores", {"score": 1}),
    ("get", "/scores/999", None), ("patch", "/scores/999", {"score": 1}),
    ("delete", "/scores/999", None),
])
def test_missing_resources(client, method, path, body):
    assert client.request(method, path, json=body).status_code == 404


@pytest.mark.parametrize("value", ["abc", "0", "-1", "99999999999999999999999999999999"])
def test_invalid_ids(client, value):
    assert client.get(f"/players/{value}").status_code == 422
    assert client.get(f"/scores/{value}").status_code == 422


@pytest.mark.parametrize("body", [{}, {"score": -1}, {"score": False}, {"score": "5"}, {"score": 0.5}, {"score": None}, {"score": 3, "player_id": 999}])
def test_invalid_score_input(client, body):
    player = add(client)
    assert client.post(f"/players/{player['id']}/scores", json=body).status_code == 422
    score_id = client.get("/scores").json()[0]["id"]
    assert client.patch(f"/scores/{score_id}", json=body).status_code == 422


def test_import_restart_and_no_resurrection(tmp_path):
    seed = tmp_path / "players.json"
    original = [{"id": 12, "username": "Existing", "score": 60}]
    seed.write_text(json.dumps(original), encoding="utf-8")
    db = tmp_path / "persistent.db"
    with TestClient(create_app(db, seed)) as client:
        assert client.get("/players").json() == original
        assert client.patch("/players/12", json={"score": 90}).status_code == 200
    # Nieuwe app en nieuwe verbindingen: de wijziging staat echt op schijf.
    with TestClient(create_app(db, seed)) as client:
        assert client.get("/players/12").json()["score"] == 90
        assert len(client.get("/players/12/scores").json()) == 2
        assert client.delete("/players/12").status_code == 204
    with TestClient(create_app(db, seed)) as client:
        assert client.get("/players").json() == []
        assert client.get("/scores").json() == []
    assert json.loads(seed.read_text(encoding="utf-8")) == original


def test_invalid_import_is_atomic_and_can_be_fixed(tmp_path):
    seed = tmp_path / "broken.json"
    seed.write_text('[{"id": 1, "username": "A", "score": 10}, {"id": 2, "username": "a", "score": 30}]')
    engine = make_engine(tmp_path / "test.db")
    try:
        with pytest.raises(ValueError, match="Dubbele"):
            initialize_database(engine, seed)
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT COUNT(*) FROM players")) == 0
            assert connection.scalar(text("SELECT COUNT(*) FROM app_metadata")) == 0
        seed.write_text('[{"id": 1, "username": "A", "score": 10}]')
        initialize_database(engine, seed)
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT COUNT(*) FROM players")) == 1
    finally:
        engine.dispose()


def test_database_enforces_foreign_keys_and_score_constraints(tmp_path):
    engine = make_engine(tmp_path / "test.db")
    try:
        initialize_database(engine, None)
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO players (id, username, username_key) VALUES (1, 'A', 'a')"))
        for player_id, score in [(999, 10), (1, -1), (1, 2.5)]:
            with pytest.raises(IntegrityError), engine.begin() as connection:
                connection.execute(text("INSERT INTO scores (player_id, score) VALUES (:id, :score)"), {"id": player_id, "score": score})
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO scores (player_id, score) VALUES (1, 10)"))
            connection.execute(text("DELETE FROM players WHERE id = 1"))
            assert connection.scalar(text("SELECT COUNT(*) FROM scores")) == 0
    finally:
        engine.dispose()


def test_console_from_other_directory_and_persistence(tmp_path):
    project = Path(__file__).resolve().parents[1]
    db = tmp_path / "console.db"
    env = dict(os.environ, PLAYER_DATABASE=str(db), PYTHONIOENCODING="utf-8")
    # Ongeldig menu, lege naam, geldig toevoegen, dubbel, zoeken, ongeldige score,
    # corrigeren, tonen en afsluiten. De console mag nergens crashen.
    commands = "x\n1\n   \n1\nConsoleTest\n1\nconsoletest\n3\nConsoleTest\n4\nConsoleTest\nabc\n-1\n77\n2\n5\n6\n"
    result = subprocess.run([sys.executable, str(project / "main.py")], input=commands,
                            text=True, capture_output=True, cwd=tmp_path, env=env, timeout=30, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    assert "Ongeldige keuze" in result.stdout
    assert "Deze username bestaat al" in result.stdout
    assert "Score aangepast naar 77" in result.stdout
    with TestClient(create_app(db, None)) as client:
        player = next(p for p in client.get("/players").json() if p["username"] == "ConsoleTest")
        assert player["score"] == 77


def test_swagger_and_openapi(client):
    assert client.get("/docs").status_code == 200
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    assert set(paths["/players/{player_id}"]) == {"get", "put", "patch", "delete"}
    assert set(paths["/players/{player_id}/scores"]) == {"get", "post"}
    assert "requestBody" in paths["/players"]["post"]
    assert "201" in paths["/players"]["post"]["responses"]
