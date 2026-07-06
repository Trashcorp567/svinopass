import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.db.models import Order


def create_pending_order(db: Session, *, email: str, tier: str, price_rub: int) -> Order:
    order = Order(
        email=email,
        tier=tier,
        price_rub=price_rub,
        status="pending",
        idempotence_key=uuid.uuid4().hex,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_by_id(db: Session, order_id: uuid.UUID) -> Order | None:
    return db.query(Order).filter(Order.id == order_id).first()


def get_by_yookassa_payment_id(db: Session, payment_id: str) -> Order | None:
    return db.query(Order).filter(Order.yookassa_payment_id == payment_id).first()


def set_yookassa_payment_id(db: Session, order: Order, payment_id: str) -> None:
    order.yookassa_payment_id = payment_id
    db.commit()


def mark_paid(db: Session, order: Order) -> None:
    order.status = "paid"
    order.paid_at = datetime.now(timezone.utc)
    db.commit()


def mark_canceled(db: Session, order: Order) -> None:
    order.status = "canceled"
    db.commit()


def mark_fulfilled(db: Session, order: Order, *, email_sent: bool) -> None:
    order.fulfilled_at = datetime.now(timezone.utc)
    order.email_sent = email_sent
    db.commit()
