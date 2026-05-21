import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass


TRUE_VALUES = {"1", "true", "yes", "on"}
FALSE_VALUES = {"0", "false", "no", "off"}


@dataclass(frozen=True)
class DemoLimitSettings:
    enabled: bool
    ask_limit: int
    window_seconds: int
    max_question_chars: int
    max_index_chunks: int
    max_context_chunks: int


def get_bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    normalized_value = raw_value.strip().lower()

    if normalized_value in TRUE_VALUES:
        return True

    if normalized_value in FALSE_VALUES:
        return False

    return default


def get_int_env(names, default: int, minimum: int = 1) -> int:
    if isinstance(names, str):
        names = [names]

    raw_value = None

    for name in names:
        raw_value = os.getenv(name)

        if raw_value is not None:
            break

    if raw_value is None:
        return default

    try:
        value = int(raw_value)
    except ValueError:
        return default

    return max(value, minimum)


def get_demo_limit_settings() -> DemoLimitSettings:
    return DemoLimitSettings(
        enabled=get_bool_env("DEMO_MODE", True),
        ask_limit=get_int_env(["DEMO_DAILY_LIMIT", "DEMO_ASK_LIMIT"], 10),
        window_seconds=get_int_env("DEMO_WINDOW_SECONDS", 24 * 60 * 60),
        max_question_chars=get_int_env("DEMO_MAX_QUESTION_CHARS", 500),
        max_index_chunks=get_int_env("DEMO_MAX_INDEX_CHUNKS", 120),
        max_context_chunks=get_int_env("DEMO_MAX_CONTEXT_CHUNKS", 8),
    )


def get_client_identifier(request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown-client"


def format_retry_after(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds} seconds"

    minutes = seconds // 60

    if minutes < 60:
        return f"{minutes} minutes"

    hours = minutes // 60
    return f"{hours} hours"


class SlidingWindowRateLimiter:
    def __init__(self):
        self._hits_by_client = defaultdict(deque)

    def hit(self, client_id: str, limit: int, window_seconds: int):
        now = time.time()
        hits = self._hits_by_client[client_id]
        cutoff = now - window_seconds

        while hits and hits[0] <= cutoff:
            hits.popleft()

        if len(hits) >= limit:
            retry_after = max(1, int(window_seconds - (now - hits[0])))
            return False, retry_after, 0

        hits.append(now)
        remaining = max(0, limit - len(hits))
        return True, 0, remaining

    def reset(self):
        self._hits_by_client.clear()


ask_rate_limiter = SlidingWindowRateLimiter()
