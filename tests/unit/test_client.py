import pytest
import httpx
from ya_metrics_mcp.metrika.client import YaMetrikaClient
from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.exceptions import MCPYaMetrikaError, AuthenticationError


@pytest.fixture
def config():
    return YaMetrikaConfig(api_key="test-token")


@pytest.fixture
def client(config):
    return YaMetrikaClient(config)


@pytest.mark.asyncio
async def test_get_sends_oauth_header(httpx_mock, client):
    httpx_mock.add_response(
        url="https://api-metrika.yandex.net/stat/v1/data?ids=123",
        json={"data": []},
    )
    result = await client.get("/stat/v1/data", {"ids": "123"})
    assert result == {"data": []}
    request = httpx_mock.get_requests()[0]
    assert request.headers["Authorization"] == "OAuth test-token"


@pytest.mark.asyncio
async def test_get_raises_auth_error_on_401(httpx_mock, client):
    httpx_mock.add_response(
        url="https://api-metrika.yandex.net/stat/v1/data?ids=123",
        status_code=401,
        text="Unauthorized",
    )
    with pytest.raises(AuthenticationError):
        await client.get("/stat/v1/data", {"ids": "123"})


@pytest.mark.asyncio
async def test_get_raises_on_500(httpx_mock, client):
    # 500 is retried; after all retries raises MCPYaMetrikaError
    httpx_mock.add_response(
        url="https://api-metrika.yandex.net/stat/v1/data?ids=123",
        status_code=500,
        text="Server Error",
    )
    # 3 retries configured but we patch retry_delay to 0 to keep test fast
    client.config.retries = 1
    client.config.retry_delay = 0.0
    with pytest.raises(MCPYaMetrikaError, match="500"):
        await client.get("/stat/v1/data", {"ids": "123"})


@pytest.mark.asyncio
async def test_close(client):
    await client.close()  # should not raise
