from decimal import Decimal
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

from yookassa import Configuration, Payment

from app.config import settings
from app.db.models import Order


def _configure() -> None:
    Configuration.account_id = settings.yookassa_shop_id
    Configuration.secret_key = settings.yookassa_secret_key


def build_return_url(order_id: str) -> str:
    parsed = urlparse(settings.yookassa_return_url)
    query = dict(parse_qsl(parsed.query))
    query["order_id"] = order_id
    return urlunparse(parsed._replace(query=urlencode(query)))


def build_receipt(email: str, tier: dict) -> dict:
    amount = f"{tier['price']:.2f}"
    return {
        "email": email,
        "items": [
            {
                "description": tier["name"][:128],
                "quantity": "1.00",
                "amount": {"value": amount, "currency": "RUB"},
                "vat_code": 1,
                "payment_mode": "full_payment",
                "payment_subject": "service",
            }
        ],
    }


def create_payment(order: Order, tier: dict, email: str) -> tuple[str, str]:
    _configure()
    amount = f"{tier['price']:.2f}"
    return_url = build_return_url(str(order.id))

    payment = Payment.create(
        {
            "amount": {"value": amount, "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": f"Svinopass: {tier['name']}"[:128],
            "metadata": {"order_id": str(order.id)},
            "receipt": build_receipt(email, tier),
        },
        order.idempotence_key,
    )

    payment_id = payment.id
    confirmation_url = payment.confirmation.confirmation_url
    return payment_id, confirmation_url


def get_payment_status(payment_id: str) -> str:
    _configure()
    payment = Payment.find_one(payment_id)
    return payment.status
