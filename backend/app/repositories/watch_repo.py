import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.db.models import WatchSubscription

WATCH_PERIOD_DAYS = 30


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def get_active_by_email(db: Session, email: str) -> WatchSubscription | None:
    now = utcnow()
    return (
        db.query(WatchSubscription)
        .filter(
            WatchSubscription.email == email.lower(),
            WatchSubscription.status == "active",
            WatchSubscription.expires_at > now,
        )
        .order_by(WatchSubscription.expires_at.desc())
        .first()
    )


def get_due_for_check(db: Session, *, min_interval_days: int = 7) -> list[WatchSubscription]:
    now = utcnow()
    cutoff = now - timedelta(days=min_interval_days)
    return (
        db.query(WatchSubscription)
        .filter(
            WatchSubscription.status == "active",
            WatchSubscription.expires_at > now,
            (WatchSubscription.last_checked_at.is_(None))
            | (WatchSubscription.last_checked_at <= cutoff),
        )
        .order_by(WatchSubscription.last_checked_at.asc().nullsfirst())
        .all()
    )


def activate_subscription(
    db: Session,
    *,
    email: str,
    order_id: uuid.UUID,
    known_breach_names: list[str],
) -> WatchSubscription:
    normalized = email.lower().strip()
    now = utcnow()
    existing = get_active_by_email(db, normalized)
    base = existing.expires_at if existing and existing.expires_at > now else now
    expires_at = base + timedelta(days=WATCH_PERIOD_DAYS)

    if existing:
        existing.expires_at = expires_at
        existing.known_breach_names = known_breach_names
        existing.last_order_id = order_id
        existing.last_checked_at = now
        existing.updated_at = now
        db.commit()
        db.refresh(existing)
        return existing

    sub = WatchSubscription(
        email=normalized,
        status="active",
        known_breach_names=known_breach_names,
        expires_at=expires_at,
        last_checked_at=now,
        last_order_id=order_id,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def mark_checked(
    db: Session,
    subscription: WatchSubscription,
    *,
    known_breach_names: list[str],
    notified: bool,
) -> None:
    now = utcnow()
    subscription.known_breach_names = known_breach_names
    subscription.last_checked_at = now
    if notified:
        subscription.last_notified_at = now
    subscription.updated_at = now
    db.commit()


def expire_stale(db: Session) -> int:
    now = utcnow()
    updated = (
        db.query(WatchSubscription)
        .filter(
            WatchSubscription.status == "active",
            WatchSubscription.expires_at <= now,
        )
        .update({"status": "expired", "updated_at": now}, synchronize_session=False)
    )
    db.commit()
    return updated
