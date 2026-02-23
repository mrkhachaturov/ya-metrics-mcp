"""Base fetcher class."""
from __future__ import annotations

import json

from ya_metrics_mcp.metrika.client import YaMetrikaClient


class BaseFetcher:
    def __init__(self, client: YaMetrikaClient) -> None:
        self.client = client

    def format_response(self, data: dict | list) -> str:
        """Format API response as a pretty-printed JSON string."""
        return json.dumps(data, ensure_ascii=False, indent=2)
