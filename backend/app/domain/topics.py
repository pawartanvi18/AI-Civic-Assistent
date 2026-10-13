from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.domain._yaml import read_yaml_mapping
from app.errors import ConfigurationError


class Topic(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    keywords: list[str] = Field(min_length=1)
    example_questions: list[str] = Field(default_factory=list)


class TopicRegistry:
    def __init__(self, topics: list[Topic]):
        ids = [t.id for t in topics]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            raise ConfigurationError(f"Duplicate topic ids: {sorted(dupes)}")
        self._topics = {t.id: t for t in topics}

    def get(self, topic_id: str) -> Topic | None:
        return self._topics.get(topic_id)

    def all(self) -> list[Topic]:
        return list(self._topics.values())

    def ids(self) -> set[str]:
        return set(self._topics)


def load_topics(path: Path) -> TopicRegistry:
    data = read_yaml_mapping(path)
    raw = data.get("topics")
    if not isinstance(raw, list) or not raw:
        raise ConfigurationError(f"{path}: 'topics' must be a non-empty list.")
    topics = []
    for i, item in enumerate(raw):
        try:
            topics.append(Topic.model_validate(item))
        except ValidationError as e:
            raise ConfigurationError(f"{path}: invalid topic #{i + 1}: {e}") from e
    return TopicRegistry(topics)