import logging
import uuid

from sqlalchemy.orm import Session

from app.repositories import order_repo
from app.services.backup_codes import generate_backup_codes
from app.services.email import send_backup_codes_email, send_password_email
from app.services.ephemeral import store_fulfillment, store_report_meta
from app.services.passphrase import generate_passphrase, passphrase_entropy_for_display
from app.services.password import estimate_entropy_bits, generate_password
from app.services.payment import get_tier
from app.services.uniqueness import claim_unique
from app.services.watch_service import activate_watch_for_order

logger = logging.getLogger(__name__)

PASSWORD_WARNING = (
    "Сохраните пароль сейчас — мы его не храним и не сможем восстановить."
)
BACKUP_WARNING = (
    "Сохраните коды офлайн — мы их не храним и не сможем восстановить."
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

    product_type = tier.get("product_type", "password")

    if product_type == "backup_codes":
        codes = generate_backup_codes()
        email_sent = send_backup_codes_email(
            to=order.email,
            codes=codes,
            tier_name=tier["name"],
            order_id=str(order.id),
        )
        if not email_sent:
            logger.error("Backup codes email delivery failed for order %s", order.id)
        store_fulfillment(
            str(order.id),
            {
                "order_id": str(order.id),
                "tier": order.tier,
                "tier_name": tier["name"],
                "product_type": "backup_codes",
                "backup_codes": codes,
                "email_sent": email_sent,
                "warning": BACKUP_WARNING,
            },
        )
        order_repo.mark_fulfilled(db, order, email_sent=email_sent)
        return

    if product_type == "watch":
        payload = activate_watch_for_order(db, email=order.email, order_id=order.id)
        store_fulfillment(
            str(order.id),
            {
                "order_id": str(order.id),
                "tier": order.tier,
                "tier_name": tier["name"],
                "product_type": "watch",
                "email_sent": payload["email_sent"],
                "warning": payload["warning"],
                "monitored_email": payload["monitored_email"],
                "expires_at": payload["expires_at"],
                "breach_count": payload["breach_count"],
                "breaches": payload["breaches"],
            },
        )
        order_repo.mark_fulfilled(db, order, email_sent=payload["email_sent"])
        return

    if order.generation_mode == "passphrase":
        password = claim_unique(generate_passphrase)
        entropy_bits = passphrase_entropy_for_display(password)
    else:
        password = claim_unique(generate_password, order.tier, tier["length"])
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
            "product_type": "password",
            "password": password,
            "entropy_bits": entropy_bits,
            "email_sent": email_sent,
            "warning": PASSWORD_WARNING,
        },
    )
    if order.tier == "legend":
        store_report_meta(
            str(order.id),
            {
                "entropy_bits": entropy_bits,
                "password_length": len(password),
                "generation_mode": order.generation_mode,
            },
        )
    order_repo.mark_fulfilled(db, order, email_sent=email_sent)
