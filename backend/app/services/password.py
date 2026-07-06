import math
import secrets
import string

AMBIGUOUS = set("0OIl1|")
LOWER = "".join(c for c in string.ascii_lowercase if c not in AMBIGUOUS)
UPPER = "".join(c for c in string.ascii_uppercase if c not in AMBIGUOUS)
DIGITS = "".join(c for c in string.digits if c not in AMBIGUOUS)
SYMBOLS = "!@#$%^&*-_=+?"
ALNUM = LOWER + UPPER + DIGITS
FULL = ALNUM + SYMBOLS


def _shuffle(chars: list[str]) -> str:
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def _fill(length: int, alphabet: str) -> list[str]:
    rng = secrets.SystemRandom()
    return [rng.choice(alphabet) for _ in range(length)]


def generate_password(tier_id: str, length: int) -> str:
    rng = secrets.SystemRandom()

    if tier_id == "svinomat":
        chars = [
            rng.choice(LOWER),
            rng.choice(UPPER),
            rng.choice(DIGITS),
            *_fill(max(length - 3, 0), ALNUM),
        ]
        return _shuffle(chars)[:length]

    if tier_id in {"bacon", "legend"}:
        chars = [
            rng.choice(LOWER),
            rng.choice(UPPER),
            rng.choice(DIGITS),
            rng.choice(SYMBOLS),
            *_fill(max(length - 4, 0), FULL),
        ]
        return _shuffle(chars)[:length]

    chars = _fill(length, FULL)
    return _shuffle(chars)[:length]


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