import pytest

from app.domain.channel_catalog import load_channels
from app.domain.service_catalog import load_services
from app.errors import ConfigurationError


def test_real_catalogs_load(app):
    services = app.state.service_catalog.all()
    assert len(services) >= 8
    assert all(s.keywords for s in services)
    assert app.state.channels.all()


def test_service_outside_allow_list_fails(tmp_path, app):
    f = tmp_path / "s.yaml"
    f.write_text(
        "services:\n  - {id: x, topic: drainage, name: X, authority: A, jurisdiction: bmc,"
        " official_url: 'https://evil.net/x', source_id: bmc_portal}\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError):
        load_services(f, app.state.topics.ids(), app.state.allow_list)


def test_service_unknown_topic_fails(tmp_path, app):
    f = tmp_path / "s.yaml"
    f.write_text(
        "services:\n  - {id: x, topic: ghost, name: X, authority: A, jurisdiction: bmc,"
        " official_url: 'https://portal.mcgm.gov.in/', source_id: bmc_portal}\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError):
        load_services(f, app.state.topics.ids(), app.state.allow_list)


def test_channel_needs_contact_or_url(tmp_path, app):
    f = tmp_path / "c.yaml"
    f.write_text("channels:\n  - {id: a, name: A, type: phone}\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_channels(f, app.state.topics.ids(), app.state.allow_list)


def test_topics_endpoint_localised(client):
    en = {t["id"]: t for t in client.get("/api/v1/topics").json()["topics"]}
    mr = {t["id"]: t for t in client.get("/api/v1/topics?lang=mr").json()["topics"]}
    assert mr["roads_potholes"]["name"] != en["roads_potholes"]["name"]
    assert en["roads_potholes"]["complaint_enabled"] is True
    assert en["birth_death_certificates"]["complaint_enabled"] is False