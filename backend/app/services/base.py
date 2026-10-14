from typing import Protocol

from app.schemas.ask import AskRequest, AskResponse
from app.schemas.complaints import (
    AnalyzeRequest,
    AnalyzeResponse,
    DraftRequest,
    DraftResponse,
)


class AskService(Protocol):
    async def ask(self, req: AskRequest) -> AskResponse: ...


class ComplaintService(Protocol):
    async def analyze(self, req: AnalyzeRequest) -> AnalyzeResponse: ...
    async def draft(self, req: DraftRequest) -> DraftResponse: ...