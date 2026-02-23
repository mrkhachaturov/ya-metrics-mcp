"""ya-metrics-mcp: MCP server for Yandex Metrika analytics."""
from __future__ import annotations

import logging

import click
from dotenv import load_dotenv

from ya_metrics_mcp.utils.lifecycle import setup_signal_handlers
from ya_metrics_mcp.utils.logging import setup_logging

logger = logging.getLogger("ya-metrics")


@click.command()
@click.option("--transport", default="stdio", type=click.Choice(["stdio", "streamable-http", "sse"]), help="Transport mode")
@click.option("--port", default=8000, type=int, help="HTTP port (HTTP transport only)")
@click.option("--host", default="0.0.0.0", help="HTTP host (HTTP transport only)")
@click.option("--env-file", default=None, help="Path to .env file")
@click.option("-v", "--verbose", count=True, help="Verbose logging (-v INFO, -vv DEBUG)")
def main(transport: str, port: int, host: str, env_file: str | None, verbose: int) -> None:
    """ya-metrics-mcp: Yandex Metrika MCP server."""
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    setup_logging(verbose)
    setup_signal_handlers()

    # Import tools to register them with the mcp instance
    import ya_metrics_mcp.servers.tools  # noqa: F401
    from ya_metrics_mcp.servers.main import mcp

    logger.info("Starting ya-metrics-mcp (transport=%s)", transport)

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport=transport, host=host, port=port)


if __name__ == "__main__":
    main()
