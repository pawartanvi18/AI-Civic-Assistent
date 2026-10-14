from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.domain._yaml import read_yaml_mapping
from app.domain.sources import SourceAllowList
from app.errors import ConfigurationError


class Service(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    topic: str
    name: str
    names: dict[str, str] = Field(default_factory=dict)
    authority: str
    jurisdiction: Literal["bmc", "maharashtra"]
    official_url: str
    source_id: str
    keywords: list[str] = Field(default_factory=list)
    verified: bool = False
    checked_on: date | None = None
    notes: str = ""

    @field_validator("official_url")
    @classmethod
    def _https_only(cls, v: str) -> str:
        if not v.startswith("https://"):
            raise ValueError("official_url must start with https://")
        return v

    def display_name(self, lang: str) -> str:
        return self.names.get(lang) or self.name


class ServiceCatalog:
    def __init__(self, services: list[Service]):
        ids = [s.id for s in services]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise ConfigurationError(f"Duplicate service ids: {sorted(dupes)}")
        self._services = list(services)

    def all(self) -> list[Service]:
        return list(self._services)

    def get(self, service_id: str) -> Service | None:
        return next((s for s in self._services if s.id == service_id), None)

    def for_topic(self, topic_id: str) -> list[Service]:
        return [s for s in self._services if s.topic == topic_id]


def load_services(
    path: Path, topic_ids: set[str], allow_list: SourceAllowList
) -> ServiceCatalog:
    data = read_yaml_mapping(path)
    raw = data.get("services")
    if not isinstance(raw, list) or not raw:
        raise ConfigurationError(f"{path}: 'services' must be a non-empty list.")
    source_ids = {r.id for r in allow_list.all_rules()}
    services = []
    for i, item in enumerate(raw):
        try:
            svc = Service.model_validate(item)
        except ValidationError as e:
            raise ConfigurationError(f"{path}: invalid service #{i + 1}: {e}") from e
        if svc.topic not in topic_ids:
            raise ConfigurationError(f"{path}: service '{svc.id}' has unknown topic '{svc.topic}'")
        if svc.source_id not in source_ids:
            raise ConfigurationError(f"{path}: service '{svc.id}' has unknown source_id '{svc.source_id}'")
        # The trust boundary applies to the catalog too.
        if not allow_list.is_allowed(svc.official_url, svc.topic):
            raise ConfigurationError(
                f"{path}: service '{svc.id}' official_url is not allowed by sources.yaml"
            )
        services.append(svc)
    return ServiceCatalog(services)