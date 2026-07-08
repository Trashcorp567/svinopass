import json
import logging
import re

import httpx

from app.config import settings
from app.services.creative_categories import STOP_WORDS, get_category
from app.services.creative import CreativeResult
from app.services.payment import get_tier

logger = logging.getLogger(__name__)

YANDEX_CHAT_URL = "https://llm.api.cloud.yandex.net/v1/chat/completions"

_JSON_BLOCK_RE = re.compile(r"\{[\s\S]*\}")
_NICK_RE = re.compile(r"^[a-zA-Z0-9_.\-]{2,24}$")

_GENERIC_SUFFIXES = frozenset({
    "vibe", "glow", "dawn", "edge", "nova", "wave", "bloom", "mist",
    "rush", "flick", "echo", "pulse", "glide", "spark", "shade", "drift",
    "dream", "core", "flow", "sync", "byte", "mind", "soul", "star",
})

_STYLE_HINTS: dict[str, str] = {
    "neutral": (
        "спокойные нейтральные ники: природа, цвета, абстракции, минимализм. "
        "FrostByte, quiet_river9, PixelMoth, hex_apricot"
    ),
    "funny": (
        "абсурдный интернет-юмор, каламбуры, самоирония — не киберспорт и не свинки. "
        "BaconBandit, SirOopsALot, MemeAccountant, ChaosHam"
    ),
    "gaming": (
        "киберспорт и стрим: кланы, ранги, sweaty-теги, xX, noscope, clutch, tilt, ranked. "
        "headshot_hog, ClutchFrag, xXrankedXx, tilt_snout — БЕЗ свиной тематики, если якорь не про свиней"
    ),
    "svino": (
        "бренд Svinopass: хрю, бекон, hog, sty, snout, khryak, rasher — свиной мем, не корпоративный маскот. "
        "OinkBandit42, Khryakzilla, BaconGhoul, StyRunner"
    ),
}

_STYLE_MUST: dict[str, str] = {
    "neutral": (
        "MUST: calm, versatile handles; mix adjectives, nouns, numbers, underscores.\n"
        "MUST NOT: gaming slang (clutch, noscope, ranked, pro, gg), pig/oink/bacon/hog, meme humor"
    ),
    "funny": (
        "MUST: jokes, puns, unexpected word combos, self-deprecating humor.\n"
        "MUST NOT: tryhard esports tags, xXclanXx format, pig theme unless anchor implies it"
    ),
    "gaming": (
        "MUST: esports/streamer energy — clutch, noscope, ranked, frag, ace, sweaty, tilt, pro, gg, "
        "clan tags, xXprefixXx, snake_case ranks.\n"
        "MUST NOT: pig/oink/bacon/hog/snout/sty/khryak (that is svino style, not gaming). "
        "Anchor word → weave into clan tag or gamer tag, not animal pun"
    ),
    "svino": (
        "MUST: pig-meme theme in most items — oink, bacon, hog, snout, sty, khryak, rasher, mud.\n"
        "MUST NOT: generic esports without pig flavor; this is Svinopass brand, not a random clan"
    ),
}

_BIO_STYLE_HINTS: dict[str, str] = {
    "neutral": "спокойные, лаконичные био без мемов и крикливого пафоса",
    "funny": "самоирония, абсурд, шутки — не киберспортивный пафос",
    "gaming": "пафос киберспортсмена/стримера, отсылки к матчам, рангам, победам",
    "svino": "свиной юмор Svinopass, бекон/хрюканье, ирония про свиней",
}

_SYSTEM_BY_CATEGORY: dict[str, str] = {
    "neutral": (
        "You invent clean, understated English usernames. "
        "No memes, no gaming slang, no animal puns. "
        "Reply only with valid JSON, no markdown."
    ),
    "funny": (
        "You invent witty, absurd English usernames. Humor and puns over competitiveness. "
        "Reply only with valid JSON, no markdown."
    ),
    "gaming": (
        "You invent sweaty gamer and clan tags in English. Esports and streamer culture only. "
        "Never default to pig/oink/bacon — that is a different style. "
        "Reply only with valid JSON, no markdown."
    ),
    "svino": (
        "You invent Svinopass pig-meme usernames. Oink, bacon, hog energy is required. "
        "Reply only with valid JSON, no markdown."
    ),
}

_GOOD_EXAMPLES: dict[str, list[str]] = {
    "neutral": ["FrostByte", "quiet_river9", "MothPilot", "hex_apricot", "CalmRaven42"],
    "funny": ["BaconBandit", "SirOopsALot", "MemeAccountant", "ChaosHam", "OopsAllOink"],
    "gaming": ["xXclutchXx", "ranked_rat", "tilt_snout", "frag_lord99", "NoScopeAce", "sweaty_queue"],
    "svino": ["OinkBandit42", "RasherRaid", "Khryakzilla", "StyRunner", "BaconGhoul", "MudLord_x"],
}

_BAD_EXAMPLES = [
    "TrashVibe", "TrashGlow", "TrashNova", "TrashEdge", "TrashPulse",
    "CoolGuy123", "SuperUser", "BestPlayer",
]

_KIND_HINTS: dict[str, str] = {
    "nicknames": (
        "15 short English usernames for games, social media and messengers. "
        "Mix CamelCase, snake_case, digits, xX tags, abbreviations. No spaces."
    ),
    "names": (
        "15 English pseudonyms / alter-egos for characters, channels and streamers. "
        "NOT real human names (no John Smith). Characters with personality."
    ),
    "social": (
        "10 English usernames for social media + 3 short profile bios in Russian (max 120 chars). "
        "Usernames: English only. Bios: Russian only (Cyrillic), witty and specific."
    ),
}


def _contains_stop_word(text: str) -> bool:
    lowered = text.lower()
    return any(stop in lowered for stop in STOP_WORDS)


def _contains_seed(text: str, seeds: list[str]) -> bool:
    lowered = text.lower()
    for seed in seeds:
        if seed in lowered:
            return True
        latin = _to_latin(seed)
        if latin and latin in lowered:
            return True
    return False


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


def _seed_prefixes(seeds: list[str]) -> list[str]:
    prefixes: list[str] = []
    for seed in seeds:
        prefixes.append(seed.lower())
        latin = _to_latin(seed).lower()
        if latin:
            prefixes.append(latin)
            if len(latin) >= 3:
                prefixes.append(latin.capitalize())
    return list(dict.fromkeys(prefixes))


def _has_cyrillic(text: str) -> bool:
    return any("\u0400" <= ch <= "\u04FF" for ch in text)


def _is_lazy_nick(nick: str, seeds: list[str]) -> bool:
    lower = nick.lower()
    if any(lower.endswith(suffix) for suffix in _GENERIC_SUFFIXES):
        for prefix in _seed_prefixes(seeds):
            if prefix and lower.startswith(prefix.lower()):
                return True
    return False


def _pack_quality_issue(items: list[str], seeds: list[str]) -> str | None:
    if len(items) < 3:
        return None

    lazy_count = sum(1 for item in items if _is_lazy_nick(item, seeds))
    if lazy_count > max(2, len(items) // 4):
        return "too many lazy AnchorWord+GenericSuffix combos"

    if seeds:
        seed_hits = sum(1 for item in items if _contains_seed(item, seeds))
        min_hits, max_prefix = _seed_requirements(len(items))
        if seed_hits < min_hits:
            return (
                f"too few items use anchor word "
                f"(need at least {min_hits}, got {seed_hits})"
            )
        prefix_hits = sum(
            1
            for item in items
            if any(item.lower().startswith(p.lower()) for p in _seed_prefixes(seeds))
        )
        if prefix_hits > max_prefix:
            return "too many items share the same anchor prefix"
        if seed_hits == len(items):
            return "every item contains the anchor — need thematic variety without repeating the prefix"

    prefix_counts: dict[str, int] = {}
    for item in items:
        match = re.match(r"^([A-Za-z]{3,})", item)
        if match:
            key = match.group(1).lower()
            prefix_counts[key] = prefix_counts.get(key, 0) + 1
    if prefix_counts and max(prefix_counts.values()) > max(3, len(items) // 3):
        return "too many nicks share the same opening word"

    suffix_hits = sum(
        1 for item in items if any(item.lower().endswith(s) for s in _GENERIC_SUFFIXES)
    )
    if suffix_hits > len(items) // 2:
        return "too many generic AI suffixes (Vibe, Glow, Nova, Pulse...)"

    return None


def _seed_requirements(item_count: int) -> tuple[int, int]:
    """Minimum items that must contain anchor; max items that may start with anchor prefix."""
    min_hits = max(4, (item_count + 2) // 3)
    max_prefix = max(4, item_count // 3)
    return min_hits, max_prefix


def _build_seed_rules(category_id: str, seeds: list[str], item_count: int) -> str:
    if not seeds:
        return "Anchor word: none — do not invent a shared prefix for all items."

    seed = seeds[0]
    latin = _to_latin(seed) or seed
    min_hits, max_prefix = _seed_requirements(item_count)
    cap = latin.capitalize()

    weave_hints = {
        "neutral": (
            f"embed \"{latin}\" in {min_hits}+ items — prefix, middle or suffix "
            f"(e.g. {cap}Moth, quiet_{latin}, hex_{latin}9)"
        ),
        "funny": (
            f"pun on \"{latin}\" / \"{seed}\" in {min_hits}+ items — rhymes, mashups, absurd wordplay "
            f"(e.g. {cap}Riddle, Pun{cap}, Sir{cap}Oops, {latin}_giggles, RiddleOf{cap})"
        ),
        "gaming": (
            f"clan/squad tag with \"{latin}\" in {min_hits}+ items "
            f"(e.g. {latin}_squad, xX{cap}Xx, {cap}Frag) — esports vibe, not animal puns"
        ),
        "svino": (
            f"pig-meme twist on \"{latin}\" in {min_hits}+ items "
            f"(e.g. {cap}Oink, {latin}_bacon, Khryak{cap})"
        ),
    }
    weave = weave_hints.get(category_id, weave_hints["neutral"])

    return f"""Anchor word: "{seed}" (Latin: {latin}) — user provided this, it MUST appear in results.
- REQUIRED: at least {min_hits} of {item_count} items MUST contain "{latin}" as substring (any position)
- How to weave: {weave}
- At most {max_prefix} items may START with {latin} — vary placement (middle, suffix, pun)
- Do NOT use lazy prefix pattern ({latin}Vibe, {latin}Glow, {latin}Nova...)
- Items without anchor: still match style, but the pack as a whole must honor the anchor"""


def _build_prompt(
    *,
    kind: str,
    category_id: str,
    seeds: list[str],
    item_count: int,
    bio_count: int,
    retry_note: str = "",
) -> str:
    category = get_category(category_id)
    category_label = category.label if category else category_id
    style = _STYLE_HINTS.get(category_id, _STYLE_HINTS["neutral"])
    style_rules = _STYLE_MUST.get(category_id, _STYLE_MUST["neutral"])
    kind_hint = _KIND_HINTS.get(kind, _KIND_HINTS["nicknames"])
    good = ", ".join(_GOOD_EXAMPLES.get(category_id, _GOOD_EXAMPLES["neutral"]))
    bad = ", ".join(_BAD_EXAMPLES[:6])
    seed_rules = _build_seed_rules(category_id, seeds, item_count)

    bios_line = ""
    if bio_count:
        bio_style = _BIO_STYLE_HINTS.get(category_id, _BIO_STYLE_HINTS["neutral"])
        bios_line = (
            f'\nAlso generate exactly {bio_count} unique bios in "bios" '
            f"(max 120 chars each). Bios MUST be in Russian (Cyrillic). "
            f"Bio tone for style «{category_label}»: {bio_style}. "
            f"English nicknames inside bios are OK."
        )

    extra = max(6, item_count // 2)
    retry_block = f"\n\nFIX FROM LAST ATTEMPT: {retry_note}" if retry_note else ""

    return f"""User selected style: «{category_label}» (id={category_id}). This choice is mandatory — output must clearly match THIS style, not a blend of others.

Task: {kind_hint}

STYLE «{category_label}»:
{style}

Style rules:
{style_rules}

{seed_rules}

CREATIVITY RULES (critical):
- Every nick must feel different: different structure, rhythm, length
- Mix formats: CamelCase, snake_case, xXtagsXx, digits, abbreviations, compound puns
- BANNED lazy pattern: AnchorWord + generic suffix (Vibe, Glow, Nova, Edge, Pulse, Wave, Bloom, Mist, Rush, Echo, Glide)
- BANNED: repeating the same prefix on most items
- Good examples for THIS style only: {good}
- Bad examples (never do this): {bad}

Output:
- At least {item_count + extra} unique items (we pick {item_count})
- English only for items (usernames), Latin letters/digits/_.-, length 2–24, no spaces
- No real person names, no profanity{bios_line}{retry_block}

Return ONLY valid JSON:
{{"items": ["Nick1", "Nick2"], "bios": []}}"""


def _parse_response(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = _JSON_BLOCK_RE.search(text)
        if not match:
            raise ValueError("AI response is not JSON") from None
        return json.loads(match.group(0))


def _sanitize_nick(raw: str) -> str | None:
    if not isinstance(raw, str):
        return None
    cleaned = raw.strip().strip('"').strip("'").strip()
    if not cleaned:
        return None
    if "." in cleaned and cleaned.count(".") == 1:
        cleaned = cleaned.split(".", 1)[-1].strip()
    cleaned = cleaned.replace(" ", "").split(",")[0].split(":")[-1].strip()
    cleaned = re.sub(r"^\d+\.\s*", "", cleaned)
    if not _NICK_RE.match(cleaned):
        match = re.search(r"[A-Za-z][A-Za-z0-9_.\-]{1,23}", cleaned)
        if not match:
            return None
        cleaned = match.group(0)
    if _contains_stop_word(cleaned):
        return None
    return cleaned


def _validate_items(
    items: list[str],
    *,
    count: int,
    seeds: list[str],
    must_contain_seed: bool,
) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        cleaned = _sanitize_nick(item)
        if not cleaned or _is_lazy_nick(cleaned, seeds):
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        if must_contain_seed and seeds and not _contains_seed(cleaned, seeds):
            continue
        seen.add(key)
        result.append(cleaned)
        if len(result) >= count:
            break
    if len(result) < count:
        raise ValueError(f"AI returned only {len(result)}/{count} valid items")
    issue = _pack_quality_issue(result, seeds)
    if issue:
        raise ValueError(f"Pack quality check failed: {issue}")
    return result


def _validate_bios(bios: list[str], count: int) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for bio in bios:
        if not isinstance(bio, str):
            continue
        cleaned = bio.strip()
        if not cleaned or not _has_cyrillic(cleaned):
            continue
        if len(cleaned) > 120:
            cleaned = cleaned[:119].rstrip() + "…"
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
        if len(result) >= count:
            break
    if count and len(result) < count:
        raise ValueError(f"AI returned only {len(result)}/{count} valid bios")
    return result


def _call_yandex_gpt(prompt: str, *, category_id: str, temperature: float) -> str:
    if not settings.yandex_gpt_api_key or not settings.yandex_gpt_folder_id:
        raise RuntimeError("Yandex GPT is not configured")

    folder_id = settings.yandex_gpt_folder_id
    system = _SYSTEM_BY_CATEGORY.get(category_id, _SYSTEM_BY_CATEGORY["neutral"])
    headers = {
        "Authorization": f"Api-Key {settings.yandex_gpt_api_key}",
        "x-folder-id": folder_id,
        "Content-Type": "application/json",
    }
    body = {
        "model": f"gpt://{folder_id}/{settings.yandex_gpt_model}/latest",
        "temperature": temperature,
        "max_tokens": 2500,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
    }

    with httpx.Client(timeout=90.0) as client:
        response = client.post(YANDEX_CHAT_URL, headers=headers, json=body)
        response.raise_for_status()
        data = response.json()

    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("Yandex GPT returned empty response")
    return choices[0]["message"]["content"]


def generate_creative_pack_ai(
    tier_id: str,
    category_id: str,
    seed_words: list[str],
) -> CreativeResult:
    tier = get_tier(tier_id)
    if not tier or tier.get("product_type") != "creative":
        raise ValueError("Not a creative tier")

    kind = tier.get("creative_kind", "nicknames")
    seeds = list(seed_words)[:1]
    item_count = tier.get("item_count") or tier.get("nick_count", 15)
    bio_count = tier.get("bio_count", 0) if kind == "social" else 0

    items: list[str] = []
    bios: list[str] = []
    seen: set[str] = set()
    last_error: Exception | None = None
    retry_note = ""

    logger.info(
        "Yandex GPT request: model=%s tier=%s category=%s seeds=%s items=%d",
        settings.yandex_gpt_model,
        tier_id,
        category_id,
        seeds,
        item_count,
    )

    temperatures = [0.92, 0.97, 1.0]
    for attempt in range(3):
        need = item_count - len(items)
        if need <= 0:
            break
        try:
            prompt = _build_prompt(
                kind=kind,
                category_id=category_id,
                seeds=seeds,
                item_count=need if not items else item_count,
                bio_count=bio_count if not bios else 0,
                retry_note=retry_note,
            )
            raw = _call_yandex_gpt(
                prompt,
                category_id=category_id,
                temperature=temperatures[attempt],
            )
            payload = _parse_response(raw)
            batch = _validate_items(
                payload.get("items", []),
                count=need if not items else item_count,
                seeds=seeds,
                must_contain_seed=False,
            )
            for item in batch:
                key = item.lower()
                if key in seen:
                    continue
                seen.add(key)
                items.append(item)
            if bio_count and not bios:
                bios = _validate_bios(payload.get("bios", []), bio_count)
            if len(items) >= item_count:
                final = items[:item_count]
                issue = _pack_quality_issue(final, seeds)
                if issue:
                    raise ValueError(f"Pack quality check failed: {issue}")
                break
        except Exception as exc:
            last_error = exc
            retry_note = str(exc)
            logger.warning("Yandex GPT attempt %s failed: %s", attempt + 1, exc)

    if len(items) < item_count:
        if last_error:
            raise last_error
        raise ValueError(f"AI returned only {len(items)}/{item_count} valid items")

    logger.info(
        "Yandex GPT ok: tier=%s category=%s items=%d",
        tier_id,
        category_id,
        len(items),
    )
    return CreativeResult(
        kind=kind,
        category=category_id,
        items=items[:item_count],
        bios=bios,
        source="yandexgpt",
    )
