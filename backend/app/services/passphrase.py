import math
import secrets
from functools import lru_cache
from pathlib import Path

from app.services.password import SYMBOLS, estimate_entropy_bits

WORDLIST_PATH = Path(__file__).resolve().parent.parent / "data" / "pig_wordlist.txt"
DEFAULT_WORD_COUNT = 4
SEPARATOR = "-"


@lru_cache(maxsize=1)
def _load_words() -> tuple[str, ...]:
    if not WORDLIST_PATH.is_file():
        raise FileNotFoundError(f"Wordlist not found: {WORDLIST_PATH}")
    words = [line.strip() for line in WORDLIST_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(words) < 100:
        raise ValueError("Wordlist too small")
    return tuple(words)


def generate_passphrase(word_count: int = DEFAULT_WORD_COUNT, separator: str = SEPARATOR) -> str:
    words = _load_words()
    rng = secrets.SystemRandom()
    picked = [rng.choice(words) for _ in range(word_count)]
    digit = rng.choice("23456789")
    symbol = rng.choice(SYMBOLS)
    return separator.join(picked) + separator + digit + symbol


def estimate_passphrase_entropy_bits(passphrase: str, word_count: int = DEFAULT_WORD_COUNT) -> float:
    words = _load_words()
    word_bits = word_count * math.log2(len(words))
    extra_bits = math.log2(8 * len(SYMBOLS))
    separator_bits = math.log2(2)
    return round(word_bits + extra_bits + separator_bits, 1)


def passphrase_entropy_for_display(passphrase: str) -> float:
    try:
        return estimate_passphrase_entropy_bits(passphrase)
    except (FileNotFoundError, ValueError):
        return estimate_entropy_bits(passphrase)
