import copy
import urllib.parse

import pytest
from importlib import import_module
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def reset_activities():
    """Backup and restore the in-memory activities between tests."""
    app_mod = import_module("src.app")
    backup = copy.deepcopy(app_mod.activities)
    yield
    # restore
    app_mod.activities.clear()
    app_mod.activities.update(backup)


def test_get_activities_returns_dict():
    app_mod = import_module("src.app")
    client = TestClient(app_mod.app)

    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # ensure a known activity exists
    assert "Chess Club" in data


def test_signup_adds_participant_and_reflects_in_activities():
    app_mod = import_module("src.app")
    client = TestClient(app_mod.app)

    activity = "Basketball Team"
    email = "tester+signup@example.com"

    # sign up
    resp = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # fetch activities and verify participant present
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email in participants


def test_remove_participant_endpoint_removes_user():
    app_mod = import_module("src.app")
    client = TestClient(app_mod.app)

    activity = "Tennis Club"
    email = "tester+remove@example.com"

    # ensure user is signed up first
    resp = client.post(f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}")
    assert resp.status_code == 200

    # now remove
    resp = client.delete(f"/activities/{urllib.parse.quote(activity)}/participants?email={urllib.parse.quote(email)}")
    assert resp.status_code == 200
    assert "Removed" in resp.json().get("message", "")

    # verify gone
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email not in participants
