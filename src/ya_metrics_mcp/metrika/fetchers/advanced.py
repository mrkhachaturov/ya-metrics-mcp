"""Advanced and specialized analytics fetcher mixin."""
from __future__ import annotations

from ya_metrics_mcp.utils.date import validate_date
from ya_metrics_mcp.utils.decorators import handle_api_errors

_VALID_GROUPS = {"day", "week", "month", "quarter", "year"}


class AdvancedMixin:
    @handle_api_errors()
    async def get_ecommerce_performance(
        self,
        counter_id: str,
        currency: str = "RUB",
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> str:
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:productCategory,ym:s:regionCountry,ym:s:regionCity",
                "metrics": f"ym:s:ecommercePurchases,ym:s:ecommerce{currency}ConvertedRevenue",
                "date1": date_from, "date2": date_to,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_data_by_time(
        self,
        counter_id: str,
        metrics: list[str],
        date_from: str | None = None,
        date_to: str | None = None,
        dimensions: list[str] | None = None,
        group: str = "day",
        top_keys: int = 7,
        timezone: str | None = None,
    ) -> str:
        if len(metrics) > 20:
            raise ValueError("Maximum 20 metrics allowed")
        if dimensions and len(dimensions) > 10:
            raise ValueError("Maximum 10 dimensions allowed")
        if group not in _VALID_GROUPS:
            raise ValueError(f"group must be one of {_VALID_GROUPS}")
        if not 1 <= top_keys <= 30:
            raise ValueError("top_keys must be between 1 and 30")
        date_from, date_to = validate_date(date_from), validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data/bytime",
            {
                "ids": counter_id,
                "metrics": ",".join(metrics),
                "dimensions": ",".join(dimensions) if dimensions else None,
                "group": group,
                "top_keys": top_keys,
                "date1": date_from,
                "date2": date_to,
                "timezone": timezone,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_yandex_direct_experiment(
        self, counter_id: str, experiment_id: int
    ) -> str:
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": f"ym:s:experimentAB{experiment_id}",
                "metrics": "ym:s:bounceRate",
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_drilldown(
        self,
        counter_id: str,
        dimensions: str,
        metrics: list[str],
        parent_id: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        limit: int | None = None,
    ) -> str:
        data = await self.client.get(
            "/stat/v1/data/drilldown",
            {
                "id": counter_id,
                "dimensions": dimensions,
                "metrics": ",".join(metrics),
                "parent_id": parent_id,
                "date1": validate_date(date_from),
                "date2": validate_date(date_to),
                "limit": limit,
            },
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_browsers_report(self, counter_id: str) -> str:
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "tech_platforms", "dimensions": "ym:s:browser", "id": counter_id},
        )
        return self.format_response(data)
