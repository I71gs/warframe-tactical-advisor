from __future__ import annotations
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_api_profile_endpoint() -> None:
    response = client.get("/profile")
    assert response.status_code == 200
    data = response.json()
    assert "mastery_rank" in data
    assert "owned_weapons" in data

def test_api_recommendations_endpoint() -> None:
    response = client.get("/recommendations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_api_progression_endpoint() -> None:
    response = client.get("/progression")
    assert response.status_code == 200
    data = response.json()
    assert "stage" in data
    assert "readiness_score" in data

def test_api_builds_endpoint() -> None:
    response = client.get("/builds")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_api_search_endpoint() -> None:
    response = client.get("/search?q=Phenmor")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_api_resources_endpoint() -> None:
    response = client.get("/resources")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_api_advisor_endpoint() -> None:
    response = client.get("/advisor?q=Phenmor")
    assert response.status_code == 200
    data = response.json()
    assert "task" in data

def test_api_sim_endpoint() -> None:
    response = client.get("/sim")
    assert response.status_code == 200
    data = response.json()
    assert "current_readiness" in data
    assert "projections" in data
