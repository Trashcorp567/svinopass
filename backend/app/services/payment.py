from sqlalchemy.orm import Session

from app.db.models import Order
from app.repositories import order_repo

TIERS: dict[str, dict] = {
    "svinomat": {
        "id": "svinomat",
        "name": "\u0421\u0432\u0438\u043d\u043e\u043c\u0430\u0442",
        "price": 99,
        "price_label": "99\u20bd",
        "description": "Разовая услуга: 1 пароль, 20 символов (буквы и цифры), доставка на экран и email",
        "length": 20,
        "product_type": "password",
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
        "description": "Разовая услуга: 1 пароль, 24 символа со спецсимволами, для важных аккаунтов",
        "length": 24,
        "product_type": "password",
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
        "description": "Разовая услуга: 1 пароль, 32 символа, максимальная энтропия",
        "length": 32,
        "product_type": "password",
        "features": [
            "32 \u0441\u0438\u043c\u0432\u043e\u043b\u0430",
            "\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430 \u0441\u043b\u0430\u0431\u044b\u0445 \u043f\u0430\u0442\u0442\u0435\u0440\u043d\u043e\u0432",
            "\u041e\u0442\u043f\u0440\u0430\u0432\u043a\u0430 \u043d\u0430 email",
        ],
    },
    "backup": {
        "id": "backup",
        "name": "\u0417\u0430\u043f\u0430\u0441\u043d\u043e\u0439 \u0445\u043b\u0435\u0432",
        "price": 149,
        "price_label": "149\u20bd",
        "description": "10 одноразовых кодов восстановления (2FA backup)",
        "length": 10,
        "product_type": "backup_codes",
        "features": [
            "10 \u043a\u043e\u0434\u043e\u0432 \u043f\u043e 10 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432",
            "CSPRNG, \u0431\u0435\u0437 \u043d\u0435\u043e\u0434\u043d\u043e\u0437\u043d\u0430\u0447\u043d\u044b\u0445 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432",
            "\u041e\u0442\u043f\u0440\u0430\u0432\u043a\u0430 \u043d\u0430 email",
        ],
    },
    "storozh": {
        "id": "storozh",
        "name": "Свиной сторож",
        "price": 199,
        "price_label": "199₽/мес",
        "description": "Мониторинг email в публичных утечках — уведомление раз в неделю",
        "length": 0,
        "product_type": "watch",
        "return_path": "/watch/success",
        "features": [
            "Проверка через LeakCheck",
            "Письмо при новых утечках",
            "30 дней мониторинга за оплату",
        ],
    },
}


def get_tier(tier_id: str) -> dict | None:
    return TIERS.get(tier_id)


def get_all_tiers() -> list[dict]:
    return list(TIERS.values())


def create_paid_order(
    db: Session, email: str, tier_id: str, generation_mode: str = "random"
) -> Order:
    tier = get_tier(tier_id)
    if not tier:
        raise ValueError(f"Unknown tier: {tier_id}")
    if tier["price"] <= 0:
        raise ValueError("Tier is not available for purchase")
    if tier.get("product_type") != "watch" and generation_mode not in {"random", "passphrase"}:
        raise ValueError("Invalid generation mode")
    return order_repo.create_pending_order(
        db,
        email=email,
        tier=tier_id,
        price_rub=tier["price"],
        generation_mode=generation_mode,
    )