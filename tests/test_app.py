import pytest
from app import app, estimate_calories


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_programs_include_baseline_plans(client):
    names = {item["name"] for item in client.get("/programs").get_json()}
    assert names == {"Fat Loss (FL)", "Muscle Gain (MG)", "Beginner (BG)"}


def test_fat_loss_calories_match_baseline_factor():
    assert estimate_calories(70, "Fat Loss (FL)") == 1540
    assert estimate_calories(80, "Muscle Gain (MG)") == 2800
    assert estimate_calories(60, "Beginner (BG)") == 1560


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
    assert response.get_json()["calories"] == 1540
