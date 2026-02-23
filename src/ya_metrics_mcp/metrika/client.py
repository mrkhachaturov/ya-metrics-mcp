"""Async HTTP client for Yandex Metrika API."""
from __future__ import annotations

import asyncio
import logging

import httpx

from ya_metrics_mcp.exceptions import AuthenticationError, MCPYaMetrikaError
from ya_metrics_mcp.metrika.config import YaMetrikaConfig

logger = logging.getLogger("ya-metrics")

API_BASE = "https://api-metrika.yandex.net"
RETRYABLE_STATUS_CODES = {500, 502, 503}


class YaMetrikaClient:
    def __init__(self, config: YaMetrikaConfig) -> None:
        self.config = config
        self._http = httpx.AsyncClient(
            base_url=API_BASE,
            headers={"Authorization": f"OAuth {config.api_key}"},
            timeout=config.timeout,
        )

    async def get(self, path: str, params: dict[str, str | int | None]) -> dict:
        """Make a GET request with retry logic."""
        clean_params = {k: v for k, v in params.items() if v is not None}
        return await self._request_with_retry(path, clean_params, attempt=1)

    async def _request_with_retry(
        self, path: str, params: dict, attempt: int
    ) -> dict:
        try:
            response = await self._http.get(path, params=params)
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
            if attempt < self.config.retries:
                await asyncio.sleep(self.config.retry_delay * attempt)
                return await self._request_with_retry(path, params, attempt + 1)
            raise MCPYaMetrikaError(f"Request failed after {attempt} attempts: {exc}") from exc

        if response.status_code in (401, 403):
            raise AuthenticationError(
                f"Yandex Metrika authentication failed ({response.status_code}). "
                "Check your YANDEX_API_KEY."
            )

        if response.status_code in RETRYABLE_STATUS_CODES:
            if attempt < self.config.retries:
                await asyncio.sleep(self.config.retry_delay * attempt)
                return await self._request_with_retry(path, params, attempt + 1)
            raise MCPYaMetrikaError(
                f"Yandex Metrika error {response.status_code}: {response.text}"
            )

        if not response.is_success:
            raise MCPYaMetrikaError(
                f"Yandex Metrika error {response.status_code}: {response.text}"
            )

        return response.json()

    async def close(self) -> None:
        await self._http.aclose()
