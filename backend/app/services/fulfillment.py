import logging
import uuid

from sqlalchemy.orm import Session

from app.repositories import order_repo
from app.services.backup_codes import generate_backup_codes
from app.services.creative import CREATIVE_WARNING, generate_creative_pack
from app.services.email import (
    send_backup_codes_email,
    send_creative_email,
    send_image_qr_email,
    send_password_email,
    send_seller_email,
)
from app.services.image_hosting import (
    create_image_token,
    store_hosted_image,
)
from app.services.public_urls import build_image_qr_page_url
from app.services.seller_content import SELLER_WARNING, generate_seller_pack
from app.services.seller_staging import pop_sell_image
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
IMAGE_QR_WARNING = (
    "Сохраните QR и ссылку сейчас. Картинка будет доступна по ссылке 30 дней — "
    "только изображение, без видео и аудио."
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

    if product_type == "image_qr":
        options = order.order_options or {}
        staging_id = options.get("staging_id")
        if not staging_id:
            raise ValueError("Image QR order missing staging_id")
        staged = pop_sell_image(staging_id)
        if not staged:
            raise ValueError("Image expired or missing")

        host_days = tier.get("host_days", 30)
        ttl_seconds = int(host_days) * 24 * 3600
        token = create_image_token()
        expires_at = store_hosted_image(
            token,
            mime=staged["mime"],
            data_b64=staged["data"],
            ttl_seconds=ttl_seconds,
        )
        page_url = build_image_qr_page_url(token)
        expires_label = expires_at.strftime("%d.%m.%Y")
        email_sent = send_image_qr_email(
            to=order.email,
            tier_name=tier["name"],
            order_id=str(order.id),
            page_url=page_url,
            expires_label=expires_label,
        )
        if not email_sent:
            logger.error("Image QR email delivery failed for order %s", order.id)
        store_fulfillment(
            str(order.id),
            {
                "order_id": str(order.id),
                "tier": order.tier,
                "tier_name": tier["name"],
                "product_type": "image_qr",
                "image_qr_url": page_url,
                "image_qr_token": token,
                "image_qr_expires_at": expires_at.isoformat(),
                "email_sent": email_sent,
                "warning": IMAGE_QR_WARNING,
            },
        )
        order_repo.mark_fulfilled(db, order, email_sent=email_sent)
        return

    if product_type == "seller":
        options = order.order_options or {}
        staging_id = options.get("staging_id")
        if not staging_id:
            raise ValueError("Seller order missing staging_id")
        staged = pop_sell_image(staging_id)
        if not staged:
            raise ValueError("Seller photo expired or missing")

        result = generate_seller_pack(
            order.tier,
            image_b64=staged["data"],
            mime=staged["mime"],
            product_name=options.get("product_name", ""),
            product_category=options.get("product_category", ""),
            product_hints=options.get("product_hints", ""),
        )
        email_sent = send_seller_email(
            to=order.email,
            cards=result.cards,
            vision_summary=result.vision_summary,
            tier_name=tier["name"],
            order_id=str(order.id),
        )
        if not email_sent:
            logger.error("Seller email delivery failed for order %s", order.id)
        store_fulfillment(
            str(order.id),
            {
                "order_id": str(order.id),
                "tier": order.tier,
                "tier_name": tier["name"],
                "product_type": "seller",
                "seller_cards": result.cards,
                "seller_vision_summary": result.vision_summary,
                "seller_source": result.source,
                "email_sent": email_sent,
                "warning": SELLER_WARNING,
            },
        )
        order_repo.mark_fulfilled(db, order, email_sent=email_sent)
        return

    if product_type == "creative":
        options = order.order_options or {}
        category = options.get("category", "neutral")
        seed_words = options.get("seed_words", [])
        result = generate_creative_pack(order.tier, category, seed_words)
        email_sent = send_creative_email(
            to=order.email,
            items=result.items,
            bios=result.bios,
            tier_name=tier["name"],
            order_id=str(order.id),
            kind=result.kind,
            category=result.category,
        )
        if not email_sent:
            logger.error("Creative email delivery failed for order %s", order.id)
        store_fulfillment(
            str(order.id),
            {
                "order_id": str(order.id),
                "tier": order.tier,
                "tier_name": tier["name"],
                "product_type": "creative",
                "creative_items": result.items,
                "creative_bios": result.bios,
                "creative_category": result.category,
                "creative_kind": result.kind,
                "creative_source": result.source,
                "email_sent": email_sent,
                "warning": CREATIVE_WARNING,
            },
        )
        order_repo.mark_fulfilled(db, order, email_sent=email_sent)
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
