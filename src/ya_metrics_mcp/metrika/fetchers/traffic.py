"""Traffic and sources analytics fetcher mixin."""
from __future__ import annotations

from ya_metrics_mcp.utils.date import default_date_range, validate_date
from ya_metrics_mcp.utils.decorators import handle_api_errors


class TrafficMixin:
    """Mixin for traffic sources and basic visit analytics.

    Requires self.client (YaMetrikaClient) and self.format_response() from BaseFetcher.
    """

    @handle_api_errors()
    async def get_account_info(self, counter_id: str) -> str:
        data = await self.client.get(f"/management/v1/counter/{counter_id}", {})
        return self.format_response(data)

    @handle_api_errors()
    async def get_visits(
        self,
        counter_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        if date_from is None and date_to is None:
            date_from, date_to = default_date_range(days=7)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "metrics": "ym:s:visits",
                "date1": date_from,
                "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def sources_summary(self, counter_id: str) -> str:
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "sources_summary", "id": counter_id},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def sources_search_phrases(self, counter_id: str) -> str:
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "sources_search_phrases", "id": counter_id},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_traffic_sources_types(self, counter_id: str) -> str:
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:lastTrafficSource",
                "metrics": "ym:s:visits,ym:s:users",
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_search_engines_data(
        self,
        counter_id: str,
        exclude_robots: bool = False,
        new_users_only: bool = False,
    ) -> str:
        filters = ["ym:s:trafficSource=='organic'"]
        if exclude_robots:
            filters.append("ym:s:isRobot=='No'")
        if new_users_only:
            filters.append("ym:s:isNewUser=='Yes'")
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:searchEngine",
                "metrics": "ym:s:visits,ym:s:users",
                "filters": " AND ".join(filters),
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def list_goals(self, counter_id: str) -> str:
        data = await self.client.get(
            f"/management/v1/counter/{counter_id}/goals",
            {},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def list_counters(
        self,
        search: str | None = None,
        per_page: int = 100,
    ) -> str:
        data = await self.client.get(
            "/management/v1/counters",
            {
                "per_page": per_page,
                "search": search,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_new_users_by_source(
        self,
        counter_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        if date_from is None and date_to is None:
            date_from, date_to = default_date_range(days=30)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:lastTrafficSource",
                "metrics": "ym:s:newUsers",
                "date1": date_from,
                "date2": date_to,
            },
        )
        return self.format_response(data)
