from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_classify_api_contract():
    response = client.post("/classify", json={"text": "hello"})
    assert response.status_code == 200
    data = response.json()
    assert "label" in data and "score" in data
    assert data["label"] in ("ham", "spam", "error")
    assert isinstance(data["score"], float)


def test_classify_spam_text():
    response = client.post("/classify", json={"text": "free prize click win money bonus"})
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "spam"


def test_model_info_endpoint():
    response = client.get("/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "model_version" in data
    assert data["model_version"] in ("keyword-v1", "ml-v2")
