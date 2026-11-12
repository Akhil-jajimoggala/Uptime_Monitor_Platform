import pytest
from fastapi.testclient import TestClient

from main import app, monitors

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_monitors():
    monitors.clear()


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_add_monitor():
    response = client.post("/monitors", json={"url": "https://github.com"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "url": "https://github.com"}


def test_list_monitors():
    client.post("/monitors", json={"url": "https://github.com"})
    response = client.get("/monitors")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_add_monitor_rejects_bad_input():
    response = client.post("/monitors", json={"wrong_field": "x"})
    assert response.status_code == 422