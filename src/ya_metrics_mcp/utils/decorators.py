"""Decorator utilities for error handling and access control."""
from __future__ import annotations

import functools
import logging
from collections.abc import Callable
from typing import Any

from ya_metrics_mcp.exceptions import MCPYaMetrikaError

logger = logging.getLogger("ya-metrics")


def handle_api_errors(service_name: str = "Yandex Metrika API") -> Callable:
    """Decorator that catches API errors and re-raises as MCPYaMetrikaError."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except MCPYaMetrikaError:
                raise
            except Exception as exc:
                logger.error("%s error in %s: %s", service_name, func.__name__, exc)
                raise MCPYaMetrikaError(
                    f"{service_name} error in {func.__name__}: {exc}"
                ) from exc
        return wrapper
    return decorator
