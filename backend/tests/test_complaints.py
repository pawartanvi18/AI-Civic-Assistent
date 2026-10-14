from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def analyze(client, **payload):
    return client.post("/api/v1/complaints/analyze", json=payload)


def draft(client, **payload):
    return client.post("/api/v1/complaints/draft", json=payload)


def test_analyze_missing_location(client):
    body = analyze(client, description="Big pothole near my house").json()
    assert body["category_id"] == "roads_potholes"
    assert body["missing_fields"] == ["location"]
    assert body["ready_to_draft"] is False
    assert body["follow_up_questions"][0]["field"] == "location"


def test_analyze_ready(client):
    body = analyze(client, description="Big pothole near my house", location="Andheri West").json()
    assert body["ready_to_draft"] is True


def test_analyze_marathi_follow_up(client):
    body = analyze(client, description="आमच्या रस्त्यावर मोठा खड्डा आहे", language="mr").json()
    assert body["category_id"] == "roads_potholes"
    assert "कुठे" in body["follow_up_questions"][0]["question"]
    assert body["language"] == "mr"


def test_analyze_ignores_non_complaint_topics(client):
    body = analyze(client, description="birth certificate", location="Dadar").json()
    assert body["category_id"] is None
    assert body["ready_to_draft"] is False


def test_draft_english(client):
    r = draft(
        client,
        category_id="drainage",
        description="Drain is blocked and overflowing",
        location="Bandra East",
        landmark="Near the station",
    )
    body = r.json()
    assert r.status_code == 200
    assert "Bandra East" in body["draft"]["body"]
    assert "not been submitted" in body["draft"]["body"]
    assert "MyBMC" in body["channel"]["name"]  # supports_complaints sorts first
    assert len(body["other_channels"]) >= 1
    assert len(body["next_steps"]) == 4
    assert "NOT an official service" in body["disclaimer"]


def test_draft_hindi(client):
    body = draft(
        client,
        category_id="streetlights",
        description="स्ट्रीटलाइट बंद है",
        location="Dadar",
        language="hi",
    ).json()
    assert "स्थान" in body["draft"]["body"]
    assert body["language"] == "hi"


def test_draft_unknown_category(client):
    r = draft(client, category_id="ghost", description="x", location="y")
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "unknown_category"


def test_draft_rejects_non_complaint_category(client):
    r = draft(client, category_id="birth_death_certificates", description="x", location="y")
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "unknown_category"


def test_draft_requires_location(client):
    r = draft(client, category_id="drainage", description="x")
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_strict_mode_draft_has_no_unverified_channel():
    app = create_app(Settings(_env_file=None, environment="test", allow_unverified_data=False))
    with TestClient(app, raise_server_exceptions=False) as c:
        body = draft(c, category_id="drainage", description="Blocked drain", location="Bandra").json()
        assert body["channel"] is None
        assert body["other_channels"] == []
        assert len(body["next_steps"]) == 4