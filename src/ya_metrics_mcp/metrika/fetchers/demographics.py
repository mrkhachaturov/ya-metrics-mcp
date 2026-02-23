"""User demographics and device analytics fetcher mixin."""
from __future__ import annotations

from ya_metrics_mcp.utils.date import validate_date
from ya_metrics_mcp.utils.decorators import handle_api_errors


class DemographicsMixin:
    @handle_api_errors()
    async def get_user_demographics(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:ageInterval,ym:s:gender,ym:s:deviceCategory",
                "metrics": "ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:bounceRate,ym:s:avgVisitDurationSeconds",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_device_analysis(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:browser,ym:s:operatingSystem",
                "metrics": "ym:s:visits,ym:s:pageviews,ym:s:bounceRate,ym:s:avgVisitDurationSeconds",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_mobile_vs_desktop(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:deviceCategory",
                "metrics": "ym:s:visits,ym:s:users,ym:s:pageviews,ym:s:bounceRate,ym:s:avgVisitDurationSeconds",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_page_depth_analysis(
        self, counter_id: str, min_pages: int = 5
    ) -> str:
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "metrics": "ym:s:visits,ym:s:users",
                "filters": f"ym:s:pageViews>{min_pages}",
            },
        )
        return self.format_response(data)
