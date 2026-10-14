from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent

DEFAULT_DISCLAIMER = (
    "This is an independent guidance tool. It is NOT an official service of "
    "the Brihanmumbai Municipal Corporation or any government body. It does not "
    "submit complaints on your behalf. Always confirm information and submit "
    "complaints through official channels."
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    app_name: str = "Civic Assistant (Independent Tool)"
    app_version: str = "0.1.0"
    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    topics_file: Path = BASE_DIR / "data" / "topics.yaml"
    sources_file: Path = BASE_DIR / "data" / "sources.yaml"
    disclaimer: str = DEFAULT_DISCLAIMER

    services_file: Path = BASE_DIR / "data" / "services.yaml"
    channels_file: Path = BASE_DIR / "data" / "channels.yaml"
    # While true, unverified catalog entries are shown (clearly labelled).
    # Set ALLOW_UNVERIFIED_DATA=false once your sources are verified.
    allow_unverified_data: bool = True

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()