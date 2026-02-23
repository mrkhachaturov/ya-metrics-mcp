from ya_metrics_mcp.metrika.fetchers.fetcher import YaMetrikaFetcher
from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.metrika.client import YaMetrikaClient


def test_fetcher_has_all_mixin_methods():
    config = YaMetrikaConfig(api_key="tok")
    client = YaMetrikaClient(config)
    fetcher = YaMetrikaFetcher(client)

    # spot-check one method from each mixin
    assert hasattr(fetcher, "get_visits")                       # TrafficMixin
    assert hasattr(fetcher, "get_content_analytics_articles")   # ContentMixin
    assert hasattr(fetcher, "get_user_demographics")            # DemographicsMixin
    assert hasattr(fetcher, "get_regional_data")                # GeographicMixin
    assert hasattr(fetcher, "get_goals_conversion")             # PerformanceMixin
    assert hasattr(fetcher, "get_data_by_time")                 # AdvancedMixin
