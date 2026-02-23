"""MCP tool registrations for Yandex Metrika analytics."""
from typing import Annotated

from fastmcp import Context
from pydantic import Field

from ya_metrics_mcp.servers.dependencies import get_metrika_fetcher
from ya_metrics_mcp.servers.main import mcp

# ─── Account & Basic Analytics ───────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def get_account_info(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Yandex Metrika counter ID")],
) -> str:
    """Get basic account and counter information from Yandex Metrika."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_account_info(counter_id)


@mcp.tool(tags={"metrika", "read"})
async def get_visits(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Yandex Metrika counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Retrieve visit statistics with optional date range (defaults to last 7 days)."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_visits(counter_id, date_from, date_to)


# ─── Traffic Sources ─────────────────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def sources_summary(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
) -> str:
    """Get comprehensive traffic sources overview and summary report."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.sources_summary(counter_id)


@mcp.tool(tags={"metrika", "read"})
async def sources_search_phrases(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
) -> str:
    """Retrieve search phrases and browser information from traffic sources."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.sources_search_phrases(counter_id)


@mcp.tool(tags={"metrika", "read"})
async def get_traffic_sources_types(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
) -> str:
    """Analyze different types of traffic sources (organic, direct, referral)."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_traffic_sources_types(counter_id)


@mcp.tool(tags={"metrika", "read"})
async def get_search_engines_data(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    exclude_robots: Annotated[bool, Field(description="Exclude robot traffic")] = False,
    new_users_only: Annotated[bool, Field(description="Filter to new users only")] = False,
) -> str:
    """Get sessions and users data from search engines with optional filters."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_search_engines_data(counter_id, exclude_robots, new_users_only)


@mcp.tool(tags={"metrika", "read"})
async def get_new_users_by_source(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Identify which traffic sources are most effective in acquiring new users."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_new_users_by_source(counter_id, date_from, date_to)


# ─── Content Analytics ────────────────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def get_content_analytics_sources(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Get sources that drive users to website articles."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_content_analytics_sources(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_content_analytics_categories(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Retrieve overall statistics by content category."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_content_analytics_categories(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_content_analytics_authors(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Get statistics on article authors performance."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_content_analytics_authors(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_content_analytics_topics(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Analyze performance by article topics."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_content_analytics_topics(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_content_analytics_articles(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Get detailed report on article views grouped by article."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_content_analytics_articles(counter_id, date_from, date_to)


# ─── User Behavior & Demographics ─────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def get_user_demographics(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Access user demographics and engagement by device category."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_user_demographics(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_device_analysis(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Analyze user behavior by browser and operating system."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_device_analysis(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_mobile_vs_desktop(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Compare traffic and engagement metrics between mobile and desktop users."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_mobile_vs_desktop(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_page_depth_analysis(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    min_pages: Annotated[int, Field(description="Minimum page views threshold", ge=1)] = 5,
) -> str:
    """Get sessions where users viewed more than the specified number of pages."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_page_depth_analysis(counter_id, min_pages)


# ─── Geographic ───────────────────────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def get_regional_data(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    cities: Annotated[list[str] | None, Field(description="City names to filter by")] = None,
) -> str:
    """Get sessions and users data for specific regions/cities."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_regional_data(counter_id, cities)


@mcp.tool(tags={"metrika", "read"})
async def get_geographical_organic_traffic(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Analyze geographical distribution of organic traffic."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_geographical_organic_traffic(counter_id, date_from, date_to)


# ─── Performance & Conversion ─────────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def get_page_performance(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Get page performance and bounce rate by URL path."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_page_performance(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_goals_conversion(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    goal_ids: Annotated[list[int], Field(description="List of goal IDs to track")],
) -> str:
    """Track conversion rates for specified goals."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_goals_conversion(counter_id, goal_ids)


@mcp.tool(tags={"metrika", "read"})
async def get_organic_search_performance(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Analyze organic search performance by search engine and query."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_organic_search_performance(counter_id, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_conversion_rate_by_source_and_landing(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    goal_id: Annotated[int, Field(description="Goal ID to track conversion for")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Get conversion rate analysis by traffic source and landing page."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_conversion_rate_by_source_and_landing(counter_id, goal_id, date_from, date_to)


# ─── Advanced Analytics ───────────────────────────────────────────────────────

@mcp.tool(tags={"metrika", "read"})
async def get_ecommerce_performance(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    currency: Annotated[str, Field(description="Currency code, e.g. RUB, USD")] = "RUB",
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
) -> str:
    """Get e-commerce performance by product category and region."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_ecommerce_performance(counter_id, currency, date_from, date_to)


@mcp.tool(tags={"metrika", "read"})
async def get_data_by_time(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    metrics: Annotated[list[str], Field(description="Metric names (max 20), e.g. ['ym:s:visits']")],
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
    dimensions: Annotated[list[str] | None, Field(description="Dimension names (max 10)")] = None,
    group: Annotated[str, Field(description="Time grouping: day|week|month|quarter|year")] = "day",
    top_keys: Annotated[int, Field(description="Number of top results (1-30)", ge=1, le=30)] = 7,
    timezone: Annotated[str | None, Field(description="Timezone offset, e.g. +03:00")] = None,
) -> str:
    """Get data for specific time periods grouped by day/week/month/quarter/year."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_data_by_time(counter_id, metrics, date_from, date_to, dimensions, group, top_keys, timezone)


@mcp.tool(tags={"metrika", "read"})
async def get_yandex_direct_experiment(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
    experiment_id: Annotated[int, Field(description="Yandex Direct experiment ID")],
) -> str:
    """Get bounce rate for specific Yandex Direct A/B experiments."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_yandex_direct_experiment(counter_id, experiment_id)


@mcp.tool(tags={"metrika", "read"})
async def get_browsers_report(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Counter ID")],
) -> str:
    """Get browsers report without accounting for browser version."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_browsers_report(counter_id)


@mcp.tool(tags={"metrika", "read"})
async def get_drilldown(
    ctx: Context,
    counter_id: Annotated[str, Field(description="Yandex Metrika counter ID")],
    dimensions: Annotated[str, Field(description="Comma-separated dimension path for drill-down, e.g. 'ym:s:regionCountry,ym:s:regionCity'")],
    metrics: Annotated[list[str], Field(description="Metric names, e.g. ['ym:s:visits', 'ym:s:users']")],
    parent_id: Annotated[str | None, Field(description="Parent node ID to drill into (omit for root level)")] = None,
    date_from: Annotated[str | None, Field(description="Start date YYYY-MM-DD")] = None,
    date_to: Annotated[str | None, Field(description="End date YYYY-MM-DD")] = None,
    limit: Annotated[int | None, Field(description="Maximum rows to return")] = None,
) -> str:
    """Generate a single branch of a hierarchical tree-view report (drill-down)."""
    fetcher = await get_metrika_fetcher(ctx)
    return await fetcher.get_drilldown(counter_id, dimensions, metrics, parent_id, date_from, date_to, limit)
