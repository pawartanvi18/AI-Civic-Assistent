from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(tags=["topics"])


class TopicOut(BaseModel):
    id: str
    name: str
    description: str
    example_questions: list[str]


class TopicsResponse(BaseModel):
    topics: list[TopicOut]


@router.get("/topics", response_model=TopicsResponse)
def list_topics(request: Request) -> TopicsResponse:
    registry = request.app.state.topics
    return TopicsResponse(
        topics=[
            TopicOut(
                id=t.id,
                name=t.name,
                description=t.description,
                example_questions=t.example_questions,
            )
            for t in registry.all()
        ]
    )