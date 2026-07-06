import logging
import uuid

from sqlalchemy.orm import Session

from app.repositories import order_repo
from app.services.email import send_password_email
from app.services.ephemeral import store_fulfillment
from app.services.password import estimate_entropy_bits, generate_password
from app.services.payment import get_tier

logger = logging.getLogger(__name__)

WARNING_TEXT = (
    "Сохраните пароль сейчас — мы его не храним и не сможем восстановить."
)


def fulfill_order(db: Session, order_id: uuid.UUID) -> None:
    order = order_repo.get_by_id(db, order_id)
    if not order:
        raise ValueError("Order not found")
    if order.fulfilled_at is not None:
        return

    tier = get_tier(order.tier)
    if not tier:
        raise ValueError("Unknown tier")

    password = generate_password(order.tier, tier["length"])
    entropy_bits = estimate_entropy_bits(password)

    email_sent = send_password_email(
        to=order.email,
        password=password,
        tier_name=tier["name"],
        order_id=str(order.id),
    )

    if not email_sent:
        logger.error("Email delivery failed for order %s", order.id)

    store_fulfillment(
        str(order.id),
        {
            "order_id": str(order.id),
            "tier": order.tier,
            "tier_name": tier["name"],
            "password": password,
            "entropy_bits": entropy_bits,
            "email_sent": email_sent,
            "warning": WARNING_TEXT,
        },
    )
    order_repo.mark_fulfilled(db, order, email_sent=email_sent)
