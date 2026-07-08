import json
from typing import Any

import redis

from app.config import settings

_redis: redis.Redis | None = None

FULFILLMENT_TTL_SECONDS = 900
REPORT_META_TTL_SECONDS = 604800  # 7 days


def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def store_report_meta(order_id: str, payload: dict[str, Any]) -> None:
    key = f"report_meta:{order_id}"
    get_redis().setex(key, REPORT_META_TTL_SECONDS, json.dumps(payload))


def get_report_meta(order_id: str) -> dict[str, Any] | None:
    raw = get_redis().get(f"report_meta:{order_id}")
    if not raw:
        return None
    return json.loads(raw)


def store_fulfillment(order_id: str, payload: dict[str, Any]) -> None:
    key = f"fulfillment:{order_id}"
    get_redis().setex(key, FULFILLMENT_TTL_SECONDS, json.dumps(payload))


def pop_fulfillment(order_id: str) -> dict[str, Any] | None:
    key = f"fulfillment:{order_id}"
    client = get_redis()
    raw = client.get(key)
    if not raw:
        return None
    client.delete(key)
    return json.loads(raw)
