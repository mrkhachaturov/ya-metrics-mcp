from ya_metrics_mcp.exceptions import MCPYaMetrikaError, AuthenticationError


def test_mcp_error_is_exception():
    err = MCPYaMetrikaError("something went wrong")
    assert str(err) == "something went wrong"
    assert isinstance(err, Exception)


def test_auth_error_is_mcp_error():
    err = AuthenticationError("invalid token")
    assert isinstance(err, MCPYaMetrikaError)
    assert str(err) == "invalid token"
