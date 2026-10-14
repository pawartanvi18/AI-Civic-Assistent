from fastapi import APIRouter

from app.schemas.feedback import FeedbackRequest, FeedbackResponse

router = APIRouter(tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse, status_code=202)
async def feedback(body: FeedbackRequest) -> FeedbackResponse:
    # Mock: accepted but intentionally not stored or logged (comments may
    # contain personal data). Real persistence comes with the database milestone.
    return FeedbackResponse(ok=True)