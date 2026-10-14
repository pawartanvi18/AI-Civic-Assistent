from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(tags=["system"])


class MetaResponse(BaseModel):
    app_name: str
    version: str
    disclaimer: str
    supported_languages: list[str]


@router.get("/meta", response_model=MetaResponse)
def meta(request: Request) -> MetaResponse:
    s = request.app.state.settings
    return MetaResponse(
        app_name=s.app_name,
        version=s.app_version,
        disclaimer=s.disclaimer,
        supported_languages=["en", "mr", "hi"],
    )