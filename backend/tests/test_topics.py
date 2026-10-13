import pytest

from app.domain.topics import load_topics
from app.errors import ConfigurationError


def test_real_topics_load(client):
    r = client.get("/api/v1/topics")
    assert r.status_code == 200
    ids = {t["id"] for t in r.json()["topics"]}
    assert {"solid_waste", "roads_potholes", "drainage"} <= ids


def test_malformed_yaml_fails(tmp_path):
    f = tmp_path / "t.yaml"
    f.write_text("topics: [unclosed", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_topics(f)


def test_duplicate_ids_fail(tmp_path):
    f = tmp_path / "t.yaml"
    f.write_text(
        "topics:\n"
        "  - {id: a, name: A, description: d, keywords: [k]}\n"
        "  - {id: a, name: B, description: d, keywords: [k]}\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError):
        load_topics(f)


def test_missing_field_fails(tmp_path):
    f = tmp_path / "t.yaml"
    f.write_text("topics:\n  - {id: a, name: A}\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_topics(f)


def test_missing_file_fails(tmp_path):
    with pytest.raises(ConfigurationError):
        load_topics(tmp_path / "missing.yaml")