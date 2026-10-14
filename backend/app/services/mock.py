import re
from datetime import datetime, timezone

from app.domain.topics import Topic, TopicRegistry
from app.errors import AppError
from app.schemas.ask import AskRequest, AskResponse
from app.schemas.common import Channel, Source
from app.schemas.complaints import (
    AnalyzeRequest,
    AnalyzeResponse,
    Draft,
    DraftRequest,
    DraftResponse,
    ExtractedFields,
    FollowUpQuestion,
)

_UNVERIFIABLE = re.compile(r"\b(fee|fees|cost|charges?|deadline|penalty)\b", re.I)

PLACEHOLDER_CHANNEL = Channel(
    name="Official BMC complaint channel (placeholder, not yet verified)",
    url=None,
    instructions=(
        "Real channel names, links and contact details will be added after the "
        "official sources are verified."
    ),
)


def match_topic(registry: TopicRegistry, text: str) -> tuple[Topic | None, int]:
    """Keyword match (word-prefix). Returns best topic and number of hits."""
    low = text.lower()
    best, best_hits = None, 0
    for topic in registry.all():
        hits = sum(
            1 for k in topic.keywords if re.search(r"\b" + re.escape(k.lower()), low)
        )
        if hits > best_hits:
            best, best_hits = topic, hits
    return best, best_hits


class MockAskService:
    def __init__(self, registry: TopicRegistry, disclaimer: str):
        self._registry = registry
        self._disclaimer = disclaimer

    async def ask(self, req: AskRequest) -> AskResponse:
        topic, _ = match_topic(self._registry, req.question)
        base = dict(language="en", disclaimer=self._disclaimer, is_mock=True)

        if topic is None:
            return AskResponse(
                status="unsupported_topic",
                answer="[MOCK] This topic is not supported yet.",
                topic_id=None,
                sources=[],
                official_channel=None,
                **base,
            )
        if _UNVERIFIABLE.search(req.question):
            return AskResponse(
                status="insufficient_evidence",
                answer=(
                    "[MOCK] I could not verify this from the official sources I "
                    "can access. Please check the official BMC channel."
                ),
                topic_id=topic.id,
                sources=[],
                official_channel=PLACEHOLDER_CHANNEL,
                **base,
            )
        return AskResponse(
            status="answered",
            answer=f"[MOCK] Sample answer about: {topic.name}. Not real guidance.",
            topic_id=topic.id,
            sources=[
                Source(
                    title="Mock source (not a real page)",
                    url="https://example.org/mock-source",
                    retrieved_at=datetime.now(timezone.utc),
                )
            ],
            official_channel=PLACEHOLDER_CHANNEL,
            **base,
        )


class MockComplaintService:
    def __init__(self, registry: TopicRegistry, disclaimer: str):
        self._registry = registry
        self._disclaimer = disclaimer

    async def analyze(self, req: AnalyzeRequest) -> AnalyzeResponse:
        topic, hits = match_topic(self._registry, req.description)
        location = req.location or None
        missing: list[str] = []
        questions: list[FollowUpQuestion] = []

        if topic is None:
            missing.append("description")
            questions.append(
                FollowUpQuestion(
                    field="description",
                    question=(
                        "Could you describe the problem in a bit more detail? "
                        "For example: garbage, pothole, blocked drain, water "
                        "supply or streetlight."
                    ),
                )
            )
        if location is None:
            missing.append("location")
            questions.append(
                FollowUpQuestion(
                    field="location",
                    question=(
                        "Where is the problem? Please give the area, street or "
                        "nearest landmark."
                    ),
                )
            )

        return AnalyzeResponse(
            category_id=topic.id if topic else None,
            category_name=topic.name if topic else None,
            confidence=min(0.5 + 0.1 * hits, 0.9) if topic else 0.0,
            extracted=ExtractedFields(description=req.description, location=location),
            missing_fields=missing,
            follow_up_questions=questions,
            ready_to_draft=not missing,
            language="en",
            is_mock=True,
        )

    async def draft(self, req: DraftRequest) -> DraftResponse:
        topic = self._registry.get(req.category_id)
        if topic is None:
            raise AppError("unknown_category", "Unknown complaint category.", 422)

        title = f"Complaint regarding {topic.name} at {req.location}"
        lines = [
            "To the concerned Ward Office / Department,",
            "",
            f"I would like to report the following issue: {req.description}",
            f"Location: {req.location}",
        ]
        if req.landmark:
            lines.append(f"Nearby landmark: {req.landmark}")
        lines += [
            "",
            "I request that this be looked into and appropriate action taken.",
            "",
            "[MOCK] This text was prepared with an independent tool and has "
            "not been submitted anywhere.",
        ]
        fields = {"category": topic.name, "location": req.location}
        if req.landmark:
            fields["landmark"] = req.landmark

        return DraftResponse(
            draft=Draft(title=title, body="\n".join(lines), fields=fields),
            channel=PLACEHOLDER_CHANNEL,
            disclaimer=self._disclaimer,
            language="en",
            is_mock=True,
        )