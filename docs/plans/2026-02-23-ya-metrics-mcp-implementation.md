# ya-metrics-mcp Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a production-quality Python MCP server for Yandex Metrika analytics, inspired by mcp-atlassian's architecture, that exposes 25 analytics tools via stdio and HTTP transports.

**Architecture:** FastMCP server with mixin-based domain fetchers (traffic, content, demographics, geographic, performance, advanced). Config loaded from env vars at startup, stored in FastMCP lifespan context, and injected into tool handlers via a dependency helper.

**Tech Stack:** Python 3.10+, FastMCP ≥2.13, httpx, Pydantic v2, Click, uvicorn, pytest + pytest-httpx, uv

**Design doc:** `docs/plans/2026-02-23-ya-metrics-mcp-design.md`
**Reference projects:**
- `../mcp-atlassian/` — architectural patterns to mirror
- `../yandex-metrika-mcp/` — 25 tools + Yandex API endpoints to port

---

## Task 1: Project scaffold

**Files:**
- Create: `pyproject.toml`
- Create: `src/ya_metrics_mcp/__init__.py`
- Create: `src/ya_metrics_mcp/exceptions.py`
- Create: `src/ya_metrics_mcp/servers/__init__.py`
- Create: `src/ya_metrics_mcp/metrika/__init__.py`
- Create: `src/ya_metrics_mcp/metrika/fetchers/__init__.py`
- Create: `src/ya_metrics_mcp/models/__init__.py`
- Create: `src/ya_metrics_mcp/utils/__init__.py`
- Create: `tests/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/conftest.py`

**Step 1: Initialize uv project**

```bash
cd /Users/mrkhachaturov/Developer/ya-metrics/ya-metrics-mcp
uv init --no-workspace --python 3.10
```

**Step 2: Write pyproject.toml**

Replace the generated `pyproject.toml` with:

```toml
[project]
name = "ya-metrics-mcp"
version = "0.1.0"
description = "MCP server for Yandex Metrika analytics"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
keywords = ["mcp", "yandex", "metrika", "analytics"]
dependencies = [
    "fastmcp>=2.13.0,<2.15.0",
    "httpx>=0.28.0",
    "pydantic>=2.10.0",
    "python-dotenv>=1.0.1",
    "click>=8.1.0",
    "uvicorn>=0.27.1",
    "starlette>=0.40.0",
]

[project.scripts]
ya-metrics-mcp = "ya_metrics_mcp:main"

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-httpx>=0.30",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/ya_metrics_mcp"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "B", "W", "I", "N", "UP"]

[tool.mypy]
python_version = "3.10"
strict = true
```

**Step 3: Install dependencies**

```bash
uv sync --extra dev
```

Expected: deps installed into `.venv/`

**Step 4: Create package skeleton**

```bash
mkdir -p src/ya_metrics_mcp/{servers,metrika/fetchers,models,utils,preprocessing}
mkdir -p tests/unit/test_fetchers
touch src/ya_metrics_mcp/__init__.py
touch src/ya_metrics_mcp/exceptions.py
touch src/ya_metrics_mcp/servers/__init__.py
touch src/ya_metrics_mcp/metrika/__init__.py
touch src/ya_metrics_mcp/metrika/fetchers/__init__.py
touch src/ya_metrics_mcp/models/__init__.py
touch src/ya_metrics_mcp/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/unit/test_fetchers/__init__.py
touch tests/conftest.py
```

**Step 5: Commit**

```bash
git init
git add .
git commit -m "chore: initialize ya-metrics-mcp project scaffold"
```

---

## Task 2: Exceptions

**Files:**
- Create: `src/ya_metrics_mcp/exceptions.py`
- Create: `tests/unit/test_exceptions.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_exceptions.py
from ya_metrics_mcp.exceptions import MCPYaMetrikaError, AuthenticationError


def test_mcp_error_is_exception():
    err = MCPYaMetrikaError("something went wrong")
    assert str(err) == "something went wrong"
    assert isinstance(err, Exception)


def test_auth_error_is_mcp_error():
    err = AuthenticationError("invalid token")
    assert isinstance(err, MCPYaMetrikaError)
    assert str(err) == "invalid token"
```

**Step 2: Run to verify it fails**

```bash
uv run pytest tests/unit/test_exceptions.py -v
```

Expected: `ImportError` — `MCPYaMetrikaError` not defined

**Step 3: Implement**

```python
# src/ya_metrics_mcp/exceptions.py
"""Custom exceptions for ya-metrics-mcp."""


class MCPYaMetrikaError(Exception):
    """Base exception for all ya-metrics-mcp errors."""


class AuthenticationError(MCPYaMetrikaError):
    """Raised when Yandex API authentication fails (401/403)."""
```

**Step 4: Run tests**

```bash
uv run pytest tests/unit/test_exceptions.py -v
```

Expected: 2 PASSED

**Step 5: Commit**

```bash
git add src/ya_metrics_mcp/exceptions.py tests/unit/test_exceptions.py
git commit -m "feat: add custom exceptions"
```

---

## Task 3: Configuration

**Files:**
- Create: `src/ya_metrics_mcp/metrika/config.py`
- Create: `tests/unit/test_config.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_config.py
import os
import pytest
from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.exceptions import AuthenticationError


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("YANDEX_API_KEY", "test-token-123")
    config = YaMetrikaConfig.from_env()
    assert config.api_key == "test-token-123"
    assert config.timeout == 30
    assert config.retries == 3
    assert config.retry_delay == 1.0
    assert config.read_only is False
    assert config.enabled_tools is None


def test_config_from_env_custom_values(monkeypatch):
    monkeypatch.setenv("YANDEX_API_KEY", "tok")
    monkeypatch.setenv("YANDEX_TIMEOUT", "60")
    monkeypatch.setenv("YANDEX_RETRIES", "5")
    monkeypatch.setenv("READ_ONLY_MODE", "true")
    monkeypatch.setenv("ENABLED_TOOLS", "get_visits,get_account_info")
    config = YaMetrikaConfig.from_env()
    assert config.timeout == 60
    assert config.retries == 5
    assert config.read_only is True
    assert config.enabled_tools == ["get_visits", "get_account_info"]


def test_config_raises_if_no_api_key(monkeypatch):
    monkeypatch.delenv("YANDEX_API_KEY", raising=False)
    with pytest.raises(AuthenticationError, match="YANDEX_API_KEY"):
        YaMetrikaConfig.from_env()


def test_is_auth_configured():
    config = YaMetrikaConfig(api_key="tok")
    assert config.is_auth_configured() is True

    config_empty = YaMetrikaConfig(api_key="")
    assert config_empty.is_auth_configured() is False
```

**Step 2: Run to verify it fails**

```bash
uv run pytest tests/unit/test_config.py -v
```

Expected: ImportError

**Step 3: Implement**

```python
# src/ya_metrics_mcp/metrika/config.py
"""Yandex Metrika configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass, field

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
```

**Step 4: Run tests**

```bash
uv run pytest tests/unit/test_config.py -v
```

Expected: 4 PASSED

**Step 5: Commit**

```bash
git add src/ya_metrics_mcp/metrika/config.py tests/unit/test_config.py
git commit -m "feat: add YaMetrikaConfig with env loading and validation"
```

---

## Task 4: HTTP Client

**Files:**
- Create: `src/ya_metrics_mcp/metrika/client.py`
- Create: `tests/unit/test_client.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_client.py
import pytest
import httpx
import pytest_httpx
from ya_metrics_mcp.metrika.client import YaMetrikaClient
from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.exceptions import MCPYaMetrikaError, AuthenticationError


@pytest.fixture
def config():
    return YaMetrikaConfig(api_key="test-token")


@pytest.fixture
def client(config):
    return YaMetrikaClient(config)


@pytest.mark.asyncio
async def test_get_sends_oauth_header(httpx_mock, client):
    httpx_mock.add_response(
        url="https://api-metrika.yandex.net/stat/v1/data?ids=123",
        json={"data": []},
    )
    result = await client.get("/stat/v1/data", {"ids": "123"})
    assert result == {"data": []}
    request = httpx_mock.get_requests()[0]
    assert request.headers["Authorization"] == "OAuth test-token"


@pytest.mark.asyncio
async def test_get_raises_auth_error_on_401(httpx_mock, client):
    httpx_mock.add_response(
        url="https://api-metrika.yandex.net/stat/v1/data?ids=123",
        status_code=401,
        text="Unauthorized",
    )
    with pytest.raises(AuthenticationError):
        await client.get("/stat/v1/data", {"ids": "123"})


@pytest.mark.asyncio
async def test_get_raises_on_500(httpx_mock, client):
    # 500 is retried; after all retries raises MCPYaMetrikaError
    httpx_mock.add_response(
        url="https://api-metrika.yandex.net/stat/v1/data?ids=123",
        status_code=500,
        text="Server Error",
    )
    # 3 retries configured but we patch retry_delay to 0 to keep test fast
    client.config.retries = 1
    client.config.retry_delay = 0.0
    with pytest.raises(MCPYaMetrikaError, match="500"):
        await client.get("/stat/v1/data", {"ids": "123"})


@pytest.mark.asyncio
async def test_close(client):
    await client.close()  # should not raise
```

**Step 2: Run to verify it fails**

```bash
uv run pytest tests/unit/test_client.py -v
```

Expected: ImportError

**Step 3: Implement**

```python
# src/ya_metrics_mcp/metrika/client.py
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
```

**Step 4: Run tests**

```bash
uv run pytest tests/unit/test_client.py -v
```

Expected: 4 PASSED

**Step 5: Commit**

```bash
git add src/ya_metrics_mcp/metrika/client.py tests/unit/test_client.py
git commit -m "feat: add YaMetrikaClient with retry and auth error handling"
```

---

## Task 5: Utilities

**Files:**
- Create: `src/ya_metrics_mcp/utils/logging.py`
- Create: `src/ya_metrics_mcp/utils/decorators.py`
- Create: `src/ya_metrics_mcp/utils/date.py`
- Create: `src/ya_metrics_mcp/utils/tools.py`
- Create: `src/ya_metrics_mcp/utils/lifecycle.py`
- Create: `tests/unit/test_utils.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_utils.py
import pytest
from ya_metrics_mcp.utils.logging import mask_sensitive
from ya_metrics_mcp.utils.date import validate_date, default_date_range
from ya_metrics_mcp.utils.tools import filter_tools
from ya_metrics_mcp.metrika.config import YaMetrikaConfig


def test_mask_sensitive_keeps_last_4():
    assert mask_sensitive("y0_AgAAAAlong_token_value") == "****alue"


def test_mask_sensitive_short_token():
    assert mask_sensitive("abc") == "****"


def test_validate_date_valid():
    assert validate_date("2024-01-15") == "2024-01-15"


def test_validate_date_invalid():
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_date("15-01-2024")


def test_validate_date_none_returns_none():
    assert validate_date(None) is None


def test_default_date_range():
    date_from, date_to = default_date_range(days=7)
    assert date_to > date_from
    assert len(date_from) == 10  # YYYY-MM-DD


def test_filter_tools_no_filter():
    config = YaMetrikaConfig(api_key="tok")
    tools = ["get_visits", "get_account_info", "sources_summary"]
    assert filter_tools(tools, config) == tools


def test_filter_tools_enabled_list():
    config = YaMetrikaConfig(api_key="tok", enabled_tools=["get_visits"])
    tools = ["get_visits", "get_account_info"]
    assert filter_tools(tools, config) == ["get_visits"]


def test_filter_tools_read_only_removes_write():
    config = YaMetrikaConfig(api_key="tok", read_only=True)
    read_tools = [("get_visits", {"read"}), ("delete_counter", {"write"})]
    result = filter_tools([t for t, _ in read_tools], config,
                          tool_tags={t: tags for t, tags in read_tools})
    assert result == ["get_visits"]
```

**Step 2: Run to verify it fails**

```bash
uv run pytest tests/unit/test_utils.py -v
```

Expected: ImportError

**Step 3: Implement utils**

```python
# src/ya_metrics_mcp/utils/logging.py
"""Logging setup and sensitive data masking."""
import logging
import sys


def setup_logging(verbose: int = 0) -> None:
    """Configure logging level based on verbosity flag.
    verbose=0 → WARNING, verbose=1 → INFO, verbose=2+ → DEBUG
    """
    level = logging.WARNING
    if verbose == 1:
        level = logging.INFO
    elif verbose >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        stream=sys.stderr,
        level=level,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )


def mask_sensitive(token: str, keep_chars: int = 4) -> str:
    """Mask a sensitive token, keeping only the last keep_chars characters."""
    if len(token) <= keep_chars:
        return "****"
    return f"****{token[-keep_chars:]}"
```

```python
# src/ya_metrics_mcp/utils/date.py
"""Date utilities for Yandex Metrika API."""
from __future__ import annotations

import re
from datetime import date, timedelta


_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_date(value: str | None) -> str | None:
    """Validate and return a YYYY-MM-DD date string, or raise ValueError."""
    if value is None:
        return None
    if not _DATE_PATTERN.match(value):
        raise ValueError(f"Date must be in YYYY-MM-DD format, got: {value!r}")
    return value


def default_date_range(days: int = 7) -> tuple[str, str]:
    """Return (date_from, date_to) for the last N days."""
    today = date.today()
    date_from = today - timedelta(days=days)
    return date_from.isoformat(), today.isoformat()
```

```python
# src/ya_metrics_mcp/utils/tools.py
"""Tool filtering logic for READ_ONLY_MODE and ENABLED_TOOLS."""
from __future__ import annotations

from ya_metrics_mcp.metrika.config import YaMetrikaConfig


def filter_tools(
    tool_names: list[str],
    config: YaMetrikaConfig,
    tool_tags: dict[str, set[str]] | None = None,
) -> list[str]:
    """Filter tool names based on config restrictions.

    Args:
        tool_names: All available tool names.
        config: Server configuration.
        tool_tags: Optional mapping of tool_name → set of tags (e.g. {"read"}, {"write"}).

    Returns:
        Filtered list of tool names.
    """
    result = tool_names

    if config.enabled_tools is not None:
        result = [t for t in result if t in config.enabled_tools]

    if config.read_only and tool_tags:
        result = [t for t in result if "write" not in tool_tags.get(t, set())]

    return result
```

```python
# src/ya_metrics_mcp/utils/decorators.py
"""Decorator utilities for error handling and access control."""
from __future__ import annotations

import functools
import logging
from collections.abc import Callable
from typing import Any

from ya_metrics_mcp.exceptions import MCPYaMetrikaError

logger = logging.getLogger("ya-metrics")


def handle_api_errors(service_name: str = "Yandex Metrika API") -> Callable:
    """Decorator that catches API errors and re-raises as MCPYaMetrikaError."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except MCPYaMetrikaError:
                raise
            except Exception as exc:
                logger.error("%s error in %s: %s", service_name, func.__name__, exc)
                raise MCPYaMetrikaError(
                    f"{service_name} error in {func.__name__}: {exc}"
                ) from exc
        return wrapper
    return decorator
```

```python
# src/ya_metrics_mcp/utils/lifecycle.py
"""Signal handling for graceful shutdown."""
import asyncio
import logging
import signal
import sys

logger = logging.getLogger("ya-metrics")


def setup_signal_handlers() -> None:
    """Register SIGTERM and SIGINT handlers for graceful shutdown."""
    def _handle_signal(sig: int, frame: object) -> None:
        logger.info("Received signal %s, shutting down...", signal.Signals(sig).name)
        sys.exit(0)

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)
```

**Step 4: Run tests**

```bash
uv run pytest tests/unit/test_utils.py -v
```

Expected: 9 PASSED

**Step 5: Commit**

```bash
git add src/ya_metrics_mcp/utils/ tests/unit/test_utils.py
git commit -m "feat: add utility modules (logging, date, tools filter, decorators, lifecycle)"
```

---

## Task 6: Base Fetcher

**Files:**
- Create: `src/ya_metrics_mcp/metrika/fetchers/base.py`
- Create: `tests/unit/test_fetchers/test_base.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_fetchers/test_base.py
import pytest
from ya_metrics_mcp.metrika.fetchers.base import BaseFetcher
from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.metrika.client import YaMetrikaClient


@pytest.fixture
def fetcher():
    config = YaMetrikaConfig(api_key="test-token")
    client = YaMetrikaClient(config)
    return BaseFetcher(client)


def test_base_fetcher_holds_client(fetcher):
    assert fetcher.client is not None


def test_base_fetcher_format_json(fetcher):
    data = {"rows": [{"key": "value"}]}
    result = fetcher.format_response(data)
    assert "rows" in result
    assert isinstance(result, str)
```

**Step 2: Run to verify it fails**

```bash
uv run pytest tests/unit/test_fetchers/test_base.py -v
```

Expected: ImportError

**Step 3: Implement**

```python
# src/ya_metrics_mcp/metrika/fetchers/base.py
"""Base fetcher class."""
from __future__ import annotations

import json

from ya_metrics_mcp.metrika.client import YaMetrikaClient


class BaseFetcher:
    def __init__(self, client: YaMetrikaClient) -> None:
        self.client = client

    def format_response(self, data: dict | list) -> str:
        """Format API response as a pretty-printed JSON string."""
        return json.dumps(data, ensure_ascii=False, indent=2)
```

**Step 4: Run tests**

```bash
uv run pytest tests/unit/test_fetchers/ -v
```

Expected: 2 PASSED

**Step 5: Commit**

```bash
git add src/ya_metrics_mcp/metrika/fetchers/base.py tests/unit/test_fetchers/
git commit -m "feat: add BaseFetcher"
```

---

## Task 7: Traffic Mixin (7 tools)

Ports these tools from `../yandex-metrika-mcp/src/client.ts`:
`get_account_info`, `get_visits`, `sources_summary`, `sources_search_phrases`, `get_traffic_sources_types`, `get_search_engines_data`, `get_new_users_by_source`

**Files:**
- Create: `src/ya_metrics_mcp/metrika/fetchers/traffic.py`
- Create: `tests/unit/test_fetchers/test_traffic.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_fetchers/test_traffic.py
import pytest
from ya_metrics_mcp.metrika.fetchers.traffic import TrafficMixin
from ya_metrics_mcp.metrika.fetchers.base import BaseFetcher
from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.metrika.client import YaMetrikaClient


class TestFetcher(TrafficMixin, BaseFetcher):
    pass


@pytest.fixture
def fetcher(httpx_mock):
    config = YaMetrikaConfig(api_key="test-token")
    client = YaMetrikaClient(config)
    return TestFetcher(client)


@pytest.mark.asyncio
async def test_get_account_info(httpx_mock, fetcher):
    httpx_mock.add_response(
        url="https://api-metrika.yandex.net/management/v1/counter/12345",
        json={"counter": {"id": 12345, "name": "My Site"}},
    )
    result = await fetcher.get_account_info("12345")
    assert "12345" in result or "My Site" in result


@pytest.mark.asyncio
async def test_get_visits_default_dates(httpx_mock, fetcher):
    httpx_mock.add_response(
        url__regex=r".*stat/v1/data.*",
        json={"data": [{"dimensions": [], "metrics": [100]}]},
    )
    result = await fetcher.get_visits("12345")
    assert "data" in result


@pytest.mark.asyncio
async def test_get_visits_raises_on_invalid_date(fetcher):
    from ya_metrics_mcp.exceptions import MCPYaMetrikaError
    with pytest.raises((ValueError, MCPYaMetrikaError)):
        await fetcher.get_visits("12345", date_from="not-a-date")
```

**Step 2: Run to verify it fails**

```bash
uv run pytest tests/unit/test_fetchers/test_traffic.py -v
```

Expected: ImportError

**Step 3: Implement — reference `../yandex-metrika-mcp/src/client.ts` for exact API URLs and params**

```python
# src/ya_metrics_mcp/metrika/fetchers/traffic.py
"""Traffic and sources analytics fetcher mixin."""
from __future__ import annotations

from ya_metrics_mcp.utils.date import default_date_range, validate_date
from ya_metrics_mcp.utils.decorators import handle_api_errors


class TrafficMixin:
    """Mixin for traffic sources and basic visit analytics.

    Requires self.client (YaMetrikaClient) and self.format_response() from BaseFetcher.
    """

    @handle_api_errors()
    async def get_account_info(self, counter_id: str) -> str:
        data = await self.client.get(f"/management/v1/counter/{counter_id}", {})
        return self.format_response(data)

    @handle_api_errors()
    async def get_visits(
        self,
        counter_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        if date_from is None and date_to is None:
            date_from, date_to = default_date_range(days=7)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "metrics": "ym:s:visits",
                "date1": date_from,
                "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def sources_summary(self, counter_id: str) -> str:
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "sources_summary", "id": counter_id},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def sources_search_phrases(self, counter_id: str) -> str:
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "sources_search_phrases", "id": counter_id},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_traffic_sources_types(self, counter_id: str) -> str:
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:lastTrafficSource",
                "metrics": "ym:s:visits,ym:s:users",
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_search_engines_data(
        self,
        counter_id: str,
        exclude_robots: bool = False,
        new_users_only: bool = False,
    ) -> str:
        filters = ["ym:s:trafficSource=='organic'"]
        if exclude_robots:
            filters.append("ym:s:isRobot=='No'")
        if new_users_only:
            filters.append("ym:s:isNewUser=='Yes'")
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:searchEngine",
                "metrics": "ym:s:visits,ym:s:users",
                "filters": " AND ".join(filters),
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_new_users_by_source(
        self,
        counter_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        if date_from is None and date_to is None:
            date_from, date_to = default_date_range(days=30)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:lastTrafficSource",
                "metrics": "ym:s:newUsers",
                "date1": date_from,
                "date2": date_to,
            },
        )
        return self.format_response(data)
```

**Step 4: Run tests**

```bash
uv run pytest tests/unit/test_fetchers/test_traffic.py -v
```

Expected: 3 PASSED

**Step 5: Commit**

```bash
git add src/ya_metrics_mcp/metrika/fetchers/traffic.py tests/unit/test_fetchers/test_traffic.py
git commit -m "feat: add TrafficMixin with 7 traffic analytics methods"
```

---

## Task 8: Content Mixin (5 tools)

Ports: `get_content_analytics_sources`, `_categories`, `_authors`, `_topics`, `_articles`

**Files:**
- Create: `src/ya_metrics_mcp/metrika/fetchers/content.py`
- Create: `tests/unit/test_fetchers/test_content.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_fetchers/test_content.py
import pytest
from ya_metrics_mcp.metrika.fetchers.content import ContentMixin
from ya_metrics_mcp.metrika.fetchers.base import BaseFetcher
from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.metrika.client import YaMetrikaClient


class TestFetcher(ContentMixin, BaseFetcher):
    pass


@pytest.fixture
def fetcher():
    return TestFetcher(YaMetrikaClient(YaMetrikaConfig(api_key="tok")))


@pytest.mark.asyncio
async def test_get_content_analytics_sources(httpx_mock, fetcher):
    httpx_mock.add_response(url__regex=r".*stat/v1/data.*", json={"data": []})
    result = await fetcher.get_content_analytics_sources("12345")
    assert isinstance(result, str)
```

**Step 2: Implement — reference `../yandex-metrika-mcp/src/client.ts` for presets**

```python
# src/ya_metrics_mcp/metrika/fetchers/content.py
"""Content (publishers) analytics fetcher mixin."""
from __future__ import annotations

from ya_metrics_mcp.utils.date import default_date_range, validate_date
from ya_metrics_mcp.utils.decorators import handle_api_errors


class ContentMixin:
    @handle_api_errors()
    async def get_content_analytics_sources(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "publishers_sources", "id": counter_id, "date1": date_from, "date2": date_to},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_content_analytics_categories(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "publishers_rubrics", "id": counter_id, "date1": date_from, "date2": date_to},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_content_analytics_authors(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "publishers_authors", "id": counter_id, "date1": date_from, "date2": date_to},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_content_analytics_topics(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "publishers_thematics", "id": counter_id, "date1": date_from, "date2": date_to},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_content_analytics_articles(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:publisherArticle",
                "metrics": "ym:s:publisherviews",
                "filters": "ym:s:publisherArticle!n",
                "sort": "-ym:s:publisherviews",
                "date1": date_from,
                "date2": date_to,
            },
        )
        return self.format_response(data)
```

**Step 3: Run tests**

```bash
uv run pytest tests/unit/test_fetchers/test_content.py -v
```

Expected: 1 PASSED

**Step 4: Commit**

```bash
git add src/ya_metrics_mcp/metrika/fetchers/content.py tests/unit/test_fetchers/test_content.py
git commit -m "feat: add ContentMixin with 5 publisher analytics methods"
```

---

## Task 9: Demographics Mixin (4 tools)

Ports: `get_user_demographics`, `get_device_analysis`, `get_mobile_vs_desktop`, `get_page_depth_analysis`

**Files:**
- Create: `src/ya_metrics_mcp/metrika/fetchers/demographics.py`
- Create: `tests/unit/test_fetchers/test_demographics.py`

Pattern is identical to ContentMixin. Write one test, implement all 4 methods.

```python
# src/ya_metrics_mcp/metrika/fetchers/demographics.py
"""User demographics and device analytics fetcher mixin."""
from __future__ import annotations

from ya_metrics_mcp.utils.date import default_date_range, validate_date
from ya_metrics_mcp.utils.decorators import handle_api_errors


class DemographicsMixin:
    @handle_api_errors()
    async def get_user_demographics(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:ageInterval,ym:s:gender,ym:s:deviceCategory",
                "metrics": "ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:bounceRate,ym:s:avgVisitDurationSeconds",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_device_analysis(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:browser,ym:s:operatingSystem",
                "metrics": "ym:s:visits,ym:s:pageviews,ym:s:bounceRate,ym:s:avgVisitDurationSeconds",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_mobile_vs_desktop(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:deviceCategory",
                "metrics": "ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:bounceRate,ym:s:avgVisitDurationSeconds",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_page_depth_analysis(
        self, counter_id: str, min_pages: int = 5
    ) -> str:
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "metrics": "ym:s:visits,ym:s:users",
                "filters": f"ym:s:pageViews>{min_pages}",
            },
        )
        return self.format_response(data)
```

Write one smoke test in `tests/unit/test_fetchers/test_demographics.py`, run, commit.

```bash
git commit -m "feat: add DemographicsMixin with 4 user behavior methods"
```

---

## Task 10: Geographic Mixin (2 tools)

Ports: `get_regional_data`, `get_geographical_organic_traffic`

```python
# src/ya_metrics_mcp/metrika/fetchers/geographic.py
"""Geographic analytics fetcher mixin."""
from __future__ import annotations

from ya_metrics_mcp.utils.date import validate_date
from ya_metrics_mcp.utils.decorators import handle_api_errors


class GeographicMixin:
    @handle_api_errors()
    async def get_regional_data(
        self,
        counter_id: str,
        cities: list[str] | None = None,
    ) -> str:
        if cities is None:
            cities = ["Москва", "Санкт-Петербург"]
        city_filter = ",".join(f"'{c}'" for c in cities)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:regionCityName",
                "metrics": "ym:s:visits,ym:s:users",
                "filters": f"ym:s:regionCityName=.({city_filter})",
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_geographical_organic_traffic(
        self,
        counter_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:regionCountry,ym:s:regionCity",
                "metrics": "ym:s:visits,ym:s:users",
                "filters": "ym:s:trafficSource=='organic'",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)
```

Write one smoke test, run, commit:
```bash
git commit -m "feat: add GeographicMixin with 2 regional analytics methods"
```

---

## Task 11: Performance Mixin (4 tools)

Ports: `get_page_performance`, `get_goals_conversion`, `get_organic_search_performance`, `get_conversion_rate_by_source_and_landing`

```python
# src/ya_metrics_mcp/metrika/fetchers/performance.py
"""Performance and conversion analytics fetcher mixin."""
from __future__ import annotations

from ya_metrics_mcp.utils.date import validate_date
from ya_metrics_mcp.utils.decorators import handle_api_errors


class PerformanceMixin:
    @handle_api_errors()
    async def get_page_performance(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:URLPath",
                "metrics": "ym:s:pageviews,ym:s:bounceRate,ym:s:avgVisitDurationSeconds",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_goals_conversion(
        self, counter_id: str, goal_ids: list[int]
    ) -> str:
        goal_metrics = ",".join(
            f"ym:s:goal{gid}conversionRate" for gid in goal_ids
        )
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "metrics": f"ym:s:users,{goal_metrics}",
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_organic_search_performance(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:searchEngine,ym:s:searchPhrase",
                "metrics": "ym:s:visits,ym:s:users,ym:s:pageviews",
                "filters": "ym:s:trafficSource=='organic'",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_conversion_rate_by_source_and_landing(
        self,
        counter_id: str,
        goal_id: int,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:trafficSource,ym:s:landingPage",
                "metrics": f"ym:s:visits,ym:s:goal{goal_id}conversionRate",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)
```

Write one smoke test, run, commit:
```bash
git commit -m "feat: add PerformanceMixin with 4 conversion/performance methods"
```

---

## Task 12: Advanced Mixin (4 tools)

Ports: `get_ecommerce_performance`, `get_data_by_time`, `get_yandex_direct_experiment`, `get_browsers_report`

```python
# src/ya_metrics_mcp/metrika/fetchers/advanced.py
"""Advanced and specialized analytics fetcher mixin."""
from __future__ import annotations

from ya_metrics_mcp.utils.date import validate_date
from ya_metrics_mcp.utils.decorators import handle_api_errors

_VALID_GROUPS = {"day", "week", "month", "quarter", "year"}


class AdvancedMixin:
    @handle_api_errors()
    async def get_ecommerce_performance(
        self,
        counter_id: str,
        currency: str = "RUB",
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:productCategory,ym:s:regionCountry,ym:s:regionCity",
                "metrics": f"ym:s:ecommercePurchases,ym:s:ecommerce{currency}ConvertedRevenue",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_data_by_time(
        self,
        counter_id: str,
        metrics: list[str],
        date_from: str | None = None,
        date_to: str | None = None,
        dimensions: list[str] | None = None,
        group: str = "day",
        top_keys: int = 7,
        timezone: str | None = None,
    ) -> str:
        if len(metrics) > 20:
            raise ValueError("Maximum 20 metrics allowed")
        if dimensions and len(dimensions) > 10:
            raise ValueError("Maximum 10 dimensions allowed")
        if group not in _VALID_GROUPS:
            raise ValueError(f"group must be one of {_VALID_GROUPS}")
        if not 1 <= top_keys <= 30:
            raise ValueError("top_keys must be between 1 and 30")
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data/bytime",
            {
                "ids": counter_id,
                "metrics": ",".join(metrics),
                "dimensions": ",".join(dimensions) if dimensions else None,
                "group": group,
                "top_keys": top_keys,
                "date1": date_from,
                "date2": date_to,
                "timezone": timezone,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_yandex_direct_experiment(
        self, counter_id: str, experiment_id: int
    ) -> str:
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": f"ym:s:experimentAB{experiment_id}",
                "metrics": "ym:s:bounceRate",
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_browsers_report(self, counter_id: str) -> str:
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "tech_platforms", "dimensions": "ym:s:browser", "id": counter_id},
        )
        return self.format_response(data)
```

Write one smoke test, run, commit:
```bash
git commit -m "feat: add AdvancedMixin with 4 advanced analytics methods"
```

---

## Task 13: YaMetrikaFetcher Composite

**Files:**
- Create: `src/ya_metrics_mcp/metrika/fetchers/fetcher.py`
- Create: `tests/unit/test_fetchers/test_fetcher.py`

**Step 1: Write the failing test**

```python
# tests/unit/test_fetchers/test_fetcher.py
from ya_metrics_mcp.metrika.fetchers.fetcher import YaMetrikaFetcher
from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.metrika.client import YaMetrikaClient


def test_fetcher_has_all_mixin_methods():
    config = YaMetrikaConfig(api_key="tok")
    client = YaMetrikaClient(config)
    fetcher = YaMetrikaFetcher(client)

    # spot-check one method from each mixin
    assert hasattr(fetcher, "get_visits")             # TrafficMixin
    assert hasattr(fetcher, "get_content_analytics_articles")  # ContentMixin
    assert hasattr(fetcher, "get_user_demographics")  # DemographicsMixin
    assert hasattr(fetcher, "get_regional_data")      # GeographicMixin
    assert hasattr(fetcher, "get_goals_conversion")   # PerformanceMixin
    assert hasattr(fetcher, "get_data_by_time")       # AdvancedMixin
```

**Step 2: Implement**

```python
# src/ya_metrics_mcp/metrika/fetchers/fetcher.py
"""Composite fetcher combining all domain mixins."""
from ya_metrics_mcp.metrika.fetchers.advanced import AdvancedMixin
from ya_metrics_mcp.metrika.fetchers.base import BaseFetcher
from ya_metrics_mcp.metrika.fetchers.content import ContentMixin
from ya_metrics_mcp.metrika.fetchers.demographics import DemographicsMixin
from ya_metrics_mcp.metrika.fetchers.geographic import GeographicMixin
from ya_metrics_mcp.metrika.fetchers.performance import PerformanceMixin
from ya_metrics_mcp.metrika.fetchers.traffic import TrafficMixin


class YaMetrikaFetcher(
    TrafficMixin,
    ContentMixin,
    DemographicsMixin,
    GeographicMixin,
    PerformanceMixin,
    AdvancedMixin,
    BaseFetcher,
):
    """Full Yandex Metrika fetcher with all analytics capabilities."""
```

**Step 3: Run all fetcher tests**

```bash
uv run pytest tests/unit/test_fetchers/ -v
```

Expected: all PASSED

**Step 4: Commit**

```bash
git add src/ya_metrics_mcp/metrika/fetchers/fetcher.py tests/unit/test_fetchers/test_fetcher.py
git commit -m "feat: add YaMetrikaFetcher composite class"
```

---

## Task 14: Server Context

**Files:**
- Create: `src/ya_metrics_mcp/servers/context.py`

```python
# src/ya_metrics_mcp/servers/context.py
"""Request context dataclass for FastMCP lifespan."""
from dataclasses import dataclass

from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.metrika.fetchers.fetcher import YaMetrikaFetcher


@dataclass
class MainAppContext:
    fetcher: YaMetrikaFetcher
    config: YaMetrikaConfig
```

No test needed (pure data container). Commit:
```bash
git add src/ya_metrics_mcp/servers/context.py
git commit -m "feat: add MainAppContext for FastMCP lifespan"
```

---

## Task 15: FastMCP Server Main

**Files:**
- Create: `src/ya_metrics_mcp/servers/main.py`
- Create: `src/ya_metrics_mcp/servers/dependencies.py`
- Create: `tests/unit/test_server.py`

**Step 1: Write dependencies.py**

```python
# src/ya_metrics_mcp/servers/dependencies.py
"""Dependency injection helpers for tool handlers."""
from fastmcp import Context

from ya_metrics_mcp.metrika.fetchers.fetcher import YaMetrikaFetcher
from ya_metrics_mcp.servers.context import MainAppContext


async def get_metrika_fetcher(ctx: Context) -> YaMetrikaFetcher:
    """Retrieve the shared YaMetrikaFetcher from lifespan context."""
    app_ctx: MainAppContext = ctx.request_context.lifespan_context
    return app_ctx.fetcher
```

**Step 2: Write main.py**

```python
# src/ya_metrics_mcp/servers/main.py
"""FastMCP server setup with lifespan, healthz, and tool filtering."""
from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from ya_metrics_mcp.metrika.client import YaMetrikaClient
from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.metrika.fetchers.fetcher import YaMetrikaFetcher
from ya_metrics_mcp.servers.context import MainAppContext

logger = logging.getLogger("ya-metrics")


@asynccontextmanager
async def main_lifespan(app: FastMCP):  # type: ignore[type-arg]
    """Initialize and clean up the Yandex Metrika client on server start/stop."""
    config = YaMetrikaConfig.from_env()
    logger.info(
        "Starting ya-metrics-mcp, read_only=%s, enabled_tools=%s",
        config.read_only,
        config.enabled_tools,
    )
    client = YaMetrikaClient(config)
    fetcher = YaMetrikaFetcher(client)
    try:
        yield MainAppContext(fetcher=fetcher, config=config)
    finally:
        await client.close()
        logger.info("ya-metrics-mcp shutdown complete")


mcp = FastMCP(
    name="ya-metrics-mcp",
    instructions="MCP server for Yandex Metrika analytics. Provides access to traffic, content, demographics, performance, and e-commerce data.",
    lifespan=main_lifespan,
)
```

**Step 3: Write a smoke test for the server**

```python
# tests/unit/test_server.py
from ya_metrics_mcp.servers.main import mcp


def test_server_has_name():
    assert mcp.name == "ya-metrics-mcp"
```

**Step 4: Run tests**

```bash
uv run pytest tests/unit/test_server.py -v
```

Expected: 1 PASSED

**Step 5: Commit**

```bash
git add src/ya_metrics_mcp/servers/ tests/unit/test_server.py
git commit -m "feat: add FastMCP server with lifespan and context"
```

---

## Task 16: Tool Registrations (all 25 tools)

**Files:**
- Create: `src/ya_metrics_mcp/servers/tools.py`

This file registers all 25 tools via `@mcp.tool()`. Each tool:
1. Uses `Annotated[type, Field(description="...")]` for parameters
2. Calls `get_metrika_fetcher(ctx)` to get the fetcher
3. Delegates to the corresponding fetcher method
4. Is tagged `{"metrika", "read"}`

```python
# src/ya_metrics_mcp/servers/tools.py
"""MCP tool registrations for Yandex Metrika analytics."""
from __future__ import annotations

from typing import Annotated

from fastmcp import Context
from pydantic import Field

from ya_metrics_mcp.servers.dependencies import get_metrika_fetcher
from ya_metrics_mcp.servers.main import mcp

# ─── Account & Basic Analytics ───────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def get_account_info(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Yandex Metrika counter ID")],
) -> str:
    """Get basic account and counter information from Yandex Metrika."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_account_info(counter_id)


@mcp.tool(tags={"metrika", "read"})
async def get_visits(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Yandex Metrika counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Retrieve visit statistics with optional date range (defaults to last 7 days)."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_visits(counter_id, date_from, date_to)


# ─── Traffic Sources ─────────────────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def sources_summary(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
) -> str:
    """Get comprehensive traffic sources overview and summary report."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.sources_summary(counter_id)


@mcp.tool(tags={"metrika", "read"})
async def sources_search_phrases(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
) -> str:
    """Retrieve search phrases and browser information from traffic sources."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.sources_search_phrases(counter_id)


@mcp.tool(tags={"metrika", "read"})
async def get_traffic_sources_types(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
) -> str:
    """Analyze different types of traffic sources (organic, direct, referral)."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_traffic_sources_types(counter_id)


@mcp.tool(tags={"metrika", "read"})
async def get_search_engines_data(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    exclude_robots: Annotated[bool, Field(description="Exclude robot traffic")] = False,
    new_users_only: Annotated[bool, Field(description="Filter to new users only")] = False,
) -> str:
    """Get sessions and users data from search engines with optional filters."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_search_engines_data(counter_id, exclude_robots, new_users_only)


@mcp.tool(tags={"metrika", "read"})
async def get_new_users_by_source(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Identify which traffic sources are most effective in acquiring new users."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_new_users_by_source(counter_id, date_from, date_to)


# ─── Content Analytics ────────────────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def get_content_analytics_sources(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Get sources that drive users to website articles."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_content_analytics_sources(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_content_analytics_categories(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Retrieve overall statistics by content category."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_content_analytics_categories(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_content_analytics_authors(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Get statistics on article authors performance."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_content_analytics_authors(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_content_analytics_topics(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Analyze performance by article topics."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_content_analytics_topics(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_content_analytics_articles(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Get detailed report on article views grouped by article."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_content_analytics_articles(counter_id, date_from, date_to)


# ─── User Behavior & Demographics ─────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def get_user_demographics(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Access user demographics and engagement by device category."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_user_demographics(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_device_analysis(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Analyze user behavior by browser and operating system."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_device_analysis(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_mobile_vs_desktop(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Compare traffic and engagement metrics between mobile and desktop users."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_mobile_vs_desktop(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_page_depth_analysis(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    min_pages: Annotated[int, Field(description="Minimum page views threshold", ge=1)] = 5,
) -> str:
    """Get sessions where users viewed more than the specified number of pages."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_page_depth_analysis(counter_id, min_pages)


# ─── Geographic ───────────────────────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def get_regional_data(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    cities: Annotated[list[str] | None, Field(description="City names to filter by")] = None,
) -> str:
    """Get sessions and users data for specific regions/cities."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_regional_data(counter_id, cities)


@mcp.tool(tags={"metrika", "read"})
async def get_geographical_organic_traffic(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Analyze geographical distribution of organic traffic."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_geographical_organic_traffic(counter_id, date_from, date_to)


# ─── Performance & Conversion ─────────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def get_page_performance(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Get page performance and bounce rate by URL path."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_page_performance(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_goals_conversion(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    goal_ids: Annotated[list[int], Field(description="List of goal IDs to track")],
) -> str:
    """Track conversion rates for specified goals."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_goals_conversion(counter_id, goal_ids)


@mcp.tool(tags={"metrika", "read"})
async def get_organic_search_performance(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Analyze organic search performance by search engine and query."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_organic_search_performance(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_conversion_rate_by_source_and_landing(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    goal_id: Annotated[int, Field(description="Goal ID to track conversion for")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Get conversion rate analysis by traffic source and landing page."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_conversion_rate_by_source_and_landing(counter_id, goal_id, date_from, date_to)


# ─── Advanced Analytics ───────────────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def get_ecommerce_performance(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    currency: Annotated[str, Field(description="Currency code, e.g. RUB, USD")] = "RUB",
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Get e-commerce performance by product category and region."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_ecommerce_performance(counter_id, currency, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_data_by_time(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    metrics: Annotated[list[str], Field(description="Metric names (max 20), e.g. ['ym:s:visits']")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
    dimensions: Annotated[list[str] | None, Field(description="Dimension names (max 10)")] = None,
    group: Annotated[str, Field(description="Time grouping: day|week|month|quarter|year")] = "day",
    top_keys: Annotated[int, Field(description="Number of top results (1-30)", ge=1, le=30)] = 7,
    timezone: Annotated[str | None, Field(description="Timezone offset, e.g. +03:00")] = None,
) -> str:
    """Get data for specific time periods grouped by day/week/month/quarter/year."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_data_by_time(counter_id, metrics, date_from, date_to, dimensions, group, top_keys, timezone)


@mcp.tool(tags={"metrika", "read"})
async def get_yandex_direct_experiment(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    experiment_id: Annotated[int, Field(description="Yandex Direct experiment ID")],
) -> str:
    """Get bounce rate for specific Yandex Direct A/B experiments."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_yandex_direct_experiment(counter_id, experiment_id)


@mcp.tool(tags={"metrika", "read"})
async def get_browsers_report(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
) -> str:
    """Get browsers report without accounting for browser version."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_browsers_report(counter_id)
```

**Run smoke test:**

```bash
uv run python -c "from ya_metrics_mcp.servers.tools import *; print('25 tools loaded OK')"
```

Expected: `25 tools loaded OK`

**Commit:**

```bash
git add src/ya_metrics_mcp/servers/tools.py
git commit -m "feat: register all 25 MCP tools"
```

---

## Task 17: CLI Entry Point

**Files:**
- Modify: `src/ya_metrics_mcp/__init__.py`

```python
# src/ya_metrics_mcp/__init__.py
"""ya-metrics-mcp: MCP server for Yandex Metrika analytics."""
from __future__ import annotations

import logging

import click
from dotenv import load_dotenv

from ya_metrics_mcp.utils.lifecycle import setup_signal_handlers
from ya_metrics_mcp.utils.logging import setup_logging

logger = logging.getLogger("ya-metrics")


@click.command()
@click.option("--transport", default="stdio", type=click.Choice(["stdio", "streamable-http", "sse"]), help="Transport mode")
@click.option("--port", default=8000, type=int, help="HTTP port (HTTP transport only)")
@click.option("--host", default="0.0.0.0", help="HTTP host (HTTP transport only)")
@click.option("--env-file", default=None, help="Path to .env file")
@click.option("-v", "--verbose", count=True, help="Verbose logging (-v INFO, -vv DEBUG)")
def main(transport: str, port: int, host: str, env_file: str | None, verbose: int) -> None:
    """ya-metrics-mcp: Yandex Metrika MCP server."""
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    setup_logging(verbose)
    setup_signal_handlers()

    # Import tools to register them with the mcp instance
    import ya_metrics_mcp.servers.tools  # noqa: F401
    from ya_metrics_mcp.servers.main import mcp

    logger.info("Starting ya-metrics-mcp (transport=%s)", transport)

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport=transport, host=host, port=port)


if __name__ == "__main__":
    main()
```

**Test the CLI help:**

```bash
uv run ya-metrics-mcp --help
```

Expected: shows help text with transport/port/host options

**Commit:**

```bash
git add src/ya_metrics_mcp/__init__.py
git commit -m "feat: add Click CLI entry point with transport/port/logging options"
```

---

## Task 18: Final Packaging & Config Files

**Files:**
- Create: `.env.example`
- Create: `README.md`
- Create: `Dockerfile`

**Step 1: Create .env.example**

```bash
# .env.example
# Required: Your Yandex Metrika OAuth token
# Get one at: https://oauth.yandex.ru/client/new
YANDEX_API_KEY=y0_AgAAAA...

# Optional configuration
YANDEX_TIMEOUT=30
YANDEX_RETRIES=3
YANDEX_RETRY_DELAY=1.0

# Server features
READ_ONLY_MODE=false
# ENABLED_TOOLS=get_visits,get_account_info
```

**Step 2: Run all tests to confirm green**

```bash
uv run pytest -v
```

Expected: all tests PASSED

**Step 3: Test end-to-end invocation**

```bash
YANDEX_API_KEY=test uv run ya-metrics-mcp --help
```

**Step 4: Final commit**

```bash
git add .env.example README.md
git commit -m "chore: add .env.example and README"
git tag v0.1.0
```

---

## Summary

| Task | Component | Tests |
|---|---|---|
| 1 | Project scaffold | — |
| 2 | Exceptions | ✓ |
| 3 | YaMetrikaConfig | ✓ |
| 4 | YaMetrikaClient | ✓ |
| 5 | Utils (logging, date, tools, decorators) | ✓ |
| 6 | BaseFetcher | ✓ |
| 7 | TrafficMixin (7 tools) | ✓ |
| 8 | ContentMixin (5 tools) | ✓ |
| 9 | DemographicsMixin (4 tools) | ✓ |
| 10 | GeographicMixin (2 tools) | ✓ |
| 11 | PerformanceMixin (4 tools) | ✓ |
| 12 | AdvancedMixin (4 tools) | ✓ |
| 13 | YaMetrikaFetcher composite | ✓ |
| 14 | Server context | — |
| 15 | FastMCP server + lifespan | ✓ |
| 16 | 25 tool registrations | smoke |
| 17 | CLI entry point | smoke |
| 18 | Packaging + config files | — |

**Total: 25 tools, full test coverage of all business logic, stdio + HTTP transport, uv + PyPI ready.**
