from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

import httpx

from app.config import settings

USER_AGENT = "Svinopass-Watch/1.0"
HIBP_BASE = "https://haveibeenpwned.com/api/v3"
LEAKCHECK_PUBLIC = "https://leakcheck.io/api/public"
LEAKCHECK_PRO = "https://leakcheck.io/api/v2/query"


@dataclass(frozen=True)
class BreachInfo:
    name: str
    title: str
    domain: str
    breach_date: str
    pwn_count: int | None


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip()).strip("-").lower()
    return slug or "breach"


def _mock_breaches(email: str) -> list[BreachInfo]:
    lowered = email.lower()
    if "clean" in lowered:
        return []
    if "leak" in lowered or "pwned" in lowered:
        return [
            BreachInfo(
                name="mock-breach-2024",
                title="Mock Social Leak",
                domain="example.com",
                breach_date="2024-06-01",
                pwn_count=1200000,
            ),
            BreachInfo(
                name="mock-shop-2019",
                title="Mock Shop Breach",
                domain="shop.example",
                breach_date="2019-03-15",
                pwn_count=45000,
            ),
        ]
    return [
        BreachInfo(
            name="mock-generic",
            title="Mock Generic Breach",
            domain="web.example",
            breach_date="2020-01-01",
            pwn_count=10000,
        )
    ]


def _parse_hibp_breach(item: dict) -> BreachInfo:
    return BreachInfo(
        name=item.get("Name", ""),
        title=item.get("Title", item.get("Name", "")),
        domain=item.get("Domain", ""),
        breach_date=item.get("BreachDate", ""),
        pwn_count=item.get("PwnCount"),
    )


def _fetch_hibp(email: str) -> list[BreachInfo]:
    if not settings.hibp_api_key:
        raise RuntimeError("HIBP provider selected but HIBP_API_KEY is not set")

    url = f"{HIBP_BASE}/breachedaccount/{email}"
    headers = {
        "hibp-api-key": settings.hibp_api_key,
        "User-Agent": USER_AGENT,
    }
    params = {"truncateResponse": "false"}

    with httpx.Client(timeout=20.0) as client:
        response = client.get(url, headers=headers, params=params)

    if response.status_code == 404:
        return []
    if response.status_code == 429:
        raise RuntimeError("HIBP rate limit exceeded")
    response.raise_for_status()

    data = response.json()
    if not isinstance(data, list):
        return []
    return [_parse_hibp_breach(item) for item in data if item.get("Name")]


def _normalize_leakcheck_date(raw: str) -> str:
    value = (raw or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}", value):
        return f"{value}-01"
    return value


def _parse_leakcheck_sources(sources: list[dict]) -> list[BreachInfo]:
    seen: set[str] = set()
    breaches: list[BreachInfo] = []
    for source in sources:
        title = (source.get("name") or "").strip()
        if not title:
            continue
        name = _slugify(title)
        if name in seen:
            continue
        seen.add(name)
        breaches.append(
            BreachInfo(
                name=name,
                title=title,
                domain="",
                breach_date=_normalize_leakcheck_date(source.get("date", "")),
                pwn_count=None,
            )
        )
    return breaches


def _fetch_leakcheck_public(email: str) -> list[BreachInfo]:
    with httpx.Client(timeout=20.0) as client:
        response = client.get(
            LEAKCHECK_PUBLIC,
            params={"check": email},
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )
    if response.status_code == 429:
        raise RuntimeError("LeakCheck rate limit exceeded")
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        return []
    sources = data.get("sources") or []
    if not isinstance(sources, list):
        return []
    return _parse_leakcheck_sources(sources)


def _fetch_leakcheck_pro(email: str) -> list[BreachInfo]:
    if not settings.leakcheck_api_key:
        return _fetch_leakcheck_public(email)

    with httpx.Client(timeout=20.0) as client:
        response = client.get(
            f"{LEAKCHECK_PRO}/{email}",
            params={"type": "email"},
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/json",
                "X-API-Key": settings.leakcheck_api_key,
            },
        )
    if response.status_code == 429:
        raise RuntimeError("LeakCheck rate limit exceeded")
    response.raise_for_status()
    data = response.json()
    if not data.get("success") or not data.get("found"):
        return []

    seen: set[str] = set()
    breaches: list[BreachInfo] = []
    for item in data.get("result") or []:
        source = item.get("source") or {}
        title = (source.get("name") or "").strip()
        if not title:
            continue
        name = _slugify(title)
        if name in seen:
            continue
        seen.add(name)
        breaches.append(
            BreachInfo(
                name=name,
                title=title,
                domain="",
                breach_date=_normalize_leakcheck_date(source.get("breach_date", "")),
                pwn_count=None,
            )
        )
    return breaches


def _fetch_leakcheck(email: str) -> list[BreachInfo]:
    if settings.leakcheck_api_key:
        return _fetch_leakcheck_pro(email)
    return _fetch_leakcheck_public(email)


def fetch_email_breaches(email: str) -> list[BreachInfo]:
    provider = settings.breach_provider.lower().strip()
    if provider == "mock":
        return _mock_breaches(email)
    if provider == "hibp":
        return _fetch_hibp(email)
    if provider == "leakcheck":
        return _fetch_leakcheck(email)
    raise RuntimeError(f"Unknown breach provider: {provider}")


def breach_to_dict(breach: BreachInfo) -> dict:
    return {
        "name": breach.name,
        "title": breach.title,
        "domain": breach.domain,
        "breach_date": breach.breach_date,
        "pwn_count": breach.pwn_count,
    }
