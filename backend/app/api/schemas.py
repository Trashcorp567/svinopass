from datetime import datetime

from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class TierInfo(BaseModel):
    id: str
    name: str
    price: int
    price_label: str
    description: str
    length: int
    features: list[str]
    product_type: str = "password"


class CheckoutRequest(BaseModel):
    tier: str = Field(..., description="Tier id")
    email: EmailStr
    mode: Literal["random", "passphrase"] = "random"


class CheckoutResponse(BaseModel):
    order_id: str
    confirmation_url: str


class BreachSummary(BaseModel):
    name: str
    title: str
    domain: str
    breach_date: str
    pwn_count: int | None = None


class OrderResultResponse(BaseModel):
    order_id: str
    tier: str
    tier_name: str
    product_type: Literal["password", "backup_codes", "watch"] = "password"
    password: str | None = None
    backup_codes: list[str] | None = None
    entropy_bits: float | None = None
    monitored_email: str | None = None
    expires_at: datetime | None = None
    breach_count: int | None = None
    breaches: list[BreachSummary] | None = None
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


class WatchPreviewRequest(BaseModel):
    email: EmailStr


class WatchPreviewResponse(BaseModel):
    email: str
    breach_count: int
    breaches: list[BreachSummary]
