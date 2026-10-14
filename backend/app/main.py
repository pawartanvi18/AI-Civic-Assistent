import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import ask, complaints, feedback, health, meta, topics
from app.config import Settings, get_settings
from app.domain.sources import load_sources
from app.domain.topics import load_topics
from app.errors import register_error_handlers
from app.logging_config import configure_logging
from app.domain.channel_catalog import load_channels
from app.domain.service_catalog import load_services
from app.services.rule_based import RuleBasedAskService, RuleBasedComplaintService

logger = logging.getLogger("app.request")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    # Fail fast: bad YAML raises ConfigurationError at startup.
    registry = load_topics(settings.topics_file)
    allow_list = load_sources(settings.sources_file, registry.ids())

    app = FastAPI(title=settings.app_name, version=settings.app_version)
    app.state.settings = settings
    app.state.topics = registry
    app.state.allow_list = allow_list
  
    catalog = load_services(settings.services_file, registry.ids(), allow_list)
    channels = load_channels(settings.channels_file, registry.ids(), allow_list)
    app.state.service_catalog = catalog
    app.state.channels = channels
    app.state.ask_service = RuleBasedAskService(
        registry, catalog, channels, settings.allow_unverified_data
    )
    app.state.complaint_service = RuleBasedComplaintService(
        registry, channels, settings.allow_unverified_data
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request.state.request_id = uuid.uuid4().hex[:12]
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        logger.info(
            "request",
            extra={
                "request_id": request.state.request_id,
                "method": request.method,
                "path": request.url.path,  # path only; no query string or body
                "status": response.status_code,
                "duration_ms": round((time.perf_counter() - start) * 1000, 1),
            },
        )
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Content-Type"],
        expose_headers=["X-Request-ID"],
    )

    register_error_handlers(app)
    app.include_router(health.router)
    for r in (meta.router, topics.router, ask.router, complaints.router, feedback.router):
        app.include_router(r, prefix="/api/v1")
    return app


app = create_app()