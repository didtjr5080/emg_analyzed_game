import pytest

from app import app, game


@pytest.fixture()
def client():
    game.reset()
    app.config.update(TESTING=True)
    return app.test_client()


def test_page_and_static_assets(client):
    assert client.get("/").status_code == 200
    assert client.get("/static/css/style.css").status_code == 200
    assert client.get("/static/js/game.js").status_code == 200
    assert client.get("/static/images/arm-wrestling-arena.png").status_code == 200


def test_emg_endpoint_clamps_and_calculates(client):
    response = client.post("/api/emg", json={"biceps": 1.5, "triceps": .2})
    assert response.status_code == 200
    data = response.get_json()
    assert data["biceps"] == 1.0
    assert data["overall_activation"] == .6
    assert data["balance"] == .8


def test_invalid_input_and_reset(client):
    assert client.post("/api/emg", json={"biceps": "bad"}).status_code == 400
    client.post("/api/control", json={"action": "start"})
    client.post("/api/score")
    assert client.post("/api/reset").get_json()["score"] == 0
