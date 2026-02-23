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
