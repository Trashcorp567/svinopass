import json
import uuid
from datetime import datetime, timedelta, timezone

from app.services.ephemeral import get_redis

HOSTED_IMAGE_TTL_DAYS = 30
HOSTED_IMAGE_TTL_SECONDS = HOSTED_IMAGE_TTL_DAYS * 24 * 3600


def _key(token: str) -> str:
    return f"hosted_image:{token}"


def create_image_token() -> str:
    return str(uuid.uuid4())


def store_hosted_image(
    token: str,
    *,
    mime: str,
    data_b64: str,
    ttl_seconds: int = HOSTED_IMAGE_TTL_SECONDS,
) -> datetime:
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
    payload = {
        "mime": mime,
        "data": data_b64,
        "expires_at": expires_at.isoformat(),
    }
    get_redis().setex(_key(token), ttl_seconds, json.dumps(payload))
    return expires_at


def get_hosted_image(token: str) -> dict | None:
    raw = get_redis().get(_key(token))
    if not raw:
        return None
    return json.loads(raw)


def validate_image_qr_checkout(tier: dict, *, staging_id: str | None) -> dict:
    if tier.get("product_type") != "image_qr":
        raise ValueError("Not an image QR tier")
    if not staging_id or not staging_id.strip():
        raise ValueError("Image is required")
    return {"staging_id": staging_id.strip()}
