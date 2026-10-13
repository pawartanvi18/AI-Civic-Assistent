import posixpath
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.domain._yaml import read_yaml_mapping
from app.errors import ConfigurationError


class SourceRule(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    name: str
    host: str  # bare hostname, e.g. "portal.example.gov.in"
    path_prefixes: list[str] = Field(default_factory=lambda: ["/"])
    topics: list[str] = Field(default_factory=lambda: ["*"])
    languages: list[str] = Field(default_factory=lambda: ["en"])
    include_subdomains: bool = False
    verified: bool = False  # flip to true only after you manually verify the source
    notes: str = ""

    @field_validator("host")
    @classmethod
    def _host_ok(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.fullmatch(r"[a-z0-9]([a-z0-9.-]*[a-z0-9])?", v):
            raise ValueError("host must be a bare hostname (no scheme, path or port)")
        return v

    @field_validator("path_prefixes")
    @classmethod
    def _prefixes_ok(cls, v: list[str]) -> list[str]:
        if not v or any(not p.startswith("/") for p in v):
            raise ValueError("path_prefixes must be non-empty and start with '/'")
        return v

    def covers_topic(self, topic_id: str) -> bool:
        return "*" in self.topics or topic_id in self.topics


def _normalise_path(raw: str) -> str:
    path = posixpath.normpath(re.sub(r"/+", "/", unquote(raw or "/")))
    return path if path.startswith("/") else "/" + path


def _path_matches(path: str, prefix: str) -> bool:
    prefix = _normalise_path(prefix)
    if prefix == "/":
        return True
    return path == prefix or path.startswith(prefix + "/")


class SourceAllowList:
    """Trust boundary: only URLs matching a rule may be used as evidence."""

    def __init__(self, rules: list[SourceRule]):
        ids = [r.id for r in rules]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise ConfigurationError(f"Duplicate source ids: {sorted(dupes)}")
        self._rules = list(rules)

    @staticmethod
    def _parse(url: str) -> tuple[str, str] | None:
        if not isinstance(url, str) or not url or len(url) > 2048:
            return None
        if any(ch.isspace() or ord(ch) < 32 for ch in url):
            return None
        try:
            parts = urlsplit(url)
            port = parts.port
        except ValueError:
            return None
        if parts.scheme != "https":
            return None
        if parts.username is not None or parts.password is not None:
            return None
        if port not in (None, 443):
            return None
        host = (parts.hostname or "").rstrip(".")
        if not host:
            return None
        return host, _normalise_path(parts.path)

    def match(self, url: str, topic_id: str | None = None) -> SourceRule | None:
        parsed = self._parse(url)
        if parsed is None:
            return None
        host, path = parsed
        for rule in self._rules:
            if topic_id is not None and not rule.covers_topic(topic_id):
                continue
            host_ok = host == rule.host or (
                rule.include_subdomains and host.endswith("." + rule.host)
            )
            if host_ok and any(_path_matches(path, p) for p in rule.path_prefixes):
                return rule
        return None

    def is_allowed(self, url: str, topic_id: str | None = None) -> bool:
        return self.match(url, topic_id) is not None

    def rules_for_topic(self, topic_id: str) -> list[SourceRule]:
        return [r for r in self._rules if r.covers_topic(topic_id)]

    def all_rules(self) -> list[SourceRule]:
        return list(self._rules)


def load_sources(path: Path, valid_topic_ids: set[str]) -> SourceAllowList:
    data = read_yaml_mapping(path)
    raw = data.get("sources")
    if not isinstance(raw, list) or not raw:
        raise ConfigurationError(f"{path}: 'sources' must be a non-empty list.")
    rules = []
    for i, item in enumerate(raw):
        try:
            rule = SourceRule.model_validate(item)
        except ValidationError as e:
            raise ConfigurationError(f"{path}: invalid source #{i + 1}: {e}") from e
        unknown = [t for t in rule.topics if t != "*" and t not in valid_topic_ids]
        if unknown:
            raise ConfigurationError(
                f"{path}: source '{rule.id}' references unknown topics {unknown}"
            )
        rules.append(rule)
    return SourceAllowList(rules)