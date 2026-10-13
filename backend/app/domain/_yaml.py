from pathlib import Path

import yaml

from app.errors import ConfigurationError


def read_yaml_mapping(path: Path) -> dict:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as e:
        raise ConfigurationError(f"Cannot read {path}: {e}") from e
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in {path}: {e}") from e
    if not isinstance(data, dict):
        raise ConfigurationError(f"{path} must contain a mapping at the top level.")
    return data