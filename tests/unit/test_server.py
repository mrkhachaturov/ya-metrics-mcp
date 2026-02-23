from ya_metrics_mcp.servers.main import mcp


def test_server_has_name():
    assert mcp.name == "ya-metrics-mcp"
