import os
from pathlib import Path
from typing import Any
import yaml


class AppConfig:
    def __init__(
            self,
            api_key: str,
            api_host: str,
            limit_message: int | None,
            limit_chars: int | None,
            temperature: float,
            system_prompt: str | None,
    ) -> None:
        self.api_key = api_key
        self.api_host = api_host
        self.limit_message = limit_message
        self.limit_chars = limit_chars
        self.temperature = temperature
        self.system_prompt = system_prompt


def _read_yaml(name: str, yaml_data: dict[str, Any], default: Any = None) -> Any:
    value = os.environ.get(name)
    if value is not None and value != '':
        return value
    return yaml_data.get(name.lower(), default)


def _parse_int(value: Any) -> int | None:
    if value in (None, ''):
        return None
    return int(value)


def _parse_float(value: Any, default: float) -> float:
    if value in (None, ''):
        return default
    return float(value)


def _validate_config(
        limit_message: int | None,
        limit_chars: int | None,
        temperature: float,
) -> None:
    if limit_message is not None and limit_message < 1:
        raise ValueError('LIMIT_MESSAGE must be positive')
    if limit_chars is not None and limit_chars < 1:
        raise ValueError('LIMIT_CHARS must be positive')
    if not 0 <= temperature <= 1:
        raise ValueError('TEMPERATURE must be between 0 and 1')


def load_config(base_dir: Path | None = None) -> AppConfig | None:
    base_dir = base_dir or Path(__file__).resolve().parents[1]
    yaml_path = base_dir / 'config.yaml'

    yaml_data: dict[str, Any] = {}
    if yaml_path.exists():
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f) or {}

    api_key = _read_yaml('API_KEY', yaml_data)
    api_host = _read_yaml('API_HOST', yaml_data)

    if not api_key or not api_host:
        return None

    limit_message = _parse_int(_read_yaml('LIMIT_MESSAGE', yaml_data))
    limit_chars = _parse_int(_read_yaml('LIMIT_CHARS', yaml_data))
    temperature = _parse_float(_read_yaml('TEMPERATURE', yaml_data), 0.7)

    _validate_config(limit_message, limit_chars, temperature)

    system_prompt = _read_yaml('SYSTEM_PROMPT', yaml_data)
    system_prompt = str(system_prompt) if system_prompt not in (None, '') else None

    return AppConfig(
        api_key=str(api_key),
        api_host=str(api_host),
        limit_message=limit_message,
        limit_chars=limit_chars,
        temperature=temperature,
        system_prompt=system_prompt,
    )