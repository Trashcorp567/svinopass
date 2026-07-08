import base64

import pytest

from app.services.image_hosting import (
    create_image_token,
    get_hosted_image,
    store_hosted_image,
    validate_image_qr_checkout,
)
from app.services.payment import get_tier

TINY_PNG_B64 = base64.b64encode(
    base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    )
).decode("ascii")


def test_validate_image_qr_requires_staging():
    tier = get_tier("qr_pic")
    assert tier is not None
    with pytest.raises(ValueError, match="Image is required"):
        validate_image_qr_checkout(tier, staging_id=None)


def test_hosted_image_roundtrip():
    token = create_image_token()
    store_hosted_image(token, mime="image/png", data_b64=TINY_PNG_B64, ttl_seconds=60)
    payload = get_hosted_image(token)
    assert payload is not None
    assert payload["mime"] == "image/png"
