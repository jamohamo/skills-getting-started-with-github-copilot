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


def test_signup_for_multiple_activities_adds_participant_to_each(client):
    email = "student@example.com"
    activity_names = ["Soccer Team", "Chess Club"]

    response = client.post(
        "/activities/signup",
        json={"email": email, "activity_names": activity_names},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Soccer Team, Chess Club"
    }
    activities_response = client.get("/activities").json()
    assert activities_response["Soccer Team"]["participants"] == [email]
    assert activities_response["Chess Club"]["participants"] == [email]
    assert client.get("/activities").headers["cache-control"] == "no-store"


def test_signup_for_multiple_activities_is_atomic_when_one_is_unknown(client):
    email = "student@example.com"

    response = client.post(
        "/activities/signup",
        json={
            "email": email,
            "activity_names": ["Soccer Team", "Unknown Club"],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found: Unknown Club"
    assert client.get("/activities").json()["Soccer Team"]["participants"] == []


def test_signup_for_multiple_activities_is_atomic_when_already_signed_up(client):
    email = "student@example.com"
    activities["Chess Club"]["participants"].append(email)

    response = client.post(
        "/activities/signup",
        json={"email": email, "activity_names": ["Soccer Team", "Chess Club"]},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for: Chess Club"
    assert client.get("/activities").json()["Soccer Team"]["participants"] == []


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
