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


@pytest.mark.asyncio
async def test_get_drilldown(httpx_mock, fetcher):
    httpx_mock.add_response(
        url=re.compile(r".*stat/v1/data/drilldown.*"),
        json={"data": [{"dimensions": [{"name": "ym:s:regionCity", "value": "Moscow"}], "metrics": ["1500"]}]},
    )
    result = await fetcher.get_drilldown(
        counter_id="12345",
        dimensions="ym:s:regionCountry,ym:s:regionCity",
        metrics=["ym:s:visits"],
        parent_id="225",
    )
    assert "Moscow" in result
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_compare_segments(httpx_mock, fetcher):
    httpx_mock.add_response(
        url=re.compile(r".*stat/v1/data/comparison.*"),
        json={
            "data": [
                {"dimensions": [{"name": "ym:s:trafficSource", "value": "Organic"}], "metrics": ["10000", "5000"]},
                {"dimensions": [{"name": "ym:s:trafficSource", "value": "Direct"}], "metrics": ["8000", "4000"]},
            ]
        },
    )
    result = await fetcher.compare_segments(
        counter_id="12345",
        metrics=["ym:s:visits", "ym:s:users"],
        dimensions="ym:s:trafficSource",
        segment_a_name="Organic",
        segment_a_filter="ym:s:trafficSource=='organic'",
        segment_b_name="Direct",
        segment_b_filter="ym:s:trafficSource=='direct'",
    )
    assert "Organic" in result or "10000" in result
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_get_drilldown_without_parent(httpx_mock, fetcher):
    httpx_mock.add_response(
        url=re.compile(r".*stat/v1/data/drilldown.*"),
        json={"data": []},
    )
    result = await fetcher.get_drilldown(
        counter_id="12345",
        dimensions="ym:s:regionCountry",
        metrics=["ym:s:visits"],
    )
    assert isinstance(result, str)
