from pathlib import Path
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from app.domain._yaml import read_yaml_mapping
from app.domain.sources import SourceAllowList
from app.errors import ConfigurationError


class ContactChannel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    name: str
    type: Literal["phone", "whatsapp", "web", "app", "email"]
    contact: str | None = None
    url: str | None = None
    languages: list[str] = Field(default_factory=lambda: ["en"])
    topics: list[str] = Field(default_factory=lambda: ["*"])
    supports_complaints: bool | None = None
    source: str = ""
    verified: bool = False
    notes: str = ""

    @field_validator("url")
    @classmethod
    def _https_only(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith("https://"):
            raise ValueError("url must start with https://")
        return v

    @model_validator(mode="after")
    def _has_target(self):
        if not (self.contact or self.url):
            raise ValueError("a channel needs a contact or a url")
        return self


class ChannelCatalog:
    def __init__(self, channels: list[ContactChannel]):
        ids = [c.id for c in channels]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise ConfigurationError(f"Duplicate channel ids: {sorted(dupes)}")
        self._channels = list(channels)

    def all(self) -> list[ContactChannel]:
        return list(self._channels)

    def for_topic(self, topic_id: str) -> list[ContactChannel]:
        return [c for c in self._channels if "*" in c.topics or topic_id in c.topics]


def load_channels(
    path: Path, topic_ids: set[str], allow_list: SourceAllowList
) -> ChannelCatalog:
    data = read_yaml_mapping(path)
    raw = data.get("channels")
    if not isinstance(raw, list) or not raw:
        raise ConfigurationError(f"{path}: 'channels' must be a non-empty list.")
    channels = []
    for i, item in enumerate(raw):
        try:
            ch = ContactChannel.model_validate(item)
        except ValidationError as e:
            raise ConfigurationError(f"{path}: invalid channel #{i + 1}: {e}") from e
        unknown = [t for t in ch.topics if t != "*" and t not in topic_ids]
        if unknown:
            raise ConfigurationError(f"{path}: channel '{ch.id}' has unknown topics {unknown}")
        if ch.url and not allow_list.is_allowed(ch.url):
            raise ConfigurationError(f"{path}: channel '{ch.id}' url is not allowed by sources.yaml")
        channels.append(ch)
    return ChannelCatalog(channels)