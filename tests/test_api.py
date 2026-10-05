from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original = deepcopy(activities)
    for activity in activities.values():
        activity["participants"] = []
    yield
    activities.clear()
    activities.update(deepcopy(original))


@pytest.fixture
def client():
    return TestClient(app)


def test_signup_for_activity_adds_participant(client):
    response = client.post("/activities/Soccer%20Team/signup?email=student@example.com")

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up student@example.com for Soccer Team"}
    assert client.get("/activities").json()["Soccer Team"]["participants"] == ["student@example.com"]


def test_duplicate_signup_returns_400(client):
    client.post("/activities/Soccer%20Team/signup?email=student@example.com")

    response = client.post("/activities/Soccer%20Team/signup?email=student@example.com")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant(client):
    client.post("/activities/Soccer%20Team/signup?email=student@example.com")

    response = client.delete("/activities/Soccer%20Team/unregister?email=student@example.com")

    assert response.status_code == 200
    assert response.json() == {"message": "Removed student@example.com from Soccer Team"}
    assert client.get("/activities").json()["Soccer Team"]["participants"] == []


def test_missing_activity_returns_404_for_signup(client):
    response = client.post("/activities/Unknown%20Club/signup?email=student@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_missing_participant_returns_404_for_unregister(client):
    response = client.delete("/activities/Soccer%20Team/unregister?email=student@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
