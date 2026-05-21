from types import SimpleNamespace

from demo_limits import (
    SlidingWindowRateLimiter,
    get_client_identifier,
    get_demo_limit_settings,
)


def test_demo_limits_are_enabled_by_default(monkeypatch):
    monkeypatch.delenv("DEMO_MODE", raising=False)

    settings = get_demo_limit_settings()

    assert settings.enabled is True
    assert settings.ask_limit == 10
    assert settings.max_question_chars == 500


def test_demo_limits_can_be_disabled(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "false")

    settings = get_demo_limit_settings()

    assert settings.enabled is False


def test_demo_daily_limit_can_be_configured(monkeypatch):
    monkeypatch.setenv("DEMO_DAILY_LIMIT", "7")

    settings = get_demo_limit_settings()

    assert settings.ask_limit == 7


def test_rate_limiter_blocks_after_limit():
    limiter = SlidingWindowRateLimiter()

    assert limiter.hit("client-a", limit=2, window_seconds=60)[0] is True
    assert limiter.hit("client-a", limit=2, window_seconds=60)[0] is True

    allowed, retry_after, remaining = limiter.hit(
        "client-a",
        limit=2,
        window_seconds=60
    )

    assert allowed is False
    assert retry_after > 0
    assert remaining == 0


def test_client_identifier_prefers_forwarded_for_header():
    request = SimpleNamespace(
        headers={"x-forwarded-for": "203.0.113.10, 10.0.0.1"},
        client=SimpleNamespace(host="127.0.0.1")
    )

    assert get_client_identifier(request) == "203.0.113.10"
