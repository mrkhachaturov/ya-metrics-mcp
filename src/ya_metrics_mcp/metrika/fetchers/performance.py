"""Performance and conversion analytics fetcher mixin."""
from __future__ import annotations

from ya_metrics_mcp.utils.date import validate_date
from ya_metrics_mcp.utils.decorators import handle_api_errors


class PerformanceMixin:
    @handle_api_errors()
    async def get_page_performance(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:URLPath",
                "metrics": "ym:s:pageviews,ym:s:bounceRate,ym:s:avgVisitDurationSeconds",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_goals_conversion(
        self, counter_id: str, goal_ids: list[int]
    ) -> str:
        goal_metrics = ",".join(
            f"ym:s:goal{gid}conversionRate" for gid in goal_ids
        )
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "metrics": f"ym:s:users,{goal_metrics}",
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_organic_search_performance(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:searchEngine,ym:s:searchPhrase",
                "metrics": "ym:s:visits,ym:s:users,ym:s:pageviews",
                "filters": "ym:s:trafficSource=='organic'",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_conversion_rate_by_source_and_landing(
        self,
        counter_id: str,
        goal_id: int,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:trafficSource,ym:s:landingPage",
                "metrics": f"ym:s:visits,ym:s:goal{goal_id}conversionRate",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)
