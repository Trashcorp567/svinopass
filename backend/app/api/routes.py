import base64
import json
import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import Response
from slowapi import Limiter
from sqlalchemy.orm import Session
from yookassa.domain.common import SecurityHelper
from yookassa.domain.notification import WebhookNotificationEventType, WebhookNotificationFactory

from app.api.schemas import (
    BreachSummary,
    CheckoutRequest,
    CheckoutResponse,
    CreativeCategoryInfo,
    HealthResponse,
    OrderPendingResponse,
    OrderResultResponse,
    SellStageResponse,
    SellerPlatformInfo,
    TierInfo,
    WatchPreviewRequest,
    WatchPreviewResponse,
)
from app.config import settings
from app.http import client_ip
from app.db.database import get_db
from app.repositories import order_repo
from app.services.ephemeral import get_report_meta, pop_fulfillment
from app.services.fulfillment import fulfill_order
from app.services.payment import create_paid_order, get_all_tiers, get_tier
from app.services.image_hosting import get_hosted_image, validate_image_qr_checkout
from app.services.seller_platforms import list_platforms, validate_seller_checkout
from app.services.seller_staging import (
    ALLOWED_MIME,
    MAX_IMAGE_BYTES,
    SELL_STAGING_TTL_SECONDS,
    create_staging_id,
    peek_sell_image,
    store_sell_image,
)
from app.services.report_pdf import build_svino_report_pdf
from app.services.yookassa_client import build_return_url, create_payment, get_payment_status
from app.services.breach_client import breach_to_dict, fetch_email_breaches
from app.services.creative_categories import list_categories
from app.services.watch_service import run_due_watch_checks

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=client_ip, enabled=settings.env == "production")
router = APIRouter(prefix="/api")


def _sync_pending_payment(db: Session, order) -> None:
    if (
        settings.yookassa_mock
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
        logger.exception("YooKassa payment sync failed for order %s", order.id)


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", service="svinopass")


@router.get("/tiers", response_model=list[TierInfo])
async def tiers():
    return [TierInfo(**t) for t in get_all_tiers()]


@router.get("/creative/categories", response_model=list[CreativeCategoryInfo])
async def creative_categories():
    return [CreativeCategoryInfo(**c.__dict__) for c in list_categories()]


@router.get("/sell/platforms", response_model=list[SellerPlatformInfo])
async def sell_platforms():
    return [
        SellerPlatformInfo(
            id=p.id,
            label=p.label,
            title_max=p.title_max,
            description_max=p.description_max,
            title_count=p.title_count,
        )
        for p in list_platforms()
    ]


@router.post("/sell/stage", response_model=SellStageResponse)
@limiter.limit("30/hour")
async def sell_stage(request: Request, file: UploadFile = File(...)):
    content_type = file.content_type or ""
    if content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Поддерживаются JPEG, PNG и WebP")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Пустой файл")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="Фото до 5 МБ")

    staging_id = create_staging_id()
    store_sell_image(
        staging_id,
        mime=content_type,
        data_b64=base64.b64encode(data).decode("ascii"),
    )
    return SellStageResponse(staging_id=staging_id, expires_in=SELL_STAGING_TTL_SECONDS)


@router.post("/image/stage", response_model=SellStageResponse)
@limiter.limit("30/hour")
async def image_stage(request: Request, file: UploadFile = File(...)):
    return await sell_stage(request, file)


@router.get("/public/images/{token}")
@limiter.limit("120/hour")
async def public_image(token: str, request: Request):
    payload = get_hosted_image(token)
    if not payload:
        raise HTTPException(status_code=404, detail="Image not found or expired")
    try:
        data = base64.b64decode(payload["data"])
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=404, detail="Image unavailable") from exc
    mime = payload.get("mime", "image/jpeg")
    if mime not in ALLOWED_MIME:
        raise HTTPException(status_code=404, detail="Image unavailable")
    return Response(content=data, media_type=mime, headers={"Cache-Control": "public, max-age=3600"})


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

    product_type = tier.get("product_type", "password")
    order_options: dict | None = None
    generation_mode = body.mode

    if product_type == "creative":
        if not body.category:
            raise HTTPException(status_code=400, detail="Category is required for creative tiers")
        try:
            category, seed_words = validate_creative_checkout(body.category, body.seed_words)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        order_options = {"category": category, "seed_words": seed_words}
        generation_mode = "random"
    elif product_type == "seller":
        try:
            order_options = validate_seller_checkout(
                tier,
                staging_id=body.staging_id,
                product_name=body.product_name,
                product_category=body.product_category,
                product_hints=body.product_hints,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if not peek_sell_image(order_options["staging_id"]):
            raise HTTPException(status_code=400, detail="Фото устарело — загрузите снова")
        generation_mode = "random"
    elif product_type == "image_qr":
        try:
            order_options = validate_image_qr_checkout(tier, staging_id=body.staging_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if not peek_sell_image(order_options["staging_id"]):
            raise HTTPException(status_code=400, detail="Картинка устарела — загрузите снова")
        generation_mode = "random"
    elif product_type != "password":
        generation_mode = "random"

    try:
        order = create_paid_order(
            db,
            body.email,
            body.tier,
            generation_mode,
            order_options=order_options,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if settings.yookassa_mock:
        order_repo.mark_paid(db, order)
        fulfill_order(db, order.id)
        return CheckoutResponse(
            order_id=str(order.id),
            confirmation_url=build_return_url(str(order.id), tier.get("return_path")),
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

    _sync_pending_payment(db, order)
    db.refresh(order)

    if order.status == "paid" and order.fulfilled_at is None:
        try:
            fulfill_order(db, order.id)
            db.refresh(order)
        except Exception:
            logger.exception("Fulfillment retry failed for order %s", order.id)

    if order.status != "paid" or order.fulfilled_at is None:
        return OrderPendingResponse(order_id=order_id)

    tier = get_tier(order.tier)
    payload = pop_fulfillment(order_id)
    if not payload:
        if order.tier == "storozh":
            detail = "Subscription details already shown. Check your email."
        elif tier and tier.get("product_type") == "creative":
            detail = "Creative pack already shown. Check your email."
        elif tier and tier.get("product_type") == "seller":
            detail = "Seller pack already shown. Check your email."
        elif tier and tier.get("product_type") == "image_qr":
            detail = "Image QR already shown. Check your email."
        else:
            detail = "Password already shown. Check your email."
        raise HTTPException(status_code=410, detail=detail)

    product_type = payload.get("product_type", "password")
    if product_type == "backup_codes":
        return OrderResultResponse(
            order_id=order_id,
            tier=order.tier,
            tier_name=tier["name"] if tier else order.tier,
            product_type="backup_codes",
            backup_codes=payload.get("backup_codes", []),
            email_sent=payload["email_sent"],
            paid_at=order.paid_at,
            warning=payload.get("warning", "Сохраните коды офлайн."),
        )
    if product_type == "watch":
        return OrderResultResponse(
            order_id=order_id,
            tier=order.tier,
            tier_name=tier["name"] if tier else order.tier,
            product_type="watch",
            monitored_email=payload.get("monitored_email"),
            expires_at=payload.get("expires_at"),
            breach_count=payload.get("breach_count"),
            breaches=payload.get("breaches"),
            email_sent=payload["email_sent"],
            paid_at=order.paid_at,
            warning=payload.get("warning", "Мониторинг активен."),
        )
    if product_type == "creative":
        return OrderResultResponse(
            order_id=order_id,
            tier=order.tier,
            tier_name=tier["name"] if tier else order.tier,
            product_type="creative",
            creative_items=payload.get("creative_items", []),
            creative_bios=payload.get("creative_bios", []),
            creative_category=payload.get("creative_category"),
            creative_kind=payload.get("creative_kind"),
            creative_source=payload.get("creative_source"),
            email_sent=payload["email_sent"],
            paid_at=order.paid_at,
            warning=payload.get("warning", "Сохраните варианты сейчас."),
        )
    if product_type == "seller":
        return OrderResultResponse(
            order_id=order_id,
            tier=order.tier,
            tier_name=tier["name"] if tier else order.tier,
            product_type="seller",
            seller_cards=payload.get("seller_cards", []),
            seller_vision_summary=payload.get("seller_vision_summary"),
            seller_source=payload.get("seller_source"),
            email_sent=payload["email_sent"],
            paid_at=order.paid_at,
            warning=payload.get("warning", "Сохраните тексты сейчас."),
        )
    if product_type == "image_qr":
        expires_raw = payload.get("image_qr_expires_at")
        expires_at = datetime.fromisoformat(expires_raw) if expires_raw else None
        return OrderResultResponse(
            order_id=order_id,
            tier=order.tier,
            tier_name=tier["name"] if tier else order.tier,
            product_type="image_qr",
            image_qr_url=payload.get("image_qr_url"),
            image_qr_expires_at=expires_at,
            email_sent=payload["email_sent"],
            paid_at=order.paid_at,
            warning=payload.get("warning", "Сохраните QR и ссылку сейчас."),
        )
    return OrderResultResponse(
        order_id=order_id,
        tier=order.tier,
        tier_name=tier["name"] if tier else order.tier,
        product_type="password",
        password=payload["password"],
        entropy_bits=payload["entropy_bits"],
        email_sent=payload["email_sent"],
        paid_at=order.paid_at,
        warning=payload.get(
            "warning",
            "Сохраните пароль сейчас — мы его не храним и не сможем восстановить.",
        ),
    )


@router.post("/watch/preview", response_model=WatchPreviewResponse)
@limiter.limit("15/hour")
async def watch_preview(request: Request, body: WatchPreviewRequest):
    try:
        breaches = fetch_email_breaches(body.email)
    except Exception as exc:
        logger.exception("Watch preview failed")
        raise HTTPException(status_code=503, detail="Breach check unavailable") from exc
    return WatchPreviewResponse(
        email=body.email.lower(),
        breach_count=len(breaches),
        breaches=[BreachSummary(**breach_to_dict(b)) for b in breaches],
    )


@router.post("/internal/watch/check")
async def watch_cron_check(request: Request, db: Session = Depends(get_db)):
    secret = settings.watch_cron_secret
    if not secret:
        raise HTTPException(status_code=503, detail="Cron not configured")
    provided = request.headers.get("X-Watch-Cron-Secret", "")
    if provided != secret:
        raise HTTPException(status_code=403, detail="Forbidden")
    stats = run_due_watch_checks(db, min_interval_days=settings.watch_check_interval_days)
    return {"status": "ok", **stats}


@router.get("/orders/{order_id}/report")
@limiter.limit("10/minute")
async def order_report(order_id: str, request: Request, db: Session = Depends(get_db)):
    try:
        oid = UUID(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid order_id") from exc

    order = order_repo.get_by_id(db, oid)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.tier != "legend":
        raise HTTPException(status_code=404, detail="Report not available for this tier")
    if order.status != "paid" or order.fulfilled_at is None:
        raise HTTPException(status_code=404, detail="Order not fulfilled")

    meta = get_report_meta(order_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Report metadata expired")

    tier = get_tier(order.tier)
    tier_name = tier["name"] if tier else order.tier
    try:
        pdf = build_svino_report_pdf(
            order_id=order_id,
            tier_name=tier_name,
            paid_at=order.paid_at,
            entropy_bits=meta["entropy_bits"],
            password_length=meta["password_length"],
            generation_mode=meta.get("generation_mode", "random"),
        )
    except FileNotFoundError as exc:
        logger.exception("PDF font missing")
        raise HTTPException(status_code=503, detail="PDF generation unavailable") from exc

    filename = f"svinopass-report-{order_id[:8]}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/webhooks/yookassa")
async def yookassa_webhook(request: Request, db: Session = Depends(get_db)):
    webhook_ip = client_ip(request)
    if not settings.yookassa_mock and settings.env != "development":
        if not SecurityHelper().is_ip_trusted(webhook_ip):
            logger.warning("Untrusted webhook IP: %s", webhook_ip)
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
