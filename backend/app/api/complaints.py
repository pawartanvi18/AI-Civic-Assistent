from fastapi import APIRouter, Request

from app.schemas.complaints import (
    AnalyzeRequest,
    AnalyzeResponse,
    DraftRequest,
    DraftResponse,
)

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(body: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    return await request.app.state.complaint_service.analyze(body)


@router.post("/draft", response_model=DraftResponse)
async def draft(body: DraftRequest, request: Request) -> DraftResponse:
    return await request.app.state.complaint_service.draft(body)