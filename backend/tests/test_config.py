import pytest
from pydantic import ValidationError

from app.config import Settings


def test_invalid_environment_fails(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "staging")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_cors_origins_parsed(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://a.test, http://b.test ,")
    s = Settings(_env_file=None)
    assert s.cors_origin_list == ["http://a.test", "http://b.test"]