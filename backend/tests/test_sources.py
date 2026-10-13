import pytest

from app.domain.sources import SourceAllowList, SourceRule, load_sources
from app.errors import ConfigurationError

ALLOW = SourceAllowList(
    [
        SourceRule(id="main", name="Main", host="civic.example.gov.in"),
        SourceRule(
            id="docs",
            name="Docs",
            host="docs.example.gov.in",
            path_prefixes=["/public"],
            topics=["drainage"],
        ),
    ]
)


@pytest.mark.parametrize(
    "url",
    [
        "https://civic.example.gov.in/",
        "https://civic.example.gov.in/page?x=1",
        "https://CIVIC.example.gov.in/page",
        "https://civic.example.gov.in:443/page",
        "https://civic.example.gov.in./page",
        "https://docs.example.gov.in/public/a.pdf",
    ],
)
def test_allowed(url):
    assert ALLOW.is_allowed(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://civic.example.gov.in/",  # not https
        "https://civic.example.gov.in.evil.net/",  # look-alike suffix
        "https://evil.net/civic.example.gov.in",  # host in path
        "https://civic.example.gov.in@evil.net/",  # userinfo trick
        "https://evil.net@civic.example.gov.in/",  # userinfo (rejected conservatively)
        "https://civic.example.gov.in:8443/",  # odd port
        "https://xcivic.example.gov.in/",  # prefix look-alike
        "https://sub.civic.example.gov.in/",  # subdomains not included
        "https://docs.example.gov.in/publicity",  # path segment boundary
        "https://docs.example.gov.in/public/../private/x",  # traversal
        "https://docs.example.gov.in/%2e%2e/private",  # encoded traversal
        "javascript:alert(1)",
        "ftp://civic.example.gov.in/",
        "not a url",
        "",
    ],
)
def test_denied(url):
    assert not ALLOW.is_allowed(url)


def test_topic_scoping():
    url = "https://docs.example.gov.in/public/a"
    assert ALLOW.is_allowed(url, topic_id="drainage")
    assert not ALLOW.is_allowed(url, topic_id="streetlights")


def test_subdomains_only_when_enabled():
    al = SourceAllowList(
        [SourceRule(id="x", name="X", host="example.gov.in", include_subdomains=True)]
    )
    assert al.is_allowed("https://a.example.gov.in/")
    assert al.is_allowed("https://example.gov.in/")
    assert not al.is_allowed("https://notexample.gov.in/")


def test_unknown_topic_in_yaml_fails(tmp_path):
    f = tmp_path / "s.yaml"
    f.write_text(
        "sources:\n  - {id: a, name: A, host: x.gov.in, topics: [ghost]}\n",
        encoding="utf-8",
    )
    with pytest.raises(ConfigurationError):
        load_sources(f, {"drainage"})


def test_real_sources_load(app):
    assert app.state.allow_list.all_rules()