# ya-metrics-mcp

MCP server for Yandex Metrika analytics. FastMCP server with mixin-based domain fetchers exposing 31 tools via stdio/HTTP transports.

## Commands

```bash
# Install deps (including dev)
uv sync --extra dev

# Run tests
uv run pytest

# Run tests with output
uv run pytest -v

# Lint
uv run ruff check src/

# Type check
uv run mypy src/

# Run the server (stdio)
YANDEX_API_KEY=your_token uv run ya-metrics-mcp

# Run with HTTP transport
YANDEX_API_KEY=your_token uv run ya-metrics-mcp --transport streamable-http --port 8000

# CLI help
uv run ya-metrics-mcp --help
```

## Architecture

```
src/ya_metrics_mcp/
├── __init__.py              # Click CLI entry point (main())
├── exceptions.py            # MCPYaMetrikaError, AuthenticationError
├── metrika/
│   ├── config.py            # YaMetrikaConfig — loaded from env vars
│   ├── client.py            # YaMetrikaClient — async httpx with retry
│   └── fetchers/
│       ├── base.py          # BaseFetcher: holds client, format_response()
│       ├── traffic.py       # TrafficMixin (9 methods: +list_counters, +list_goals)
│       ├── content.py       # ContentMixin (5 methods)
│       ├── demographics.py  # DemographicsMixin (4 methods)
│       ├── geographic.py    # GeographicMixin (2 methods)
│       ├── performance.py   # PerformanceMixin (4 methods)
│       ├── advanced.py      # AdvancedMixin (7 methods: +get_drilldown, +compare_segments, +compare_segments_drilldown)
│       └── fetcher.py       # YaMetrikaFetcher — all mixins combined
├── servers/
│   ├── main.py              # FastMCP instance + main_lifespan()
│   ├── context.py           # MainAppContext dataclass
│   ├── dependencies.py      # get_metrika_fetcher(ctx) DI helper
│   └── tools.py             # @mcp.tool() registrations (all 31 tools)
└── utils/
    ├── date.py              # validate_date(), default_date_range()
    ├── decorators.py        # @handle_api_errors() — wraps exceptions
    ├── logging.py           # setup_logging(), mask_sensitive()
    ├── lifecycle.py         # setup_signal_handlers()
    └── tools.py             # filter_tools() — READ_ONLY_MODE / ENABLED_TOOLS
```

## Key Patterns

**Adding a new tool** — three steps:
1. Add a method to the appropriate mixin in `src/ya_metrics_mcp/metrika/fetchers/`
2. Decorate it with `@handle_api_errors()`
3. Register it in `src/ya_metrics_mcp/servers/tools.py` with `@mcp.tool(tags={"metrika", "read"})`

**Config flows via lifespan**: `YaMetrikaConfig.from_env()` → `YaMetrikaClient` → `YaMetrikaFetcher` → `MainAppContext` yielded by `main_lifespan`, injected into tools via `get_metrika_fetcher(ctx)`.

## Gotchas

**`tools.py` must NOT use `from __future__ import annotations`** — FastMCP/Pydantic evaluate `Annotated[...]` type hints at decoration time. Deferred string annotations break this with `NameError: name 'Annotated' is not defined`.

**`pytest-httpx` ≥0.36 API change** — use `url=re.compile(r"...")` not `url__regex=r"..."`:
```python
# correct
httpx_mock.add_response(url=re.compile(r".*stat/v1/data.*"), json={"data": []})
```

**`TestFetcher` naming** — pytest tries to collect classes named `Test*` as test suites. Name test helper classes `XxxFetcher` (e.g. `TrafficFetcher`) to avoid the collection warning.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `YANDEX_API_KEY` | ✓ | — | OAuth token from oauth.yandex.ru |
| `YANDEX_TIMEOUT` | | `30` | Request timeout (seconds) |
| `YANDEX_RETRIES` | | `3` | Retry attempts for 5xx errors |
| `YANDEX_RETRY_DELAY` | | `1.0` | Base retry delay (seconds) |
| `READ_ONLY_MODE` | | `false` | Block write-tagged tools |
| `ENABLED_TOOLS` | | all | Comma-separated allowlist |

## Testing

Tests use `pytest-asyncio` (`asyncio_mode = "auto"`) and `pytest-httpx` for HTTP mocking.

```bash
uv run pytest tests/unit/test_client.py    # HTTP client + retry logic
uv run pytest tests/unit/test_fetchers/    # All 6 domain mixins + composite
uv run pytest tests/unit/test_server.py   # FastMCP server smoke test
```
