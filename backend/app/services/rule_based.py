from datetime import datetime, time, timezone

from app.domain.channel_catalog import ChannelCatalog, ContactChannel
from app.domain.matching import best_topic, count_hits, has_complaint_signal
from app.domain.service_catalog import Service, ServiceCatalog
from app.domain.topics import TopicRegistry
from app.errors import AppError
from app.messages import normalize_lang, t
from app.schemas.ask import AskRequest, AskResponse
from app.schemas.common import Channel, ServiceInfo, Source
from app.schemas.complaints import (
    AnalyzeRequest,
    AnalyzeResponse,
    Draft,
    DraftRequest,
    DraftResponse,
    ExtractedFields,
    FollowUpQuestion,
)

MAX_SERVICES = 3


def to_channel(ch: ContactChannel, lang: str) -> Channel:
    if ch.type == "phone" and ch.contact:
        instructions = t(lang, "ch_phone", contact=ch.contact)
    elif ch.type == "whatsapp" and ch.contact:
        instructions = t(lang, "ch_whatsapp", contact=ch.contact)
    elif ch.url:
        instructions = t(lang, "ch_web", url=ch.url)
    else:
        instructions = ch.contact or ""
    if not ch.verified:
        instructions += t(lang, "unverified_tag")
    return Channel(
        name=ch.name, url=ch.url, instructions=instructions, verified=ch.verified
    )


class RuleBasedAskService:
    def __init__(
        self,
        topics: TopicRegistry,
        services: ServiceCatalog,
        channels: ChannelCatalog,
        allow_unverified: bool,
    ):
        self._topics = topics
        self._services = services
        self._channels = channels
        self._allow_unverified = allow_unverified

    def _ok(self, verified: bool) -> bool:
        return verified or self._allow_unverified

    def _rank_services(self, text: str, topic) -> list[Service]:
        scored = []
        for s in self._services.all():
            kw_hits = count_hits(s.keywords, text)
            if kw_hits == 0:
                continue
            owner = self._topics.get(s.topic)
            bonus = count_hits(owner.keywords, text) if owner else 0
            scored.append((2 * kw_hits + bonus, s))
        if scored:
            best = max(score for score, _ in scored)
            return [s for score, s in scored if score == best]
        if topic is not None:  # topic known, service unclear: offer that topic's services
            return self._services.for_topic(topic.id)
        return []

    def _general_channel(self, topic_id: str, lang: str) -> Channel | None:
        usable = [c for c in self._channels.for_topic(topic_id) if self._ok(c.verified)]
        return to_channel(usable[0], lang) if usable else None

    async def ask(self, req: AskRequest) -> AskResponse:
        lang = normalize_lang(req.language)
        text = req.question
        base = {"language": lang, "disclaimer": t(lang, "disclaimer"), "is_mock": False}

        # 1) Complaint intent: a complaint-enabled topic plus a problem signal.
        complaint_topic, _ = best_topic(self._topics.all(), text, complaint_only=True)
        if complaint_topic and has_complaint_signal(text):
            return AskResponse(
                status="answered",
                intent="complaint",
                answer=t(lang, "ans_complaint", category=complaint_topic.display_name(lang)),
                topic_id=complaint_topic.id,
                sources=[],
                **base,
            )

        # 2) Information: catalog first.
        topic, _ = best_topic(self._topics.all(), text)
        ranked = self._rank_services(text, topic)
        services = [s for s in ranked if self._ok(s.verified)][:MAX_SERVICES]
        if services:
            return self._service_answer(services, lang, base)

        # 3) Known topic, no verified answer available.
        if topic is not None:
            return AskResponse(
                status="insufficient_evidence",
                intent="information",
                answer=t(lang, "ans_insufficient"),
                topic_id=topic.id,
                sources=[],
                official_channel=self._general_channel(topic.id, lang),
                **base,
            )

        # 4) Outside supported scope.
        names = ", ".join(tp.display_name(lang) for tp in self._topics.all())
        return AskResponse(
            status="unsupported_topic",
            intent="unsupported",
            answer=t(lang, "ans_unsupported", topics=names),
            topic_id=None,
            sources=[],
            **base,
        )

    def _service_answer(self, services: list[Service], lang: str, base: dict) -> AskResponse:
        if len(services) == 1:
            s = services[0]
            parts = [t(lang, "ans_one", name=s.display_name(lang), authority=s.authority)]
            if s.jurisdiction == "maharashtra":
                parts.append(t(lang, "state_note"))
        else:
            listing = "\n".join(f"• {s.display_name(lang)} — {s.authority}" for s in services)
            parts = [t(lang, "ans_many", list=listing)]
        parts.append(t(lang, "fees_note"))
        if any(not s.verified for s in services):
            parts.append(t(lang, "unverified_note"))

        sources = [
            Source(
                title=f"{s.display_name(lang)} — {s.authority}",
                url=s.official_url,
                retrieved_at=(
                    datetime.combine(s.checked_on, time.min, tzinfo=timezone.utc)
                    if s.checked_on
                    else None
                ),
                verified=s.verified,
            )
            for s in services
        ]
        # A BMC helpline is only relevant for BMC services, not state ones.
        all_bmc = all(s.jurisdiction == "bmc" for s in services)
        return AskResponse(
            status="answered",
            intent="information",
            answer="\n\n".join(parts),
            topic_id=services[0].topic,
            sources=sources,
            services=[
                ServiceInfo(
                    id=s.id,
                    name=s.display_name(lang),
                    authority=s.authority,
                    jurisdiction=s.jurisdiction,
                    official_url=s.official_url,
                    verified=s.verified,
                )
                for s in services
            ],
            steps=[t(lang, "step_1"), t(lang, "step_2"), t(lang, "step_3")],
            official_channel=self._general_channel(services[0].topic, lang) if all_bmc else None,
            **base,
        )


class RuleBasedComplaintService:
    def __init__(self, topics: TopicRegistry, channels: ChannelCatalog, allow_unverified: bool):
        self._topics = topics
        self._channels = channels
        self._allow_unverified = allow_unverified

    async def analyze(self, req: AnalyzeRequest) -> AnalyzeResponse:
        lang = normalize_lang(req.language)
        topic, hits = best_topic(self._topics.all(), req.description, complaint_only=True)
        location = req.location or None
        missing: list[str] = []
        questions: list[FollowUpQuestion] = []

        if topic is None:
            missing.append("description")
            questions.append(FollowUpQuestion(field="description", question=t(lang, "q_description")))
        if location is None:
            missing.append("location")
            questions.append(FollowUpQuestion(field="location", question=t(lang, "q_location")))

        return AnalyzeResponse(
            category_id=topic.id if topic else None,
            category_name=topic.display_name(lang) if topic else None,
            confidence=min(0.4 + 0.15 * hits, 0.9) if topic else 0.0,
            extracted=ExtractedFields(description=req.description, location=location),
            missing_fields=missing,
            follow_up_questions=questions,
            ready_to_draft=not missing,
            language=lang,
            is_mock=False,
        )

    async def draft(self, req: DraftRequest) -> DraftResponse:
        topic = self._topics.get(req.category_id)
        if topic is None or not topic.complaint_enabled:
            raise AppError("unknown_category", "Unknown complaint category.", 422)
        lang = normalize_lang(req.language)
        category = topic.display_name(lang)

        lines = [
            t(lang, "d_to"),
            "",
            t(lang, "d_intro"),
            req.description,
            t(lang, "d_location", location=req.location),
        ]
        if req.landmark:
            lines.append(t(lang, "d_landmark", landmark=req.landmark))
        lines += ["", t(lang, "d_request"), "", t(lang, "d_footer")]

        fields = {"category": category, "location": req.location}
        if req.landmark:
            fields["landmark"] = req.landmark

        usable = [c for c in self._channels.for_topic(topic.id) if c.verified or self._allow_unverified]
        usable.sort(key=lambda c: 0 if c.supports_complaints else 1)  # stable sort
        primary = to_channel(usable[0], lang) if usable else None
        others = [to_channel(c, lang) for c in usable[1:]]

        return DraftResponse(
            draft=Draft(
                title=t(lang, "d_title", category=category, location=req.location),
                body="\n".join(lines),
                fields=fields,
            ),
            channel=primary,
            other_channels=others,
            next_steps=[t(lang, f"ns_{i}") for i in range(1, 5)],
            disclaimer=t(lang, "disclaimer"),
            language=lang,
            is_mock=False,
        )