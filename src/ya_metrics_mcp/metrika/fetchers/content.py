"""Content (publishers) analytics fetcher mixin."""
from __future__ import annotations

from ya_metrics_mcp.utils.date import validate_date
from ya_metrics_mcp.utils.decorators import handle_api_errors


class ContentMixin:
    @handle_api_errors()
    async def get_content_analytics_sources(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "publishers_sources", "id": counter_id, "date1": date_from, "date2": date_to},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_content_analytics_categories(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "publishers_rubrics", "id": counter_id, "date1": date_from, "date2": date_to},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_content_analytics_authors(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "publishers_authors", "id": counter_id, "date1": date_from, "date2": date_to},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_content_analytics_topics(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {"preset": "publishers_thematics", "id": counter_id, "date1": date_from, "date2": date_to},
        )
        return self.format_response(data)

    @handle_api_errors()
    async def get_content_analytics_articles(
        self, counter_id: str, date_from: str | None = None, date_to: str | None = None
    ) -> str:
        date_from = validate_date(date_from)
        date_to = validate_date(date_to)
        data = await self.client.get(
            "/stat/v1/data",
            {
                "ids": counter_id,
                "dimensions": "ym:s:publisherArticle",
                "metrics": "ym:s:publisherviews",
                "filters": "ym:s:publisherArticle!n",
                "sort": "-ym:s:publisherviews",
                "date1": date_from,
                "date2": date_to,
            },
        )
        return self.format_response(data)
