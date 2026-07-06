import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from yookassa.domain.common import SecurityHelper
from yookassa.domain.notification import WebhookNotificationEventType, WebhookNotificationFactory

from app.api.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    HealthResponse,
    OrderPendingResponse,
    OrderResultResponse,
    TierInfo,
)
from app.config import settings
from app.db.database import get_db
from app.repositories import order_repo
from app.services.ephemeral import pop_fulfillment
from app.services.fulfillment import fulfill_order
from app.services.payment import create_paid_order, get_all_tiers, get_tier
from app.services.yookassa_client import build_return_url, create_payment, get_payment_status

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address, enabled=settings.env == "production")
router = APIRouter(prefix="/api")


def _sync_pending_payment_in_dev(db: Session, order) -> None:
    if (
        settings.yookassa_mock
        or settings.env != "development"
        or order.status != "pending"
        or not order.yookassa_payment_id
        or not settings.yookassa_shop_id
        or not settings.yookassa_secret_key
    ):
        return
    try:
        status = get_payment_status(order.yookassa_payment_id)
        if status == "succeeded":
            order_repo.mark_paid(db, order)
            fulfill_order(db, order.id)
    except Exception:
        logger.exception("Dev YooKassa payment sync failed for order %s", order.id)


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", service="svinopass")


@router.get("/tiers", response_model=list[TierInfo])
async def tiers():
    return [TierInfo(**t) for t in get_all_tiers()]


@router.post("/checkout", response_model=CheckoutResponse)
@limiter.limit("5/minute")
async def checkout(
    request: Request,
    body: CheckoutRequest,
    db: Session = Depends(get_db),
):
    tier = get_tier(body.tier)
    if not tier:
        raise HTTPException(status_code=400, detail="Unknown tier")
    if tier["price"] <= 0:
        raise HTTPException(status_code=400, detail="Tier is not for sale")

    try:
        order = create_paid_order(db, body.email, body.tier)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if settings.yookassa_mock:
        order_repo.mark_paid(db, order)
        fulfill_order(db, order.id)
        return CheckoutResponse(
            order_id=str(order.id),
            confirmation_url=build_return_url(str(order.id)),
        )

    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        raise HTTPException(status_code=503, detail="Payment provider not configured")

    try:
        payment_id, confirmation_url = create_payment(order, tier, body.email)
    except Exception as exc:
        logger.exception("YooKassa payment creation failed")
        raise HTTPException(status_code=502, detail=f"Payment creation failed: {exc}") from exc

    order_repo.set_yookassa_payment_id(db, order, payment_id)
    return CheckoutResponse(order_id=str(order.id), confirmation_url=confirmation_url)


@router.get("/orders/{order_id}/result", response_model=OrderResultResponse | OrderPendingResponse)
async def order_result(order_id: str, db: Session = Depends(get_db)):
    try:
        oid = UUID(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid order_id") from exc

    order = order_repo.get_by_id(db, oid)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    _sync_pending_payment_in_dev(db, order)
    db.refresh(order)

    if order.status != "paid" or order.fulfilled_at is None:
        return OrderPendingResponse(order_id=order_id)

    payload = pop_fulfillment(order_id)
    if not payload:
        raise HTTPException(
            status_code=410,
            detail="Password already shown. Check your email.",
        )

    tier = get_tier(order.tier)
    return OrderResultResponse(
        order_id=order_id,
        tier=order.tier,
        tier_name=tier["name"] if tier else order.tier,
        password=payload["password"],
        entropy_bits=payload["entropy_bits"],
        email_sent=payload["email_sent"],
        paid_at=order.paid_at,
        warning=payload.get(
            "warning",
            "Сохраните пароль сейчас — мы его не храним и не сможем восстановить.",
        ),
    )


@router.post("/webhooks/yookassa")
async def yookassa_webhook(request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else ""
    if not settings.yookassa_mock and settings.env != "development":
        if not SecurityHelper().is_ip_trusted(client_ip):
            logger.warning("Untrusted webhook IP: %s", client_ip)
            raise HTTPException(status_code=403, detail="Forbidden")

    try:
        body = await request.json()
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    try:
        notification = WebhookNotificationFactory().create(body)
    except Exception as exc:
        logger.exception("Webhook parse failed")
        raise HTTPException(status_code=400, detail="Invalid notification") from exc

    event = notification.event
    payment = notification.object

    if event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
        order_id_str = payment.metadata.get("order_id") if payment.metadata else None
        order = None
        if order_id_str:
            try:
                order = order_repo.get_by_id(db, UUID(order_id_str))
            except ValueError:
                order = None
        if not order:
            order = order_repo.get_by_yookassa_payment_id(db, payment.id)
        if order and order.status != "paid":
            order_repo.mark_paid(db, order)
        if order:
            fulfill_order(db, order.id)

    elif event == WebhookNotificationEventType.PAYMENT_CANCELED:
        order = order_repo.get_by_yookassa_payment_id(db, payment.id)
        if order and order.status == "pending":
            order_repo.mark_canceled(db, order)

    return {"status": "ok"}
