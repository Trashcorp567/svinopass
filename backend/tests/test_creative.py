import pytest
import re

from app.config import settings
from app.services.creative import _generate_creative_pack_wordlist, generate_creative_pack
from app.services.creative_categories import validate_creative_checkout


@pytest.fixture(autouse=True)
def disable_creative_ai(monkeypatch):
    monkeypatch.setattr(settings, "creative_ai_enabled", False)
    monkeypatch.setattr(settings, "yandex_gpt_api_key", "")
    monkeypatch.setattr(settings, "yandex_gpt_folder_id", "")


def test_validate_single_seed_only():
    with pytest.raises(ValueError, match="одно"):
        validate_creative_checkout("funny", ["bacon", "oink"])


def test_validate_neutral_accepts_one_seed():
    _, words = validate_creative_checkout("neutral", ["bacon"])
    assert words == ["bacon"]


def test_generate_klichki_count():
    result = generate_creative_pack("klichki", "neutral", [])
    assert result.kind == "nicknames"
    assert len(result.items) == 15
    assert len(set(item.lower() for item in result.items)) == 15
    assert result.bios == []


def test_generate_imena_count():
    result = _generate_creative_pack_wordlist("imena", "gaming", [])
    assert result.kind == "names"
    assert len(result.items) == 15
    for item in result.items:
        assert " " not in item


def test_generate_socpak_with_bios():
    result = generate_creative_pack("socpak", "funny", ["meme"])
    assert result.kind == "social"
    assert len(result.items) == 10
    assert len(result.bios) == 3
    assert all(len(bio) <= 120 for bio in result.bios)
    assert all(any("\u0400" <= ch <= "\u04FF" for ch in bio) for bio in result.bios)


def test_funny_with_seed():
    result = generate_creative_pack("klichki", "funny", ["bacon"])
    assert len(result.items) == 15


def test_english_only_output():
    result = generate_creative_pack("klichki", "neutral", [])
    assert all(re.match(r"^[a-zA-Z0-9_.\-]+$", item) for item in result.items)


def test_svino_category():
    result = generate_creative_pack("klichki", "svino", [])
    assert len(result.items) == 15


def test_build_prompt_gaming_style():
    from app.services.creative_ai import _build_prompt

    prompt = _build_prompt(
        kind="social",
        category_id="gaming",
        seeds=["trashcorp"],
        item_count=10,
        bio_count=3,
    )
    assert "Игровой" in prompt
    assert "id=gaming" in prompt
    assert "MUST NOT: pig/oink/bacon" in prompt
    assert "киберспорт" in prompt.lower() or "esports" in prompt.lower()
    assert "пафос киберспортсмена" in prompt
    assert "REQUIRED: at least" in prompt
    assert "trashcorp" in prompt


def test_pack_requires_anchor_usage():
    from app.services.creative_ai import _pack_quality_issue

    generic = [
        "SirOopsALot", "MemeAccountant", "ChaosHam", "QuirkyQuokka",
        "WhimsicalWombat", "GigglyGiraffe", "NuttyNarwhal", "SillySealSaga",
        "PunnyPenguin", "JestingJellyfish", "ZanyZebra", "BaconBandit",
        "OopsAllOink", "NuttyNinja", "SillySocks",
    ]
    issue = _pack_quality_issue(generic, ["irishka"])
    assert issue and "anchor" in issue.lower()

    with_anchor = [
        "IrishkaRiddle", "PunIrishka", "SirIrishka", "irishka_jokes", "RiddleIrishka",
        "ChaosHam", "MemeAccountant", "SirOopsALot", "QuirkyQuokka", "NuttyNarwhal",
        "SillySealSaga", "PunnyPenguin", "ZanyZebra", "BaconBandit", "OopsAllOink",
    ]
    assert _pack_quality_issue(with_anchor, ["irishka"]) is None


def test_build_prompt_svino_differs_from_gaming():
    from app.services.creative_ai import _build_prompt

    gaming = _build_prompt(
        kind="nicknames",
        category_id="gaming",
        seeds=[],
        item_count=15,
        bio_count=0,
    )
    svino = _build_prompt(
        kind="nicknames",
        category_id="svino",
        seeds=[],
        item_count=15,
        bio_count=0,
    )
    assert "pig-meme" in svino
    assert "Never default to pig" not in svino
    assert gaming != svino


def test_parse_ai_json():
    from app.services.creative_ai import (
        _has_cyrillic,
        _is_lazy_nick,
        _pack_quality_issue,
        _parse_response,
        _sanitize_nick,
        _validate_bios,
        _validate_items,
    )

    payload = _parse_response('{"items": ["1. TrashBacon", "NeonKhryak"], "bios": []}')
    items = _validate_items(
        payload["items"],
        count=2,
        seeds=["trash"],
        must_contain_seed=False,
    )
    assert items == ["TrashBacon", "NeonKhryak"]
    assert _sanitize_nick("1. TrashStorm") == "TrashStorm"
    assert _is_lazy_nick("TrashVibe", ["trash"])
    assert not _is_lazy_nick("TrashBacon", ["trash"])
    assert _pack_quality_issue(
        [f"Trash{x}" for x in ("Vibe", "Glow", "Nova", "Edge", "Pulse")],
        ["trash"],
    )
    bios = _validate_bios(
        ["Making content until 3am", "Мемы, кофе и хаос", "Ещё одно русское био"],
        2,
    )
    assert len(bios) == 2
    assert all(_has_cyrillic(bio) for bio in bios)
