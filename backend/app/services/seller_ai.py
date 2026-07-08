import base64
import json
import logging
import re

import httpx

from app.config import settings
from app.services.creative_ai import YANDEX_CHAT_URL
from app.services.seller_platforms import SellerPlatform

logger = logging.getLogger(__name__)

YANDEX_OCR_URL = "https://ocr.api.cloud.yandex.net/ocr/v1/recognizeText"

_JSON_BLOCK_RE = re.compile(r"\{[\s\S]*\}")

_PLATFORM_RULES: dict[str, str] = {
    "ozon": (
        "Ozon: rich SEO description, structured bullets, factual tone. "
        "Title max {title_max} chars, description max {description_max} chars."
    ),
    "wb": (
        "Wildberries: concise punchy title, benefit-first description. "
        "Title max {title_max} chars (strict), description max {description_max} chars."
    ),
    "avito": (
        "Avito: friendly classifieds style, local buyer language. "
        "Title max {title_max} chars, description max {description_max} chars."
    ),
}


def _trim(text: str, limit: int) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _yandex_headers() -> dict[str, str]:
    if not settings.yandex_gpt_api_key or not settings.yandex_gpt_folder_id:
        raise RuntimeError("Yandex GPT is not configured")
    return {
        "Authorization": f"Api-Key {settings.yandex_gpt_api_key}",
        "x-folder-id": settings.yandex_gpt_folder_id,
        "Content-Type": "application/json",
    }


def _seller_text_model() -> str:
    model = (settings.yandex_gpt_seller_model or "yandexgpt-lite").strip()
    return model or "yandexgpt-lite"


def _model_uri(model: str) -> str:
    folder_id = settings.yandex_gpt_folder_id
    return f"gpt://{folder_id}/{model}/latest"


def _call_yandex_gpt(
    messages: list[dict],
    *,
    model: str | None = None,
    temperature: float = 0.5,
    max_tokens: int = 3500,
) -> str:
    model_name = model or _seller_text_model()
    body = {
        "model": _model_uri(model_name),
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    with httpx.Client(timeout=120.0) as client:
        response = client.post(YANDEX_CHAT_URL, headers=_yandex_headers(), json=body)
        if response.status_code >= 400:
            logger.warning(
                "Yandex GPT seller request failed: model=%s status=%s body=%s",
                model_name,
                response.status_code,
                response.text[:500],
            )
        response.raise_for_status()
        data = response.json()

    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError("Yandex GPT returned empty response")
    return choices[0]["message"]["content"]


def extract_image_ocr_text(*, image_b64: str, mime: str) -> str:
    """Extract visible text from a product photo via Yandex OCR."""
    headers = {
        "Authorization": f"Api-Key {settings.yandex_gpt_api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "mimeType": mime,
        "languageCodes": ["ru", "en"],
        "model": "page",
        "content": image_b64,
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.post(YANDEX_OCR_URL, headers=headers, json=body)
        if response.status_code >= 400:
            logger.warning(
                "Yandex OCR failed: status=%s body=%s",
                response.status_code,
                response.text[:300],
            )
            return ""
        data = response.json()

    annotation = data.get("result", {}).get("textAnnotation", {})
    text = str(annotation.get("fullText", "")).strip()
    if len(text) > 1500:
        text = text[:1500].rstrip() + "…"
    return text


def _describe_image_with_vision(*, image_b64: str, mime: str) -> str:
    """Optional multimodal description when a vision-capable model is configured."""
    vision_model = (settings.yandex_gpt_vision_model or "").strip()
    if not vision_model or vision_model == settings.yandex_gpt_model:
        return ""

    data_url = f"data:{mime};base64,{image_b64}"
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Опиши товар на фото для продавца маркетплейса: "
                        "что это, цвет, материал, комплектация, видимые детали. "
                        "2–4 предложения по-русски, без выдуманных характеристик."
                    ),
                },
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    ]
    try:
        return _call_yandex_gpt(
            messages,
            model=vision_model,
            temperature=0.2,
            max_tokens=400,
        ).strip()
    except Exception as exc:
        logger.warning("Yandex vision model %s failed: %s", vision_model, exc)
        return ""


def _build_image_context(*, image_b64: str, mime: str) -> tuple[str, str]:
    vision_text = _describe_image_with_vision(image_b64=image_b64, mime=mime)
    ocr_text = extract_image_ocr_text(image_b64=image_b64, mime=mime)

    parts: list[str] = []
    if vision_text:
        parts.append(f"Описание по фото (AI): {vision_text}")
    if ocr_text:
        parts.append(f"Текст на упаковке/этикетке (OCR): {ocr_text}")

    summary = " ".join(parts).strip()
    if summary:
        return summary, "photo"
    return "", "hints"


def _parse_cards_payload(raw: str, platforms: list[SellerPlatform]) -> tuple[str, list[dict]]:
    match = _JSON_BLOCK_RE.search(raw)
    if not match:
        raise ValueError("AI response is not JSON")
    payload = json.loads(match.group())
    vision_summary = str(payload.get("vision_summary", "")).strip()
    cards_in = payload.get("cards", [])
    if not isinstance(cards_in, list):
        raise ValueError("Invalid cards array")

    by_id = {p.id: p for p in platforms}
    cards: list[dict] = []
    for item in cards_in:
        if not isinstance(item, dict):
            continue
        platform_id = str(item.get("platform", "")).strip()
        platform = by_id.get(platform_id)
        if not platform:
            continue
        titles_raw = item.get("titles", [])
        if not isinstance(titles_raw, list):
            titles_raw = []
        titles: list[str] = []
        seen: set[str] = set()
        for title in titles_raw:
            cleaned = _trim(str(title), platform.title_max)
            if not cleaned:
                continue
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            titles.append(cleaned)
            if len(titles) >= platform.title_count:
                break
        if len(titles) < platform.title_count:
            raise ValueError(f"Not enough titles for {platform_id}")

        description = _trim(str(item.get("description", "")), platform.description_max)
        if len(description) < 80:
            raise ValueError(f"Description too short for {platform_id}")

        bullets_raw = item.get("bullets", [])
        bullets: list[str] = []
        if isinstance(bullets_raw, list):
            for bullet in bullets_raw[:8]:
                line = _trim(str(bullet), 200)
                if line:
                    bullets.append(line)

        cards.append(
            {
                "platform": platform.id,
                "platform_label": platform.label,
                "titles": titles,
                "description": description,
                "bullets": bullets,
            }
        )

    if len(cards) != len(platforms):
        raise ValueError("AI returned incomplete platform cards")
    return vision_summary, cards


def generate_seller_cards_ai(
    *,
    platforms: list[SellerPlatform],
    image_b64: str,
    mime: str,
    product_name: str,
    product_category: str,
    product_hints: str,
) -> tuple[str, list[dict]]:
    image_context, context_source = _build_image_context(image_b64=image_b64, mime=mime)

    platform_blocks = []
    for platform in platforms:
        rules = _PLATFORM_RULES[platform.id].format(
            title_max=platform.title_max,
            description_max=platform.description_max,
        )
        platform_blocks.append(
            f'- "{platform.id}" ({platform.label}): exactly {platform.title_count} titles, '
            f"one description, 3-6 bullet points. {rules}"
        )

    context_block = image_context or (
        "Фото не удалось разобрать автоматически — опирайся на подсказки продавца ниже."
    )

    user_text = (
        "Write marketplace listing copy in Russian for a seller.\n\n"
        f"Image analysis:\n{context_block}\n\n"
        f"Product name (optional): {product_name or '—'}\n"
        f"Category (optional): {product_category or '—'}\n"
        f"Seller hints (optional): {product_hints or '—'}\n\n"
        "Platforms to generate:\n"
        + "\n".join(platform_blocks)
        + "\n\n"
        "Use only facts from image analysis and seller hints. "
        "Do not invent certifications, medical claims, or exact dimensions.\n\n"
        "Reply ONLY with JSON:\n"
        "{\n"
        '  "vision_summary": "1-2 sentences in Russian: what the product is",\n'
        '  "cards": [\n'
        "    {\n"
        '      "platform": "ozon",\n'
        '      "titles": ["...", "...", "...", "...", "..."],\n'
        '      "description": "...",\n'
        '      "bullets": ["...", "..."]\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "No markdown."
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a Russian marketplace copywriter. "
                "Output valid JSON only."
            ),
        },
        {"role": "user", "content": user_text},
    ]

    raw = _call_yandex_gpt(messages, temperature=0.45)
    vision_summary, cards = _parse_cards_payload(raw, platforms)
    if not vision_summary and image_context:
        vision_summary = _trim(image_context, 400)
    elif not vision_summary and context_source == "hints":
        vision_summary = (
            "Текст собран по подсказкам продавца — проверьте факты перед публикацией."
        )
    return vision_summary, cards


def generate_seller_cards_fallback(
    *,
    platforms: list[SellerPlatform],
    product_name: str,
    product_category: str,
    product_hints: str,
) -> tuple[str, list[dict]]:
    base_name = product_name or product_category or "Товар"
    vision_summary = (
        "Не удалось сгенерировать текст через AI — черновик по вашим подсказкам. "
        "Проверьте факты и допишите характеристики перед публикацией."
    )
    hint = product_hints or "Качественный товар для повседневного использования."
    hint_short = _trim(hint, 60)
    category = product_category or "уточните у продавца"

    title_seeds = [
        base_name,
        f"{base_name} — {category}" if product_category else f"{base_name} — {hint_short}",
        f"{base_name}: {hint_short}",
        f"Купить {base_name}",
        f"{base_name} | {product_category or 'для дома'}",
    ]

    cards: list[dict] = []
    for platform in platforms:
        titles: list[str] = []
        seen: set[str] = set()
        for seed in title_seeds:
            cleaned = _trim(seed, platform.title_max)
            key = cleaned.lower()
            if key in seen:
                continue
            seen.add(key)
            titles.append(cleaned)
            if len(titles) >= platform.title_count:
                break
        while len(titles) < platform.title_count:
            extra = _trim(f"{base_name} ({len(titles) + 1})", platform.title_max)
            titles.append(extra)

        description = _trim(
            f"{base_name}. {hint} "
            f"Категория: {category}. "
            "Проверьте характеристики перед публикацией на маркетплейсе.",
            platform.description_max,
        )
        bullets = [
            _trim(f"Название: {base_name}", 200),
            _trim(f"Категория: {category}", 200),
            _trim(hint, 200),
        ]
        cards.append(
            {
                "platform": platform.id,
                "platform_label": platform.label,
                "titles": titles,
                "description": description,
                "bullets": bullets,
            }
        )
    return vision_summary, cards
