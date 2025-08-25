import pytest
from fastapi.testclient import TestClient
from main import app
from database import Database
import base64

client = TestClient(app)

# Тестовые данные
TEST_DATA = {
    "user": {
        "email": "test@example.com",
        "fam": "Тестов",
        "name": "Тест",
        "otc": "Тестович",
        "phone": "+79990001122"
    },
    "coords": {
        "latitude": 45.0000,
        "longitude": 90.0000,
        "height": 1000
    },
    "beauty_title": "пер. тест",
    "title": "Тестовый перевал",
    "levels": {
        "winter": "1A",
        "summer": "1A",
        "autumn": "1B",
        "spring": "1A"
    },
    "images": [
        {
            "title": "Тестовое изображение",
            "data": base64.b64encode(b"test_image_data").decode('utf-8')
        }
    ]
}


def test_database_connection():
    with Database() as db:
        assert db.conn is not None
        assert not db.conn.closed


def test_full_workflow():
    # Тест добавления данных
    response = client.post("/submitData/", json=TEST_DATA)
    assert response.status_code == 201
    pereval_id = response.json()["pereval_id"]

    # Тест получения данных
    response = client.get(f"/submitData/{pereval_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == TEST_DATA["title"]
    assert data["status"] == "new"

    # Тест поиска по email
    response = client.get("/submitData/", params={"user__email": TEST_DATA["user"]["email"]})
    assert response.status_code == 200
    assert len(response.json()) > 0

    # Тест обновления данных
    update_data = {
        "title": "Обновленное название",
        "levels": {
            "winter": "2A",
            "summer": "1B",
            "autumn": "1B",
            "spring": "2A"
        }
    }
    response = client.patch(f"/submitData/{pereval_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["state"] == 1

    # Проверка обновленных данных
    response = client.get(f"/submitData/{pereval_id}")
    assert response.json()["title"] == "Обновленное название"
    assert response.json()["levels"]["winter"] == "2A"