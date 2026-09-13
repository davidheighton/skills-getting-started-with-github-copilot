import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient

from app import app, activities

client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "student@example.edu"

    activities[activity_name]["participants"] = ["michael@mergington.edu", email]

    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"


def test_unregister_raises_for_unknown_activity():
    response = client.delete("/activities/DoesNotExist/unregister?email=student@example.edu")

    assert response.status_code == 404
