# ya-metrics-mcp Design Document

**Date:** 2026-02-23
**Status:** Approved
**Location:** `/Users/mrkhachaturov/Developer/ya-metrics/ya-metrics-mcp`

---

## Overview

`ya-metrics-mcp` is a Python MCP server providing access to Yandex Metrika analytics via the Model Context Protocol. It is inspired by the architecture of `mcp-atlassian` (clean, modular, production-quality) and supersedes the reference implementation `yandex-metrika-mcp` (TypeScript).

The project launches with all 25 tools from `yandex-metrika-mcp` and is designed to grow.

---

## Reference Projects

| Project | Role | Key takeaways |
|---|---|---|
| `mcp-atlassian` | Architectural inspiration | FastMCP, mixin fetchers, Pydantic config, logging, decorators, lifecycle |
| `yandex-metrika-mcp` | Feature baseline | All 25 tools, Yandex API endpoints, retry logic, error handling |

---

## Technology Stack

| Component | Choice | Reason |
|---|---|---|
| Language | Python 3.10+ | Matches mcp-atlassian, FastMCP ecosystem |
| MCP framework | FastMCP ≥2.13.0 | Decorator-based tools, lifespan context, multi-transport |
| HTTP client | httpx | Async, retry-friendly, used in mcp-atlassian |
| Validation | Pydantic v2 | Config + response models |
| CLI | Click | Entry point, transport/port flags, verbosity |
| HTTP server | uvicorn + starlette | For streamable-HTTP transport |
| Package manager | uv | Lock file, fast installs |
| Distribution | PyPI as `ya-metrics-mcp` | `pip install` + `uvx ya-metrics-mcp` |
| Testing | pytest + pytest-asyncio + pytest-httpx | All API calls mocked |
| Linting | ruff + mypy | Code quality |

---

## Project Structure

```
ya-metrics-mcp/
├── src/ya_metrics_mcp/
│   ├── __init__.py              # Click CLI: --transport, --port, --host, -v/-vv
│   ├── exceptions.py            # MCPYaMetrikaError, AuthenticationError
│   ├── servers/
│   │   ├── main.py              # YaMetricsMCP(FastMCP subclass)
│   │   │                        #   - lifespan context manager
│   │   │                        #   - _list_tools_mcp() with ENABLED_TOOLS + READ_ONLY filtering
│   │   │                        #   - /healthz route
│   │   └── tools.py             # All @mcp.tool(tags={...}) registrations (25 tools)
│   ├── metrika/
│   │   ├── client.py            # YaMetrikaClient (httpx.AsyncClient, retry, timeout)
│   │   ├── config.py            # YaMetrikaConfig.from_env(), is_auth_configured()
│   │   └── fetchers/
│   │       ├── base.py          # BaseFetcher (holds client reference)
│   │       ├── traffic.py       # TrafficMixin   — 7 tools
│   │       ├── content.py       # ContentMixin   — 5 tools
│   │       ├── demographics.py  # DemographicsMixin — 4 tools
│   │       ├── geographic.py    # GeographicMixin   — 2 tools
│   │       ├── performance.py   # PerformanceMixin  — 4 tools
│   │       └── advanced.py      # AdvancedMixin     — 4 tools
│   ├── models/
│   │   └── metrika.py           # Pydantic response models (optional, typed output)
│   └── utils/
│       ├── logging.py           # setup_logging(), mask_sensitive()
│       ├── decorators.py        # @handle_api_errors, @check_write_access
│       ├── tools.py             # filter_tools() helper
│       ├── lifecycle.py         # SIGTERM/SIGINT signal handlers
│       └── date.py              # validate_date(), default_date_range()
├── tests/
│   ├── conftest.py              # fixtures: mock_config, mock_client, mock_fetcher
│   └── unit/
│       ├── test_config.py
│       ├── test_client.py
│       └── test_fetchers/
│           ├── test_traffic.py
│           ├── test_content.py
│           ├── test_demographics.py
│           ├── test_geographic.py
│           ├── test_performance.py
│           └── test_advanced.py
├── docs/
│   └── plans/
│       └── 2026-02-23-ya-metrics-mcp-design.md
├── pyproject.toml
├── uv.lock
├── .env.example
├── README.md
├── Dockerfile
└── smithery.yaml
```

---

## Authentication

Single-token model. No per-request auth extraction.

```env
YANDEX_API_KEY=y0_AgAAA...
```

- All requests use `Authorization: OAuth {token}` header
- Server fails to start with a clear error if `YANDEX_API_KEY` is missing
- No OAuth flow, no keyring — intentionally simple

---

## Configuration

```python
@dataclass
class YaMetrikaConfig:
    api_key: str                              # YANDEX_API_KEY (required)
    timeout: int = 30                         # YANDEX_TIMEOUT (seconds)
    retries: int = 3                          # YANDEX_RETRIES
    retry_delay: float = 1.0                  # YANDEX_RETRY_DELAY (seconds)
    read_only: bool = False                   # READ_ONLY_MODE=true
    enabled_tools: list[str] | None = None    # ENABLED_TOOLS=tool1,tool2

    @classmethod
    def from_env(cls) -> "YaMetrikaConfig": ...

    def is_auth_configured(self) -> bool:
        return bool(self.api_key)
```

---

## Tool Organization

### YaMetrikaFetcher (composite class)

```python
class YaMetrikaFetcher(
    TrafficMixin,
    ContentMixin,
    DemographicsMixin,
    GeographicMixin,
    PerformanceMixin,
    AdvancedMixin,
    BaseFetcher,
):
    pass
```

### Tool → Mixin Mapping

| Mixin | Tools |
|---|---|
| **TrafficMixin** | `get_account_info`, `get_visits`, `sources_summary`, `sources_search_phrases`, `get_traffic_sources_types`, `get_search_engines_data`, `get_new_users_by_source` |
| **ContentMixin** | `get_content_analytics_sources`, `get_content_analytics_categories`, `get_content_analytics_authors`, `get_content_analytics_topics`, `get_content_analytics_articles` |
| **DemographicsMixin** | `get_user_demographics`, `get_device_analysis`, `get_mobile_vs_desktop`, `get_page_depth_analysis` |
| **GeographicMixin** | `get_regional_data`, `get_geographical_organic_traffic` |
| **PerformanceMixin** | `get_page_performance`, `get_goals_conversion`, `get_organic_search_performance`, `get_conversion_rate_by_source_and_landing` |
| **AdvancedMixin** | `get_ecommerce_performance`, `get_data_by_time`, `get_yandex_direct_experiment`, `get_browsers_report` |

All tools are tagged `{"metrika", "read"}`. Future write tools will carry `{"metrika", "write"}`.

---

## Data Flow

### Startup
```
CLI (click)
  → load .env
  → YaMetrikaConfig.from_env()       # validate YANDEX_API_KEY present
  → YaMetrikaClient(config)           # httpx.AsyncClient with retry wrapper
  → YaMetrikaFetcher(client)          # all mixins composed
  → MainAppContext(fetcher, config)    # stored in FastMCP lifespan state
  → YaMetricsMCP.run(transport)       # stdio OR uvicorn HTTP
```

### Per-request (tool call)
```
MCP client → tool call
  → servers/tools.py handler
  → get_metrika_fetcher(ctx)          # retrieve fetcher from lifespan state
  → fetcher.method(params)            # mixin method with @handle_api_errors
  → client.get(url)                   # httpx with Authorization: OAuth header
  → JSON response
  → formatted string returned to MCP client
```

---

## Operational Features (from mcp-atlassian best practices)

### READ_ONLY_MODE
- `READ_ONLY_MODE=true` env var
- `@check_write_access` decorator on all write tools (none at launch, ready for future)
- `_list_tools_mcp()` hides write-tagged tools when read-only is active

### ENABLED_TOOLS
- `ENABLED_TOOLS=get_visits,get_account_info` (comma-separated)
- `_list_tools_mcp()` filters to only listed tools when set
- Useful for restricting a deployment to specific tools

### Health Check
- `/healthz` HTTP route (available in HTTP transport mode)
- Returns `{"status": "ok", "version": "x.x.x"}`
- For Kubernetes liveness probes

### Graceful Shutdown
- `utils/lifecycle.py` registers SIGTERM + SIGINT handlers
- Logs shutdown, closes httpx client cleanly

### Logging
- `utils/logging.py` with severity levels: WARNING (default), INFO (-v), DEBUG (-vv)
- `mask_sensitive(token, keep_chars=4)` for log output
- Logs to stderr (MCP stdio convention)

---

## Error Handling

### Custom Exceptions
```python
class MCPYaMetrikaError(Exception): ...
class AuthenticationError(MCPYaMetrikaError): ...
```

### Decorator Pattern (mirrors mcp-atlassian)
```python
@handle_api_errors(service_name="Yandex Metrika API")
async def get_visits(self, counter_id: str, ...) -> dict:
    ...
# Catches: httpx.HTTPError (401/403/5xx), ValueError, TypeError
# Returns: formatted error message string to MCP client
```

---

## HTTP Client

```python
class YaMetrikaClient:
    BASE_URL = "https://api-metrika.yandex.net"

    def __init__(self, config: YaMetrikaConfig):
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"OAuth {config.api_key}"},
            timeout=config.timeout,
        )
        self.config = config

    async def get(self, path: str, params: dict) -> dict:
        # with retry logic (3 attempts, exponential backoff)
        # retries on: timeout, 500, 502, 503
        ...
```

---

## CLI Usage

```bash
# Install
pip install ya-metrics-mcp
# or: uvx ya-metrics-mcp (zero-install)

# Run (stdio)
ya-metrics-mcp

# Run (HTTP)
ya-metrics-mcp --transport streamable-http --port 8000

# Verbose logging
ya-metrics-mcp -v       # INFO level
ya-metrics-mcp -vv      # DEBUG level
```

### Claude Desktop config
```json
{
  "mcpServers": {
    "ya-metrics": {
      "command": "uvx",
      "args": ["ya-metrics-mcp"],
      "env": {
        "YANDEX_API_KEY": "y0_AgAAA..."
      }
    }
  }
}
```

---

## Testing Strategy

- All Yandex API calls mocked with `pytest-httpx`
- No real API calls in CI
- `conftest.py` provides: `mock_config`, `mock_client`, `mock_fetcher` fixtures
- Unit tests per fetcher mixin, client, and config
- `pytest-asyncio` for async test functions

---

## Yandex Metrika API Endpoints Used

Inherited unchanged from `yandex-metrika-mcp`:

| Endpoint | Purpose |
|---|---|
| `GET /management/v1/counter/{id}` | Account/counter info |
| `GET /stat/v1/data` | All analytics queries (dimensions, metrics, filters, presets) |
| `GET /stat/v1/data/bytime` | Time-grouped analytics |

Auth header: `Authorization: OAuth {token}`

---

## Design Decisions Log

| Decision | Choice | Reason |
|---|---|---|
| Language | Python | Matches mcp-atlassian style preference |
| Transport | stdio + HTTP | Flexibility for local and remote use |
| Auth | Single env var | Sufficient for personal/single-tenant use; simpler |
| Architecture | A + best of C | Clean structure without per-request auth complexity |
| Packaging | uv + PyPI | Standard, supports uvx zero-install |
| Fetcher style | Mixins | Domain separation, easy to extend |
| HTTP client | httpx | Async, used in mcp-atlassian, retry-friendly |
