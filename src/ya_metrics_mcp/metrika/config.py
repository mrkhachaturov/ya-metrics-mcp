"""Yandex Metrika configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass

from ya_metrics_mcp.exceptions import AuthenticationError


@dataclass
class YaMetrikaConfig:
    api_key: str
    timeout: int = 30
    retries: int = 3
    retry_delay: float = 1.0
    read_only: bool = False
    enabled_tools: list[str] | None = None

    @classmethod
    def from_env(cls) -> "YaMetrikaConfig":
        api_key = os.environ.get("YANDEX_API_KEY", "")
        if not api_key:
            raise AuthenticationError(
                "YANDEX_API_KEY environment variable is required. "
                "Get a token at https://oauth.yandex.ru/client/new"
            )
        enabled_raw = os.environ.get("ENABLED_TOOLS", "").strip()
        enabled_tools = (
            [t.strip() for t in enabled_raw.split(",") if t.strip()]
            if enabled_raw
            else None
        )
        return cls(
            api_key=api_key,
            timeout=int(os.environ.get("YANDEX_TIMEOUT", "30")),
            retries=int(os.environ.get("YANDEX_RETRIES", "3")),
            retry_delay=float(os.environ.get("YANDEX_RETRY_DELAY", "1.0")),
            read_only=os.environ.get("READ_ONLY_MODE", "").lower() == "true",
            enabled_tools=enabled_tools,
        )

    def is_auth_configured(self) -> bool:
        return bool(self.api_key)
