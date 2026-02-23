import re
import pytest
from ya_metrics_mcp.metrika.fetchers.advanced import AdvancedMixin
from ya_metrics_mcp.metrika.fetchers.base import BaseFetcher
from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.metrika.client import YaMetrikaClient


class AdvFetcher(AdvancedMixin, BaseFetcher):
    pass


@pytest.fixture
def fetcher():
    return AdvFetcher(YaMetrikaClient(YaMetrikaConfig(api_key="tok")))


@pytest.mark.asyncio
async def test_get_browsers_report(httpx_mock, fetcher):
    httpx_mock.add_response(url=re.compile(r".*stat/v1/data.*"), json={"data": []})
    result = await fetcher.get_browsers_report("12345")
    assert isinstance(result, str)
