from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

Language = Literal["en", "mr", "hi"]


class RequestModel(BaseModel):
    """Base for all inputs: trims whitespace, rejects unknown fields."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Source(BaseModel):
    title: str
    url: str
    retrieved_at: datetime | None = None  # None = catalog entry never checked
    verified: bool = False


class Channel(BaseModel):
    name: str
    url: str | None = None
    instructions: str
    verified: bool = False


class ServiceInfo(BaseModel):
    id: str
    name: str
    authority: str
    jurisdiction: Literal["bmc", "maharashtra"]
    official_url: str
    verified: bool