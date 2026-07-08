import hashlib
import logging

from app.services.ephemeral import get_redis

logger = logging.getLogger(__name__)

ISSUED_CREDENTIALS_KEY = "svinopass:issued_credentials"
MAX_CLAIM_ATTEMPTS = 32


def credential_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def claim_credential(value: str) -> bool:
    """Return True if this credential has not been issued before."""
    try:
        added = get_redis().sadd(ISSUED_CREDENTIALS_KEY, credential_fingerprint(value))
        return added == 1
    except Exception:
        logger.exception("Redis unavailable for uniqueness check; allowing credential")
        return True


def claim_unique(generator, *args, **kwargs):
    for attempt in range(MAX_CLAIM_ATTEMPTS):
        value = generator(*args, **kwargs)
        if claim_credential(value):
            return value
        logger.warning("Credential collision on attempt %s", attempt + 1)
    raise RuntimeError("Could not generate unique credential")
