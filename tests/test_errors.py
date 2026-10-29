import json

from fastapi.testclient import TestClient
import pytest
from sqlalchemy.exc import OperationalError

from api import create_app
from conftest import authenticate
import service


@pytest.fixture
def fault_client(tmp_path):
    with TestClient(
        create_app(tmp_path / "errors.db", None), raise_server_exceptions=False
    ) as client:
        authenticate(client)
        yield client


def test_null_character_in_name_returns_422(fault_client):
    response = fault_client.post("/players", json={"username": "\x00Alice"})
    assert response.status_code == 422
    assert fault_client.get("/players").json() == []
    assert fault_client.post("/players", json={"username": "Alice"}).status_code == 201


def test_invalid_unicode_password_returns_422(fault_client):
    body = json.dumps({"username": "NewAccount", "password": "Wachtwoord\ud8002026"})
    response = fault_client.post(
        "/auth/register", content=body, headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
    assert "Wachtwoord" not in response.text
    assert fault_client.get("/auth/me").status_code == 200


def test_repeated_put_does_not_duplicate_score_history(client):
    player = client.post("/players", json={"username": "Alice", "score": 10}).json()
    path = f"/players/{player['id']}"
    body = {"username": "Alice", "score": 20}
    first = client.put(path, json=body)
    second = client.put(path, json=body)
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert [s["score"] for s in client.get(path + "/scores").json()] == [10, 20]
    # Een expliciete nieuwe score mag wel opnieuw dezelfde waarde hebben.
    assert client.post(path + "/scores", json={"score": 20}).status_code == 201
    assert [s["score"] for s in client.get(path + "/scores").json()] == [10, 20, 20]


@pytest.mark.parametrize(
    "method,path,body",
    [
        ("post", "/players", []),
        ("post", "/players", "geen object"),
        ("post", "/players", None),
        ("post", "/players", {"username": "A\nB"}),
        ("post", "/players", {"username": "A\x7fB"}),
        (
            "post",
            "/auth/register",
            {"username": "A\x00B", "password": "Testwachtwoord-2026!"},
        ),
    ],
)
def test_unexpected_input_is_rejected_without_crashing(client, method, path, body):
    response = client.request(method, path, json=body)
    assert response.status_code == 422
    assert all(
        set(error) == {"loc", "msg", "type"} for error in response.json()["detail"]
    )
    assert client.get("/").json()["status"] == "ok"
    assert client.get("/players").json() == []


@pytest.mark.parametrize("path", ["/players", "/auth/register"])
def test_malformed_json(client, path):
    response = client.post(
        path, content='{"username":', headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["type"] == "json_invalid"
    assert client.get("/players").json() == []


def test_unknown_route_and_wrong_method(client):
    assert client.get("/does-not-exist").status_code == 404
    response = client.delete("/leaderboard")
    assert response.status_code == 405
    assert "GET" in response.headers["allow"]
    assert isinstance(response.json()["detail"], str)


def test_database_failure_rolls_back_and_next_request_works(
    fault_client, monkeypatch, caplog
):
    def broken_commit(session):
        raise OperationalError(
            "SECRET_SQL", {"password": "SECRET_INPUT"}, Exception("database locked")
        )

    with monkeypatch.context() as patch:
        patch.setattr(service, "commit_player", broken_commit)
        response = fault_client.post("/players", json={"username": "RetryPlayer"})
    assert response.status_code == 503
    assert response.headers["retry-after"] == "1"
    assert response.json() == {
        "detail": "Database tijdelijk niet beschikbaar. Probeer later opnieuw."
    }
    assert "SECRET" not in response.text + caplog.text
    assert fault_client.get("/players").json() == []
    assert (
        fault_client.post("/players", json={"username": "RetryPlayer"}).status_code
        == 201
    )


def test_unexpected_error_has_safe_json_and_does_not_stop_api(
    fault_client, monkeypatch, caplog
):
    def broken_list(*args, **kwargs):
        raise RuntimeError("SECRET_PATH_AND_PASSWORD")

    with monkeypatch.context() as patch:
        patch.setattr(service, "list_players", broken_list)
        response = fault_client.get("/players")
    assert response.status_code == 500
    assert response.json() == {"detail": "Er ging iets mis op de server."}
    assert "SECRET" not in response.text + caplog.text
    assert fault_client.get("/players").status_code == 200


def test_unicode_and_sql_like_text_remain_valid(client):
    name = "Zoë'); DROP TABLE players; --"
    response = client.post("/players", json={"username": name, "score": 0})
    assert response.status_code == 201
    assert client.get("/players").json() == [response.json()]


def test_repeated_zero_put_after_last_score_deleted(client):
    player = client.post("/players", json={"username": "Zero"}).json()
    path = f"/players/{player['id']}"
    score = client.get(path + "/scores").json()[0]
    assert client.delete(f"/scores/{score['id']}").status_code == 204
    for _ in range(2):
        assert (
            client.put(path, json={"username": "Zero", "score": 0}).status_code == 200
        )
    assert len(client.get(path + "/scores").json()) == 1
