import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def ask(client, question, language=None):
    body = {"question": question}
    if language:
        body["language"] = language
    return client.post("/api/v1/ask", json=body)


@pytest.mark.parametrize(
    "question,language,service_id",
    [
        ("Where can I get a birth certificate?", None, "birth_death_certificate"),
        ("जन्म प्रमाणपत्र कुठे मिळेल?", "mr", "birth_death_certificate"),
        ("जाति प्रमाणपत्र कहाँ बनवाएँ?", "hi", "revenue_certificates"),
        ("mala janm dakhla kuthe milel", "mr", "birth_death_certificate"),
        ("How do I get a new water connection?", None, "water_connection_bills"),
        ("How do I get a trade license?", None, "trade_license"),
    ],
)
def test_service_questions(client, question, language, service_id):
    r = ask(client, question, language)
    body = r.json()
    assert r.status_code == 200
    assert body["status"] == "answered"
    assert body["intent"] == "information"
    assert body["services"][0]["id"] == service_id
    assert body["services"][0]["official_url"].startswith("https://")
    assert body["steps"]
    assert body["language"] == (language or "en")
    assert body["is_mock"] is False


def test_state_service_marked(client):
    body = ask(client, "Where do I apply for a caste certificate?").json()
    assert body["services"][0]["jurisdiction"] == "maharashtra"
    assert "Maharashtra" in body["answer"]
    assert body["official_channel"] is None  # BMC helpline is not relevant


def test_unverified_data_is_labelled(client):
    body = ask(client, "Where can I get a birth certificate?").json()
    assert body["services"][0]["verified"] is False
    assert "not been checked" in body["answer"]


@pytest.mark.parametrize(
    "question",
    ["There is a big pothole near my house", "How do I report a pothole?"],
)
def test_complaint_intent(client, question):
    body = ask(client, question).json()
    assert body["intent"] == "complaint"
    assert body["topic_id"] == "roads_potholes"


def test_known_topic_without_catalog_answer_is_insufficient(client):
    body = ask(client, "What is the segregation rule for garbage?").json()
    assert body["status"] == "insufficient_evidence"
    assert body["topic_id"] == "solid_waste"
    assert body["services"] == []


def test_unsupported(client):
    body = ask(client, "What is the capital of France?").json()
    assert body["status"] == "unsupported_topic"
    assert body["intent"] == "unsupported"


def test_strict_mode_hides_unverified_entries():
    app = create_app(Settings(_env_file=None, environment="test", allow_unverified_data=False))
    with TestClient(app, raise_server_exceptions=False) as c:
        body = ask(c, "Where can I get a birth certificate?").json()
        assert body["status"] == "insufficient_evidence"
        assert body["services"] == []
        assert body["official_channel"] is None


def test_disclaimer_is_localised(client):
    body = ask(client, "जन्म प्रमाणपत्र", "mr").json()
    assert "स्वतंत्र" in body["disclaimer"]


def test_empty_question_rejected(client):
    r = client.post("/api/v1/ask", json={"question": "   "})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_unknown_field_rejected(client):
    r = client.post("/api/v1/ask", json={"question": "pothole", "extra": 1})
    assert r.status_code == 422