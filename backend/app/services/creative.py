import logging
import re
import secrets
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.config import settings
from app.services.creative_categories import get_category
from app.services.password import _load_tokens
from app.services.payment import get_tier

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "creative"
CREATIVE_WARNING = (
    "Сохраните варианты сейчас — мы их не храним. "
    "Занятость ников в соцсетях и играх не проверяется."
)


@dataclass
class CreativeResult:
    kind: str
    category: str
    items: list[str]
    bios: list[str]
    source: str = "wordlist"


@lru_cache(maxsize=8)
def _load_lines(filename: str) -> tuple[str, ...]:
    path = DATA_DIR / filename
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise FileNotFoundError(f"Creative wordlist empty: {path}")
    return tuple(lines)


def _rng() -> secrets.SystemRandom:
    return secrets.SystemRandom()


def _to_latin(word: str) -> str:
    mapping = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    result: list[str] = []
    for ch in word.lower():
        if "a" <= ch <= "z" or "0" <= ch <= "9":
            result.append(ch)
        elif ch in mapping:
            result.append(mapping[ch])
    return "".join(result)


def _contains_seed(text: str, seeds: list[str]) -> bool:
    lowered = text.lower()
    for seed in seeds:
        if seed in lowered:
            return True
        latin = _to_latin(seed)
        if latin and latin in lowered:
            return True
    return False


def _is_english_nick(text: str) -> bool:
    return bool(re.match(r"^[a-zA-Z0-9_.\-]{2,24}$", text))


def _pick_seeds(seeds: list[str], count: int = 1) -> list[str]:
    rng = _rng()
    if not seeds:
        return []
    if len(seeds) <= count:
        return list(seeds)
    return rng.sample(seeds, count)


def _join_nick(adj: str, noun: str, style: str) -> str:
    rng = _rng()
    if style == "camel":
        return f"{adj.capitalize()}{noun.capitalize()}"
    if style == "snake":
        return f"{adj}_{noun}"
    if style == "flat":
        return f"{adj}{noun}"
    if style == "digit":
        return f"{adj}{noun}{rng.randint(1, 999)}"
    suffix = rng.choice(_load_lines("gaming_suffix.txt"))
    return f"{adj}{noun}{suffix}"


def _nick_from_parts(adj: str, noun: str, category: str) -> str:
    styles = ["camel", "snake", "flat", "digit"]
    if category == "gaming":
        styles.append("suffix")
    return _join_nick(adj, noun, _rng().choice(styles))


def _nick_with_seeds(seeds: list[str], category: str) -> str:
    rng = _rng()
    seed = _to_latin(rng.choice(seeds)).capitalize()
    if not seed:
        seed = "Seed"
    adj = rng.choice(_load_lines("nick_adj.txt"))
    noun = rng.choice(_load_lines("nick_noun.txt"))
    patterns = [
        f"{seed}{noun}",
        f"{adj}{seed}",
        f"{seed}_{noun}",
        f"{seed.capitalize()}{adj}",
        f"{adj}{seed}{rng.randint(1, 99)}",
    ]
    if category == "gaming":
        patterns.append(f"{seed}{rng.choice(_load_lines('gaming_suffix.txt'))}")
    return rng.choice(patterns)


def _svino_nick() -> str:
    rng = _rng()
    token = rng.choice(_load_tokens())
    adj = rng.choice(_load_lines("nick_adj.txt"))
    patterns = [
        f"{token}{rng.randint(1, 99)}",
        f"{adj}{token}",
        f"{token.capitalize()}{adj}",
        f"{token}_{adj}",
    ]
    return rng.choice(patterns)


def _generate_nickname(category: str, seeds: list[str]) -> str:
    if category == "svino":
        if seeds:
            return _nick_with_seeds(seeds, "gaming")
        return _svino_nick()
    if seeds and category in ("funny", "gaming", "neutral") and _rng().random() < 0.7:
        return _nick_with_seeds(seeds, "gaming" if category == "gaming" else category)
    adj = _rng().choice(_load_lines("nick_adj.txt"))
    noun = _rng().choice(_load_lines("nick_noun.txt"))
    return _nick_from_parts(adj, noun, category)


def _generate_pseudonym(category: str, seeds: list[str]) -> str:
    """Pseudonym-style nick for the «imena» tier — not real person names."""
    return _generate_nickname(category, seeds)


def _generate_name(category: str, seeds: list[str]) -> str:
    return _generate_pseudonym(category, seeds)


def _unique_items(
    generator,
    count: int,
    *,
    category: str,
    seeds: list[str],
    must_contain_seed: bool = False,
) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    attempts = 0
    max_attempts = count * 40
    while len(result) < count and attempts < max_attempts:
        attempts += 1
        item = generator(category, seeds)
        if not _is_english_nick(item):
            continue
        key = item.lower()
        if key in seen:
            continue
        if must_contain_seed and seeds and not _contains_seed(item, seeds):
            continue
        seen.add(key)
        result.append(item)
    if len(result) < count:
        raise RuntimeError("Could not generate enough unique creative items")
    return result


def _truncate_bio(text: str, max_len: int = 120) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def _generate_bios(nicknames: list[str], seeds: list[str], count: int) -> list[str]:
    rng = _rng()
    templates = list(_load_lines("bio_templates.txt"))
    bios: list[str] = []
    seen: set[str] = set()
    attempts = 0
    seed_text = ", ".join(seeds) if seeds else "свободный стиль"
    while len(bios) < count and attempts < count * 20:
        attempts += 1
        nick = rng.choice(nicknames)
        template = rng.choice(templates)
        bio = _truncate_bio(template.format(nick=nick, seeds=seed_text))
        if bio in seen:
            continue
        seen.add(bio)
        bios.append(bio)
    return bios


def _generate_creative_pack_wordlist(
    tier_id: str,
    category_id: str,
    seed_words: list[str],
) -> CreativeResult:
    if not get_category(category_id):
        raise ValueError("Unknown category")

    tier = get_tier(tier_id)
    if not tier or tier.get("product_type") != "creative":
        raise ValueError("Not a creative tier")

    kind = tier.get("creative_kind", "nicknames")
    seeds = list(seed_words)

    if kind == "names":
        items = _unique_items(
            _generate_name,
            tier.get("item_count", 15),
            category=category_id,
            seeds=seeds,
        )
        return CreativeResult(kind=kind, category=category_id, items=items, bios=[])

    if kind == "social":
        nick_count = tier.get("nick_count", 10)
        bio_count = tier.get("bio_count", 3)
        items = _unique_items(
            _generate_nickname,
            nick_count,
            category=category_id,
            seeds=seeds,
        )
        bios = _generate_bios(items, seeds, bio_count)
        return CreativeResult(kind=kind, category=category_id, items=items, bios=bios)

    items = _unique_items(
        _generate_nickname,
        tier.get("item_count", 15),
        category=category_id,
        seeds=seeds,
    )
    return CreativeResult(kind=kind, category=category_id, items=items, bios=[])


def generate_creative_pack(
    tier_id: str,
    category_id: str,
    seed_words: list[str],
) -> CreativeResult:
    if (
        settings.creative_ai_enabled
        and settings.yandex_gpt_api_key
        and settings.yandex_gpt_folder_id
    ):
        try:
            from app.services.creative_ai import generate_creative_pack_ai

            logger.info(
                "Calling Yandex GPT: tier=%s category=%s seeds=%s",
                tier_id,
                category_id,
                seed_words,
            )
            result = generate_creative_pack_ai(tier_id, category_id, seed_words)
            logger.info(
                "Yandex GPT ok: tier=%s category=%s items=%d",
                tier_id,
                category_id,
                len(result.items),
            )
            return result
        except Exception:
            logger.exception(
                "Yandex GPT failed, using wordlist fallback (tier=%s category=%s)",
                tier_id,
                category_id,
            )

    logger.info(
        "Wordlist fallback: tier=%s category=%s seeds=%s",
        tier_id,
        category_id,
        seed_words,
    )
    return _generate_creative_pack_wordlist(tier_id, category_id, seed_words)
