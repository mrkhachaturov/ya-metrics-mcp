"""FastMCP server setup with lifespan and tool filtering."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastmcp import FastMCP

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
