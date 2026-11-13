import pytest
from fastapi.testclient import TestClient

from main import app
from db import get_connection

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_database():
    with get_connection() as conn:
        conn.execute("TRUNCATE monitors RESTART IDENTITY CASCADE")
@pytest.mark.parametrize(
    "raw",
    ["google.com", "www.google.com", "https:www.google.com", "https://www.google.com/"],
)
def test_add_monitor_accepts_common_url_formats(raw):
    response = client.post("/monitors", json={"url": raw})
    assert response.status_code == 200
    assert response.json()["url"].startswith("https://")
    assert not response.json()["url"].endswith("/")


def test_add_monitor_rejects_invalid_address():
    response = client.post("/monitors", json={"url": "not a url"})
    assert response.status_code == 422

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

def test_delete_monitor():
    created = client.post("/monitors", json={"url": "https://github.com"}).json()
    response = client.delete(f"/monitors/{created['id']}")
    assert response.status_code == 204
    assert client.get("/monitors").json() == []


def test_delete_missing_monitor():
    response = client.delete("/monitors/999")
    assert response.status_code == 404

def test_add_monitor_rejects_bad_input():
    response = client.post("/monitors", json={"wrong_field": "x"})
    assert response.status_code == 422