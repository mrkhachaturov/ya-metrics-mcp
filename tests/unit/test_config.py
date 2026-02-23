import pytest
from ya_metrics_mcp.metrika.config import YaMetrikaConfig
from ya_metrics_mcp.exceptions import AuthenticationError


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("YANDEX_API_KEY", "test-token-123")
    config = YaMetrikaConfig.from_env()
    assert config.api_key == "test-token-123"
    assert config.timeout == 30
    assert config.retries == 3
    assert config.retry_delay == 1.0
    assert config.read_only is False
    assert config.enabled_tools is None


def test_config_from_env_custom_values(monkeypatch):
    monkeypatch.setenv("YANDEX_API_KEY", "tok")
    monkeypatch.setenv("YANDEX_TIMEOUT", "60")
    monkeypatch.setenv("YANDEX_RETRIES", "5")
    monkeypatch.setenv("READ_ONLY_MODE", "true")
    monkeypatch.setenv("ENABLED_TOOLS", "get_visits,get_account_info")
    config = YaMetrikaConfig.from_env()
    assert config.timeout == 60
    assert config.retries == 5
    assert config.read_only is True
    assert config.enabled_tools == ["get_visits", "get_account_info"]


def test_config_raises_if_no_api_key(monkeypatch):
    monkeypatch.delenv("YANDEX_API_KEY", raising=False)
    with pytest.raises(AuthenticationError, match="YANDEX_API_KEY"):
        YaMetrikaConfig.from_env()


def test_is_auth_configured():
    config = YaMetrikaConfig(api_key="tok")
    assert config.is_auth_configured() is True

    config_empty = YaMetrikaConfig(api_key="")
    assert config_empty.is_auth_configured() is False
