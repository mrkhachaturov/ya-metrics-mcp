"""Request context dataclass for FastMCP lifespan."""
from dataclasses import dataclass

from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.metrika.fetchers.fetcher import YaMetrikaFetcher


@dataclass
class MainAppContext:
    fetcher: YaMetrikaFetcher
    config: YaMetrikaConfig
