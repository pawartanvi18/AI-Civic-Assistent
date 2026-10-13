from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(tags=["system"])


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    independent_tool: bool


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    s = request.app.state.settings
    return HealthResponse(
        status="ok",
        version=s.app_version,
        environment=s.environment,
        independent_tool=True,
    )