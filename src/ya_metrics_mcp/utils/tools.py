"""Tool filtering logic for READ_ONLY_MODE and ENABLED_TOOLS."""
from __future__ import annotations

from ya_metrics_mcp.metrika.config import YaMetrikaConfig


def filter_tools(
    tool_names: list[str],
    config: YaMetrikaConfig,
    tool_tags: dict[str, set[str]] | None = None,
) -> list[str]:
    """Filter tool names based on config restrictions.

    Args:
        tool_names: All available tool names.
        config: Server configuration.
        tool_tags: Optional mapping of tool_name → set of tags (e.g. {"read"}, {"write"}).

    Returns:
        Filtered list of tool names.
    """
    result = tool_names

    if config.enabled_tools is not None:
        result = [t for t in result if t in config.enabled_tools]

    if config.read_only and tool_tags:
        result = [t for t in result if "write" not in tool_tags.get(t, set())]

    return result
