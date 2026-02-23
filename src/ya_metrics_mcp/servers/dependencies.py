"""Dependency injection helpers for tool handlers."""
from fastmcp import Context

from ya_metrics_mcp.metrika.fetchers.fetcher import YaMetrikaFetcher
from ya_metrics_mcp.servers.context import MainAppContext


async def get_metrika_fetcher(ctx: Context) -> YaMetrikaFetcher:
    """Retrieve the shared YaMetrikaFetcher from lifespan context."""
    app_ctx: MainAppContext = ctx.request_context.lifespan_context
    return app_ctx.fetcher
