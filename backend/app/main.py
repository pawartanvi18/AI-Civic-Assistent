import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, meta, topics
from app.config import Settings, get_settings
from app.domain.sources import load_sources
from app.domain.topics import load_topics
from app.errors import register_error_handlers
from app.logging_config import configure_logging

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
    app.include_router(meta.router, prefix="/api/v1")
    app.include_router(topics.router, prefix="/api/v1")
    return app


app = create_app()