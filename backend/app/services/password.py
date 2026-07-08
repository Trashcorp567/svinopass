import math
import secrets
import string
from functools import lru_cache
from pathlib import Path

AMBIGUOUS = set("0OIl1|")
LOWER = "".join(c for c in string.ascii_lowercase if c not in AMBIGUOUS)
UPPER = "".join(c for c in string.ascii_uppercase if c not in AMBIGUOUS)
DIGITS = "".join(c for c in string.digits if c not in AMBIGUOUS)
SYMBOLS = "!@#$%^&*-_=+?"
ALNUM = LOWER + UPPER + DIGITS
FULL = ALNUM + SYMBOLS

TOKEN_PATH = Path(__file__).resolve().parent.parent / "data" / "pig_tokens.txt"
MIN_RANDOM_PADDING = 8


def _shuffle(chars: list[str]) -> str:
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def _fill(length: int, alphabet: str) -> list[str]:
    rng = secrets.SystemRandom()
    return [rng.choice(alphabet) for _ in range(length)]


@lru_cache(maxsize=1)
def _load_tokens() -> tuple[str, ...]:
    if not TOKEN_PATH.is_file():
        raise FileNotFoundError(f"Pig token list not found: {TOKEN_PATH}")
    tokens = [line.strip() for line in TOKEN_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(tokens) < 10:
        raise ValueError("Pig token list too small")
    return tuple(tokens)


def _pick_token(length: int) -> str:
    rng = secrets.SystemRandom()
    max_token_len = max(length - MIN_RANDOM_PADDING, 4)
    candidates = [token for token in _load_tokens() if 3 <= len(token) <= max_token_len]
    if not candidates:
        candidates = [token for token in _load_tokens() if len(token) < length]
    return rng.choice(candidates)


def _required_chars(tier_id: str) -> list[str]:
    rng = secrets.SystemRandom()
    if tier_id == "svinomat":
        return [rng.choice(LOWER), rng.choice(UPPER), rng.choice(DIGITS)]
    if tier_id in {"bacon", "legend"}:
        return [
            rng.choice(LOWER),
            rng.choice(UPPER),
            rng.choice(DIGITS),
            rng.choice(SYMBOLS),
        ]
    return []


def _alphabet_for_tier(tier_id: str) -> str:
    if tier_id == "svinomat":
        return ALNUM
    return FULL


def generate_password(tier_id: str, length: int) -> str:
    rng = secrets.SystemRandom()
    token = _pick_token(length)
    filler_len = max(length - len(token), 0)
    alphabet = _alphabet_for_tier(tier_id)
    required = _required_chars(tier_id)
    extra = max(filler_len - len(required), 0)
    filler = _shuffle(required + _fill(extra, alphabet))
    pos = rng.randrange(0, len(filler) + 1)
    password = filler[:pos] + token + filler[pos:]
    if len(password) < length:
        password += "".join(rng.choice(alphabet) for _ in range(length - len(password)))
    return password[:length]


def password_contains_theme(password: str) -> bool:
    lowered = password.lower()
    for token in _load_tokens():
        if token.lower() in lowered:
            return True
    return False


def estimate_entropy_bits(password: str) -> float:
    pool = 0
    if any(c in LOWER for c in password):
        pool += len(LOWER)
    if any(c in UPPER for c in password):
        pool += len(UPPER)
    if any(c in DIGITS for c in password):
        pool += len(DIGITS)
    if any(c in SYMBOLS for c in password):
        pool += len(SYMBOLS)
    if pool <= 1:
        pool = len(FULL)
    return round(len(password) * math.log2(pool), 1)
