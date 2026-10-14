from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import Channel, Language, RequestModel, ServiceInfo, Source

AskStatus = Literal["answered", "insufficient_evidence", "unsupported_topic"]
AskIntent = Literal["information", "complaint", "unsupported"]


class AskRequest(RequestModel):
    question: str = Field(min_length=1, max_length=1000)
    language: Language | None = None


class AskResponse(BaseModel):
    status: AskStatus
    intent: AskIntent
    answer: str | None
    topic_id: str | None
    language: Language
    sources: list[Source]
    services: list[ServiceInfo] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    official_channel: Channel | None = None
    disclaimer: str
    is_mock: bool = False