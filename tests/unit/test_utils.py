import pytest
from ya_metrics_mcp.utils.logging import mask_sensitive
from ya_metrics_mcp.utils.date import validate_date, default_date_range
from ya_metrics_mcp.utils.tools import filter_tools
from ya_metrics_mcp.metrika.config import YaMetrikaConfig


def test_mask_sensitive_keeps_last_4():
    assert mask_sensitive("y0_AgAAAAlong_token_value") == "****alue"


def test_mask_sensitive_short_token():
    assert mask_sensitive("abc") == "****"


def test_validate_date_valid():
    assert validate_date("2024-01-15") == "2024-01-15"


def test_validate_date_invalid():
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        validate_date("15-01-2024")


def test_validate_date_none_returns_none():
    assert validate_date(None) is None


def test_default_date_range():
    date_from, date_to = default_date_range(days=7)
    assert date_to > date_from
    assert len(date_from) == 10  # YYYY-MM-DD


def test_filter_tools_no_filter():
    config = YaMetrikaConfig(api_key="tok")
    tools = ["get_visits", "get_account_info", "sources_summary"]
    assert filter_tools(tools, config) == tools


def test_filter_tools_enabled_list():
    config = YaMetrikaConfig(api_key="tok", enabled_tools=["get_visits"])
    tools = ["get_visits", "get_account_info"]
    assert filter_tools(tools, config) == ["get_visits"]


def test_filter_tools_read_only_removes_write():
    config = YaMetrikaConfig(api_key="tok", read_only=True)
    read_tools = [("get_visits", {"read"}), ("delete_counter", {"write"})]
    result = filter_tools([t for t, _ in read_tools], config,
                          tool_tags={t: tags for t, tags in read_tools})
    assert result == ["get_visits"]
