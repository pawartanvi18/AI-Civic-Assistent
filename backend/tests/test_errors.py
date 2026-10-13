def test_404_uses_standard_body(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_validation_error_does_not_echo_input(app):
    from fastapi.testclient import TestClient

    @app.get("/needs-int")
    def needs_int(n: int):
        return {"n": n}

    with TestClient(app, raise_server_exceptions=False) as c:
        r = c.get("/needs-int", params={"n": "secret-value"})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"
    assert "secret-value" not in r.text


def test_unhandled_error_hides_traceback(app):
    from fastapi.testclient import TestClient

    @app.get("/boom")
    def boom():
        raise RuntimeError("internal detail")

    with TestClient(app, raise_server_exceptions=False) as c:
        r = c.get("/boom")
    assert r.status_code == 500
    assert r.json()["error"]["code"] == "internal_error"
    assert "internal detail" not in r.text
    assert "Traceback" not in r.text