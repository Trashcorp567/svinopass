import base64
import pytest

from app.config import settings
from app.services.seller_content import generate_seller_pack
from app.services.seller_platforms import validate_seller_checkout
from app.services.seller_staging import store_sell_image, pop_sell_image, create_staging_id
from app.services.payment import get_tier


# 1x1 PNG
TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)
TINY_PNG_B64 = base64.b64encode(TINY_PNG).decode("ascii")


@pytest.fixture
def disable_seller_ai(monkeypatch):
    monkeypatch.setattr(settings, "yandex_gpt_api_key", "")
    monkeypatch.setattr(settings, "yandex_gpt_folder_id", "")


def test_validate_seller_checkout_requires_staging():
    tier = get_tier("ozon_card")
    assert tier is not None
    with pytest.raises(ValueError, match="photo"):
        validate_seller_checkout(
            tier,
            staging_id=None,
            product_name="Кружка",
            product_category="Посуда",
            product_hints="450 мл",
        )


def test_generate_seller_pack_fallback(disable_seller_ai):
    result = generate_seller_pack(
        "ozon_card",
        image_b64=TINY_PNG_B64,
        mime="image/png",
        product_name="Термокружка",
        product_category="Посуда",
        product_hints="Сохраняет тепло 6 часов",
    )
    assert result.source == "template"
    assert len(result.cards) == 1
    assert result.cards[0]["platform"] == "ozon"
    assert len(result.cards[0]["titles"]) == 5
    assert len(result.cards[0]["description"]) >= 80
    assert all("вариант" not in title.lower() for title in result.cards[0]["titles"])


def test_sell_pack_has_three_platforms(disable_seller_ai):
    result = generate_seller_pack(
        "sell_pack",
        image_b64=TINY_PNG_B64,
        mime="image/png",
        product_name="Наушники",
        product_category="Электроника",
        product_hints="Bluetooth 5.3",
    )
    platforms = {card["platform"] for card in result.cards}
    assert platforms == {"ozon", "wb", "avito"}


def test_staging_roundtrip():
    staging_id = create_staging_id()
    store_sell_image(staging_id, mime="image/png", data_b64=TINY_PNG_B64)
    payload = pop_sell_image(staging_id)
    assert payload is not None
    assert payload["mime"] == "image/png"
    assert pop_sell_image(staging_id) is None
