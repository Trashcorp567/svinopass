from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class TierInfo(BaseModel):
    id: str
    name: str
    price: int
    price_label: str
    description: str
    length: int
    features: list[str]


class CheckoutRequest(BaseModel):
    tier: str = Field(..., description="Tier id: svinomat, bacon, legend")
    email: EmailStr


class CheckoutResponse(BaseModel):
    order_id: str
    confirmation_url: str


class OrderResultResponse(BaseModel):
    order_id: str
    tier: str
    tier_name: str
    password: str
    entropy_bits: float
    email_sent: bool
    paid_at: datetime | None
    warning: str = (
        "Сохраните пароль сейчас — мы его не храним и не сможем восстановить."
    )


class OrderPendingResponse(BaseModel):
    status: str = "pending"
    order_id: str


class HealthResponse(BaseModel):
    status: str
    service: str
