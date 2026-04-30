from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

ORIGINAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert expected_activity in body
    assert isinstance(body[expected_activity]["participants"], list)
    assert body[expected_activity]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_adds_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "teststudent@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(url, params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities_response = client.get("/activities").json()
    assert email in activities_response[activity_name]["participants"]


def test_duplicate_signup_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(url, params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_participant_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    participant_email = "daniel@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/participants"

    # Act
    response = client.delete(url, params={"email": participant_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {participant_email} from {activity_name}"

    activities_response = client.get("/activities").json()
    assert participant_email not in activities_response[activity_name]["participants"]


def test_delete_missing_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    missing_email = "ghost@mergington.edu"
    url = f"/activities/{quote(activity_name, safe='')}/participants"

    # Act
    response = client.delete(url, params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
