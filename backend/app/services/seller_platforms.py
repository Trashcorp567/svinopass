from dataclasses import dataclass


@dataclass(frozen=True)
class SellerPlatform:
    id: str
    label: str
    title_max: int
    description_max: int
    title_count: int = 5


PLATFORMS: dict[str, SellerPlatform] = {
    "ozon": SellerPlatform(
        id="ozon",
        label="Ozon",
        title_max=200,
        description_max=6000,
    ),
    "wb": SellerPlatform(
        id="wb",
        label="Wildberries",
        title_max=60,
        description_max=5000,
    ),
    "avito": SellerPlatform(
        id="avito",
        label="Avito",
        title_max=50,
        description_max=7500,
    ),
}


def get_platform(platform_id: str) -> SellerPlatform | None:
    return PLATFORMS.get(platform_id)


def list_platforms() -> list[SellerPlatform]:
    return list(PLATFORMS.values())


def platforms_for_tier(tier: dict) -> list[SellerPlatform]:
    platform_key = tier.get("platform", "ozon")
    if platform_key == "all":
        return list_platforms()
    platform = get_platform(platform_key)
    return [platform] if platform else []


def validate_seller_checkout(
    tier: dict,
    *,
    staging_id: str | None,
    product_name: str | None,
    product_category: str | None,
    product_hints: str | None,
) -> dict:
    if tier.get("product_type") != "seller":
        raise ValueError("Not a seller tier")
    if not staging_id or not staging_id.strip():
        raise ValueError("Product photo is required")
    if not platforms_for_tier(tier):
        raise ValueError("Unknown seller platform")
    name = (product_name or "").strip()[:120]
    category = (product_category or "").strip()[:120]
    hints = (product_hints or "").strip()[:500]
    return {
        "staging_id": staging_id.strip(),
        "product_name": name,
        "product_category": category,
        "product_hints": hints,
    }
