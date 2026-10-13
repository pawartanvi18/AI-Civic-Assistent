def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["independent_tool"] is True
    assert body["version"]


def test_meta_has_disclaimer(client):
    r = client.get("/api/v1/meta")
    assert r.status_code == 200
    assert "NOT an official service" in r.json()["disclaimer"]


def test_request_id_header(client):
    assert client.get("/health").headers.get("X-Request-ID")