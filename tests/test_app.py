import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original_participants = {
        activity_name: list(details["participants"])
        for activity_name, details in activities.items()
    }

    yield

    for activity_name, details in activities.items():
        details["participants"] = list(original_participants[activity_name])


@pytest.fixture
def client():
    return TestClient(app)


def test_signup_for_activity_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    activities[activity_name]["participants"] = ["michael@mergington.edu"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"


def test_signup_for_activity_rejects_duplicate(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    activities[activity_name]["participants"] = [email, "daniel@mergington.edu"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_email_from_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email = "student@example.edu"
    activities[activity_name]["participants"] = ["michael@mergington.edu", email]

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"


def test_unregister_raises_for_unknown_activity(client):
    # Act
    response = client.delete("/activities/DoesNotExist/unregister?email=student@example.edu")

    # Assert
    assert response.status_code == 404
