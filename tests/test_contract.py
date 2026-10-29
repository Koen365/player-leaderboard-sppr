import json
from pathlib import Path

from jsonschema import Draft202012Validator


# Dit is het publieke contract: methode, pad, succescode en loginplicht.
OPERATIONS = [
    ("get", "/", 200, False),
    ("post", "/auth/register", 201, False),
    ("post", "/auth/login", 200, False),
    ("get", "/auth/me", 200, True),
    ("post", "/auth/logout", 204, True),
    ("get", "/players", 200, False),
    ("post", "/players", 201, True),
    ("get", "/players/{player_id}", 200, False),
    ("put", "/players/{player_id}", 200, True),
    ("patch", "/players/{player_id}", 200, True),
    ("delete", "/players/{player_id}", 204, True),
    ("get", "/players/{player_id}/scores", 200, False),
    ("post", "/players/{player_id}/scores", 201, True),
    ("get", "/scores", 200, False),
    ("get", "/scores/{score_id}", 200, False),
    ("patch", "/scores/{score_id}", 200, True),
    ("delete", "/scores/{score_id}", 204, True),
    ("get", "/leaderboard", 200, False),
]


def test_exported_contract_matches_live_api(anonymous_client):
    contract = json.loads((Path(__file__).resolve().parents[1] / "openapi.json").read_text(encoding="utf-8"))
    assert contract == anonymous_client.get("/openapi.json").json()
    assert sum(len(methods) for methods in contract["paths"].values()) == len(OPERATIONS)
    for method, path, status, protected in OPERATIONS:
        operation = contract["paths"][path][method]
        assert str(status) in operation["responses"]
        assert bool(operation.get("security")) == protected
        assert operation["summary"]
        if status == 204:
            assert "content" not in operation["responses"]["204"]
        if protected:
            assert operation["responses"]["401"]["content"]["application/json"]["schema"]
        elif method == "get":
            assert "401" not in operation["responses"]
    invalid = contract["components"]["schemas"]["ValidationIssue"]["properties"]
    assert set(invalid) == {"loc", "msg", "type"}


def test_documented_examples_and_full_student_flow(anonymous_client):
    client = anonymous_client
    contract = client.get("/openapi.json").json()

    def example(name):
        return contract["components"]["schemas"][name]["examples"][0].copy()

    def request(method, template, expected, *, path=None, **kwargs):
        response = client.request(method, path or template, **kwargs)
        assert response.status_code == expected, response.text
        documented = contract["paths"][template][method]["responses"][str(expected)]
        if expected == 204:
            assert response.content == b""
        else:
            schema = {"components": contract["components"], **documented["content"]["application/json"]["schema"]}
            Draft202012Validator(schema).validate(response.json())
        return response

    request("get", "/", 200)
    account = example("UserCreate")
    request("post", "/auth/register", 201, json=account)
    request("post", "/auth/register", 409, json=account)
    request("post", "/auth/login", 401, data={**account, "password": "fout-wachtwoord"})
    request("post", "/auth/login", 422, data={"username": account["username"]})
    request("get", "/auth/me", 401)
    login = request("post", "/auth/login", 200, data=account)
    client.headers["Authorization"] = "Bearer " + login.json()["access_token"]
    request("get", "/auth/me", 200)
    request("get", "/players", 200)
    body = example("PlayerCreate")
    created = request("post", "/players", 201, json=body)
    path = created.headers["Location"]
    assert path == f"/players/{created.json()['id']}"
    request("get", "/players/{player_id}", 200, path=path)
    request("post", "/players", 409, json=body)
    request("patch", "/players/{player_id}", 200, path=path, json=example("PlayerPatch"))
    request("put", "/players/{player_id}", 200, path=path, json=example("PlayerReplace"))
    request("patch", "/players/{player_id}", 400, path=path, json={})
    request("patch", "/players/{player_id}", 422, path=path, json={"score": -1})
    score = request("post", "/players/{player_id}/scores", 201, path=path + "/scores", json=example("ScoreCreate"))
    score_path = score.headers["Location"]
    request("get", "/players/{player_id}/scores", 200, path=path + "/scores")
    request("get", "/scores", 200)
    request("get", "/scores/{score_id}", 200, path=score_path)
    request("patch", "/scores/{score_id}", 200, path=score_path, json={"score": 250})
    request("get", "/leaderboard", 200)

    other = {**account, "username": "AndereGebruiker"}
    request("post", "/auth/register", 201, json=other)
    other_token = request("post", "/auth/login", 200, data=other).json()["access_token"]
    request("patch", "/players/{player_id}", 403, path=path, json={"score": 900},
            headers={"Authorization": "Bearer " + other_token})
    request("delete", "/scores/{score_id}", 204, path=score_path)
    request("get", "/scores/{score_id}", 404, path=score_path)
    request("delete", "/players/{player_id}", 204, path=path)
    request("get", "/players/{player_id}", 404, path=path)
    request("post", "/auth/logout", 204)
    request("get", "/auth/me", 401)
