from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import Channel, Language, RequestModel


class AnalyzeRequest(RequestModel):
    description: str = Field(min_length=1, max_length=2000)
    location: str | None = Field(default=None, max_length=300)
    language: Language | None = None


class ExtractedFields(BaseModel):
    description: str
    location: str | None = None


class FollowUpQuestion(BaseModel):
    field: Literal["description", "location"]
    question: str


class AnalyzeResponse(BaseModel):
    category_id: str | None
    category_name: str | None
    confidence: float
    extracted: ExtractedFields
    missing_fields: list[str]
    follow_up_questions: list[FollowUpQuestion]
    ready_to_draft: bool
    language: Language
    is_mock: bool


class DraftRequest(RequestModel):
    category_id: str = Field(min_length=1, max_length=64)
    description: str = Field(min_length=1, max_length=2000)
    location: str = Field(min_length=1, max_length=300)
    landmark: str | None = Field(default=None, max_length=200)
    language: Language | None = None


class Draft(BaseModel):
    title: str
    body: str
    fields: dict[str, str]


class DraftResponse(BaseModel):
    draft: Draft
    channel: Channel | None
    other_channels: list[Channel] = Field(default_factory=list)
    next_steps: list[str]
    disclaimer: str
    language: Language
    is_mock: bool = False