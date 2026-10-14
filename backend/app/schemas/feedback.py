from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import RequestModel


class FeedbackRequest(RequestModel):
    rating: Literal["up", "down"]
    request_id: str | None = Field(default=None, max_length=64)
    comment: str | None = Field(default=None, max_length=500)


class FeedbackResponse(BaseModel):
    ok: bool