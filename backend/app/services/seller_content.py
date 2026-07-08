import logging
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger(__name__)
from app.services.payment import get_tier
from app.services.seller_ai import generate_seller_cards_ai, generate_seller_cards_fallback
from app.services.seller_platforms import platforms_for_tier

SELLER_WARNING = (
    "Сохраните тексты сейчас — мы их не храним. "
    "Проверьте факты, габариты и комплектацию перед публикацией на маркетплейсе."
)


@dataclass
class SellerPackResult:
    vision_summary: str
    cards: list[dict]
    source: str


def generate_seller_pack(
    tier_id: str,
    *,
    image_b64: str,
    mime: str,
    product_name: str,
    product_category: str,
    product_hints: str,
) -> SellerPackResult:
    tier = get_tier(tier_id)
    if not tier or tier.get("product_type") != "seller":
        raise ValueError("Not a seller tier")

    platforms = platforms_for_tier(tier)
    if not platforms:
        raise ValueError("Seller platform is not configured")

    if settings.yandex_gpt_api_key and settings.yandex_gpt_folder_id and image_b64:
        try:
            vision_summary, cards = generate_seller_cards_ai(
                platforms=platforms,
                image_b64=image_b64,
                mime=mime,
                product_name=product_name,
                product_category=product_category,
                product_hints=product_hints,
            )
            return SellerPackResult(
                vision_summary=vision_summary,
                cards=cards,
                source="yandexgpt",
            )
        except Exception as exc:
            logger.warning("Seller AI generation failed, using template: %s", exc)

    vision_summary, cards = generate_seller_cards_fallback(
        platforms=platforms,
        product_name=product_name,
        product_category=product_category,
        product_hints=product_hints,
    )
    return SellerPackResult(
        vision_summary=vision_summary,
        cards=cards,
        source="template",
    )
