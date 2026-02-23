"""Custom exceptions for ya-metrics-mcp."""


class MCPYaMetrikaError(Exception):
    """Base exception for all ya-metrics-mcp errors."""


class AuthenticationError(MCPYaMetrikaError):
    """Raised when Yandex API authentication fails (401/403)."""
