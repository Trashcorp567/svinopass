import json
import uuid
from typing import Any

from app.services.ephemeral import get_redis

SELL_STAGING_TTL_SECONDS = 1800
MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_MIME = frozenset({"image/jpeg", "image/png", "image/webp"})


def _key(staging_id: str) -> str:
    return f"sell_staging:{staging_id}"


def create_staging_id() -> str:
    return str(uuid.uuid4())


def store_sell_image(staging_id: str, *, mime: str, data_b64: str) -> None:
    payload = {"mime": mime, "data": data_b64}
    get_redis().setex(_key(staging_id), SELL_STAGING_TTL_SECONDS, json.dumps(payload))


def peek_sell_image(staging_id: str) -> dict[str, Any] | None:
    raw = get_redis().get(_key(staging_id))
    if not raw:
        return None
    return json.loads(raw)


def pop_sell_image(staging_id: str) -> dict[str, Any] | None:
    client = get_redis()
    key = _key(staging_id)
    raw = client.get(key)
    if not raw:
        return None
    client.delete(key)
    return json.loads(raw)
