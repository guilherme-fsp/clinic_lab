from fastapi.testclient import TestClient

from scheduling_api.app import app


client = TestClient(app)


def test_health_check():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }


def test_create_appointment():

    payload = {
        "exams": [
            {
                "name": "Hemograma Completo",
                "code": "LAB001",
            }
        ]
    }

    response = client.post(
        "/appointments",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "requested"

    assert data["exams"] == payload["exams"]

    assert data["appointment_id"].startswith(
        "APT-"
    )

def test_create_appointment_rejects_empty_exams():

    response = client.post(
        "/appointments",
        json={
            "exams": []
        },
    )

    assert response.status_code == 422