import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories import watch_repo
from app.services.email import send_watch_alert_email, send_watch_welcome_email
from app.services.breach_client import BreachInfo, breach_to_dict, fetch_email_breaches

logger = logging.getLogger(__name__)


def _breach_names(breaches: list[BreachInfo]) -> list[str]:
    return sorted({breach.name for breach in breaches if breach.name})


def _new_breaches(known: list[str], current: list[BreachInfo]) -> list[BreachInfo]:
    known_set = set(known)
    return [breach for breach in current if breach.name and breach.name not in known_set]


def activate_watch_for_order(db: Session, *, email: str, order_id: uuid.UUID) -> dict:
    breaches = fetch_email_breaches(email)
    names = _breach_names(breaches)
    subscription = watch_repo.activate_subscription(
        db,
        email=email,
        order_id=order_id,
        known_breach_names=names,
    )
    breach_payload = [breach_to_dict(b) for b in breaches]
    email_sent = send_watch_welcome_email(
        to=email,
        order_id=str(order_id),
        monitored_email=email,
        expires_at=subscription.expires_at,
        breaches=breach_payload,
    )
    if not email_sent:
        logger.error("Watch welcome email failed for order %s", order_id)

    return {
        "monitored_email": email.lower(),
        "expires_at": subscription.expires_at.isoformat(),
        "breach_count": len(breaches),
        "breaches": breach_payload,
        "email_sent": email_sent,
        "warning": (
            "Мониторинг активен. Новые утечки пришлём на email раз в неделю. "
            "Продлите подписку до окончания срока."
        ),
    }


def check_subscription(db: Session, subscription) -> bool:
    """Check one subscription. Returns True if alert email was sent."""
    if subscription.expires_at <= watch_repo.utcnow():
        subscription.status = "expired"
        db.commit()
        return False

    breaches = fetch_email_breaches(subscription.email)
    current_names = _breach_names(breaches)
    fresh = _new_breaches(subscription.known_breach_names or [], breaches)
    notified = False

    if fresh:
        breach_payload = [breach_to_dict(b) for b in fresh]
        notified = send_watch_alert_email(
            to=subscription.email,
            monitored_email=subscription.email,
            new_breaches=breach_payload,
            total_count=len(breaches),
            expires_at=subscription.expires_at,
        )
        if not notified:
            logger.error("Watch alert email failed for %s", subscription.email)

    watch_repo.mark_checked(
        db,
        subscription,
        known_breach_names=current_names,
        notified=notified,
    )
    return notified


def run_due_watch_checks(db: Session, *, min_interval_days: int = 7) -> dict:
    watch_repo.expire_stale(db)
    due = watch_repo.get_due_for_check(db, min_interval_days=min_interval_days)
    alerts = 0
    checked = 0
    errors = 0

    for subscription in due:
        try:
            if check_subscription(db, subscription):
                alerts += 1
            checked += 1
        except Exception:
            errors += 1
            logger.exception("Watch check failed for %s", subscription.email)

    return {"checked": checked, "alerts": alerts, "errors": errors, "due": len(due)}
