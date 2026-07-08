import re
from dataclasses import dataclass

SEED_WORD_RE = re.compile(r"^[a-zA-Zа-яА-ЯёЁ0-9]{2,16}$")
MAX_SEED_WORDS = 1
STOP_WORDS = frozenset({"хуй", "пизд", "еба", "бля", "сука", "fuck", "shit"})


@dataclass(frozen=True)
class CreativeCategory:
    id: str
    label: str
    description: str
    requires_seeds: bool
    optional_seeds: bool


CATEGORIES: dict[str, CreativeCategory] = {
    "neutral": CreativeCategory(
        id="neutral",
        label="Нейтральный",
        description="Спокойные ники без шуток",
        requires_seeds=False,
        optional_seeds=True,
    ),
    "funny": CreativeCategory(
        id="funny",
        label="Шуточный",
        description="С юмором; можно добавить одно слово-опору",
        requires_seeds=False,
        optional_seeds=True,
    ),
    "gaming": CreativeCategory(
        id="gaming",
        label="Игровой",
        description="Стиль кланов и ников; одно слово-опора по желанию",
        requires_seeds=False,
        optional_seeds=True,
    ),
    "svino": CreativeCategory(
        id="svino",
        label="Свино-бренд",
        description="Тематика Svinopass: хрю, бекон и компания",
        requires_seeds=False,
        optional_seeds=True,
    ),
}


def list_categories() -> list[CreativeCategory]:
    return list(CATEGORIES.values())


def get_category(category_id: str) -> CreativeCategory | None:
    return CATEGORIES.get(category_id)


def normalize_seed_words(raw: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for word in raw:
        cleaned = word.strip().lower()
        if not cleaned or cleaned in seen:
            continue
        if not SEED_WORD_RE.match(cleaned):
            raise ValueError("Слово-опора: 2–16 символов, только буквы и цифры")
        if any(stop in cleaned for stop in STOP_WORDS):
            raise ValueError("Слово-опора содержит недопустимые фрагменты")
        seen.add(cleaned)
        result.append(cleaned)
        if len(result) > MAX_SEED_WORDS:
            raise ValueError("Можно указать только одно слово-опору")
    return result


def validate_creative_checkout(category_id: str, seed_words: list[str]) -> tuple[str, list[str]]:
    category = get_category(category_id)
    if not category:
        raise ValueError("Неизвестная категория стиля")

    words = normalize_seed_words(seed_words)
    if category.requires_seeds and not words:
        raise ValueError("Для этой категории нужно указать слово-опору")
    if not category.optional_seeds and not category.requires_seeds and words:
        raise ValueError("Для этой категории слово-опора не нужно")
    if category.optional_seeds and len(words) > MAX_SEED_WORDS:
        raise ValueError("Можно указать только одно слово-опору")

    return category_id, words
