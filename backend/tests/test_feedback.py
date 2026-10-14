def test_feedback_accepted(client):
    r = client.post("/api/v1/feedback", json={"rating": "up"})
    assert r.status_code == 202
    assert r.json() == {"ok": True}


def test_feedback_invalid_rating(client):
    r = client.post("/api/v1/feedback", json={"rating": "maybe"})
    assert r.status_code == 422