from sqlalchemy.orm import Session

from app.db.models import Order
from app.repositories import order_repo

TIERS: dict[str, dict] = {
    "svinomat": {
        "id": "svinomat",
        "name": "\u0421\u0432\u0438\u043d\u043e\u043c\u0430\u0442",
        "price": 99,
        "price_label": "99\u20bd",
        "description": "\u041d\u0430\u0434\u0451\u0436\u043d\u044b\u0439 \u043f\u0430\u0440\u043e\u043b\u044c \u0434\u043b\u044f \u043f\u043e\u0432\u0441\u0435\u0434\u043d\u0435\u0432\u043d\u044b\u0445 \u0441\u0435\u0440\u0432\u0438\u0441\u043e\u0432",
        "length": 20,
        "features": [
            "20 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432 CSPRNG",
            "\u0411\u0443\u043a\u0432\u044b \u0438 \u0446\u0438\u0444\u0440\u044b",
            "\u041e\u0442\u043f\u0440\u0430\u0432\u043a\u0430 \u043d\u0430 email",
        ],
    },
    "bacon": {
        "id": "bacon",
        "name": "\u0411\u0435\u043a\u043e\u043d Pro",
        "price": 499,
        "price_label": "499\u20bd",
        "description": "\u0414\u043b\u044f \u0431\u0430\u043d\u043a\u043e\u0432 \u0438 \u0432\u0430\u0436\u043d\u044b\u0445 \u0430\u043a\u043a\u0430\u0443\u043d\u0442\u043e\u0432",
        "length": 24,
        "features": [
            "24 \u0441\u0438\u043c\u0432\u043e\u043b\u0430 + \u0441\u043f\u0435\u0446\u0441\u0438\u043c\u0432\u043e\u043b\u044b",
            "\u0413\u0430\u0440\u0430\u043d\u0442\u0438\u044f \u0440\u0435\u0433\u0438\u0441\u0442\u0440\u043e\u0432",
            "\u041e\u0442\u043f\u0440\u0430\u0432\u043a\u0430 \u043d\u0430 email",
        ],
    },
    "legend": {
        "id": "legend",
        "name": "\u041b\u0435\u0433\u0435\u043d\u0434\u0430 \u0445\u0440\u044e\u0448\u0438",
        "price": 1999,
        "price_label": "1999\u20bd",
        "description": "\u041c\u0430\u043a\u0441\u0438\u043c\u0430\u043b\u044c\u043d\u0430\u044f \u044d\u043d\u0442\u0440\u043e\u043f\u0438\u044f",
        "length": 32,
        "features": [
            "32 \u0441\u0438\u043c\u0432\u043e\u043b\u0430",
            "\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0441\u043b\u0430\u0431\u044b\u0445 \u043f\u0430\u0442\u0442\u0435\u0440\u043d\u043e\u0432",
            "\u041e\u0442\u043f\u0440\u0430\u0432\u043a\u0430 \u043d\u0430 email",
        ],
    },
}


def get_tier(tier_id: str) -> dict | None:
    return TIERS.get(tier_id)


def get_all_tiers() -> list[dict]:
    return list(TIERS.values())


def create_paid_order(db: Session, email: str, tier_id: str) -> Order:
    tier = get_tier(tier_id)
    if not tier:
        raise ValueError(f"Unknown tier: {tier_id}")
    if tier["price"] <= 0:
        raise ValueError("Tier is not available for purchase")
    return order_repo.create_pending_order(
        db, email=email, tier=tier_id, price_rub=tier["price"]
    )