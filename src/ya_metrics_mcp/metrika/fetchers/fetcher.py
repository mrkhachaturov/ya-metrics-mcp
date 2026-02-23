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
