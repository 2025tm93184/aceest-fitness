import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app as aceest


@pytest.fixture
def client():
    aceest.clients.clear()
    aceest.app.config["TESTING"] = True
    with aceest.app.test_client() as test_client:
        yield test_client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_home_reports_gym_capacity(client):
    gym = client.get("/").get_json()["gym"]
    assert gym["capacity"] == 150
    assert gym["area_sq_ft"] == 10000
    assert gym["break_even_members"] == 250


def test_programs_include_baseline_plans(client):
    names = {item["name"] for item in client.get("/programs").get_json()}
    assert names == {"Fat Loss (FL)", "Muscle Gain (MG)", "Beginner (BG)"}


def test_fat_loss_calories_match_baseline_factor():
    assert aceest.estimate_calories(70, "Fat Loss (FL)") == 1540
    assert aceest.estimate_calories(80, "Muscle Gain (MG)") == 2800
    assert aceest.estimate_calories(60, "Beginner (BG)") == 1560


def test_unknown_program_rejected(client):
    response = client.post("/calories", json={"weight": 70, "program": "Yoga"})
    assert response.status_code == 400


def test_client_requires_name_and_program(client):
    response = client.post("/clients", json={"weight": 70})
    assert response.status_code == 400


def test_create_client(client):
    response = client.post(
        "/clients",
        json={"name": "Ravi", "age": 28, "weight": 70, "program": "Fat Loss (FL)"},
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["calories"] == 1540
    listed = client.get("/clients").get_json()
    assert listed[0]["name"] == "Ravi"

