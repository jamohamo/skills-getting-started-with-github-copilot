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
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post("/activities/Soccer%20Team/signup?email=student@example.com")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": "Signed up student@example.com for Soccer Team"}
    assert client.get("/activities").json()["Soccer Team"]["participants"] == [email]


def test_duplicate_signup_returns_400(client):
    # Arrange
    email = "student@example.com"
    client.post(f"/activities/Soccer%20Team/signup?email={email}")

    # Act
    response = client.post(f"/activities/Soccer%20Team/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant(client):
    # Arrange
    email = "student@example.com"
    client.post(f"/activities/Soccer%20Team/signup?email={email}")

    # Act
    response = client.delete(f"/activities/Soccer%20Team/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Soccer Team"}
    assert client.get("/activities").json()["Soccer Team"]["participants"] == []


def test_missing_activity_returns_404_for_signup(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post("/activities/Unknown%20Club/signup?email=student@example.com")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_missing_participant_returns_404_for_unregister(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete(f"/activities/Soccer%20Team/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
