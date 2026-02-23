"""Geographic analytics fetcher mixin."""
from __future__ import annotations

from ya_metrics_mcp.utils.date import validate_date
from ya_metrics_mcp.utils.decorators import handle_api_errors


class GeographicMixin:
    @handle_api_errors()
    async def get_regional_data(
        self,
        counter_id: str,
        cities: list[str] | None = None,
    ) -> str:
        if cities is None:
            cities = ["Москва", "Санкт-Петербург"]
        city_filter = ",".join(f"'{c}'" for c in cities)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:regionCityName",
                "metrics": "ym:s:visits,ym:s:users",
                "filters": f"ym:s:regionCityName=.({city_filter})",
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_geographical_organic_traffic(
        self,
        counter_id: str,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:regionCountry,ym:s:regionCity",
                "metrics": "ym:s:visits,ym:s:users",
                "filters": "ym:s:trafficSource=='organic'",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)
