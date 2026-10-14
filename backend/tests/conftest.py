import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

SOURCES_YAML = """\
sources:
  - id: bmc_portal
    name: BMC portal (test fixture)
    host: portal.mcgm.gov.in
    path_prefixes: ["/"]
    topics: ["*"]
"""

SERVICES_YAML = """\
services:
  - id: birth_death_certificate
    topic: birth_death_certificates
    name: Birth and death certificate
    authority: Public Health Department (BMC)
    jurisdiction: bmc
    official_url: "https://portal.mcgm.gov.in/test-page"
    source_id: bmc_portal
    keywords: [birth, death, born]
    verified: {flag}
"""

CHANNELS_YAML = """\
channels:
  - id: mybmc_whatsapp
    name: MyBMC Assist (WhatsApp chatbot)
    type: whatsapp
    contact: "+91 00000 00000"
    topics: ["*"]
    supports_complaints: true
    verified: {flag}
  - id: bmc_helpline
    name: BMC helpline (test)
    type: phone
    contact: "0000"
    topics: ["*"]
    verified: {flag}
"""


@pytest.fixture
def app():
    return create_app(Settings(_env_file=None, environment="test"))


@pytest.fixture
def client(app):
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture
def make_app(tmp_path):
    """Build an app with fixture sources/services/channels, so tests do not
    depend on which real entries you have verified."""

    def _make(*, verified: bool, allow_unverified: bool):
        flag = "true" if verified else "false"
        (tmp_path / "sources.yaml").write_text(SOURCES_YAML, encoding="utf-8")
        (tmp_path / "services.yaml").write_text(
            SERVICES_YAML.format(flag=flag), encoding="utf-8"
        )
        (tmp_path / "channels.yaml").write_text(
            CHANNELS_YAML.format(flag=flag), encoding="utf-8"
        )
        return create_app(
            Settings(
                _env_file=None,
                environment="test",
                sources_file=tmp_path / "sources.yaml",
                services_file=tmp_path / "services.yaml",
                channels_file=tmp_path / "channels.yaml",
                allow_unverified_data=allow_unverified,
            )
        )

    return _make