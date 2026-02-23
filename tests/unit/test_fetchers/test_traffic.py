import re
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
        url=re.compile(r".*stat/v1/data.*"),
        json={"data": [{"dimensions": [], "metrics": [100]}]},
    )
    result = await fetcher.get_visits("12345")
    assert "data" in result


@pytest.mark.asyncio
async def test_get_visits_raises_on_invalid_date(fetcher):
    from ya_metrics_mcp.exceptions import MCPYaMetrikaError
    with pytest.raises((ValueError, MCPYaMetrikaError)):
        await fetcher.get_visits("12345", date_from="not-a-date")


@pytest.mark.asyncio
async def test_list_counters(httpx_mock, fetcher):
    httpx_mock.add_response(
        url=re.compile(r".*management/v1/counters.*"),
        json={
            "counters": [
                {"id": 12345, "name": "My Website", "site": "example.com"},
                {"id": 67890, "name": "My Blog", "site": "blog.example.com"},
            ]
        },
    )
    result = await fetcher.list_counters()
    assert "12345" in result or "My Website" in result
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_list_counters_with_filter(httpx_mock, fetcher):
    httpx_mock.add_response(
        url=re.compile(r".*management/v1/counters.*"),
        json={"counters": [{"id": 12345, "name": "My Website"}]},
    )
    result = await fetcher.list_counters(search="My Website")
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_list_goals(httpx_mock, fetcher):
    httpx_mock.add_response(
        url="https://api-metrika.yandex.net/management/v1/counter/12345/goals",
        json={
            "goals": [
                {"id": 1001, "name": "Purchase", "type": "action"},
                {"id": 1002, "name": "Sign Up", "type": "form"},
            ]
        },
    )
    result = await fetcher.list_goals("12345")
    assert "1001" in result or "Purchase" in result
    assert isinstance(result, str)
