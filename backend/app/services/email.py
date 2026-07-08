import logging
import smtplib
import time
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
import httpx
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.config import settings
from app.services.watch_action_plan import format_action_plan_text

logger = logging.getLogger(__name__)

_sendpulse_token: tuple[str, float] | None = None


def _build_email_content(*, tier_name: str, order_id: str, password: str) -> tuple[str, str]:
    subject = f"Svinopass — ваш пароль ({tier_name})"
    body = (
        f"Здравствуйте!\n\n"
        f"Ваш пароль по заказу {order_id} (тариф «{tier_name}»):\n\n"
        f"{password}\n\n"
        f"Мы не храним пароли на сервере. Сохраните это письмо в надёжном месте "
        f"или перенесите пароль в менеджер паролей.\n\n"
        f"— Svinopass (svinopass.ru)\n"
    )
    return subject, body


def _build_backup_codes_email_content(
    *, tier_name: str, order_id: str, codes: list[str]
) -> tuple[str, str]:
    subject = f"Svinopass — коды восстановления ({tier_name})"
    numbered = "\n".join(f"{i + 1}. {code}" for i, code in enumerate(codes))
    body = (
        f"Здравствуйте!\n\n"
        f"Ваши одноразовые коды восстановления по заказу {order_id} "
        f"(тариф «{tier_name}»):\n\n"
        f"{numbered}\n\n"
        f"Храните коды офлайн в надёжном месте. Каждый код предназначен для однократного "
        f"использования. Мы не храним коды на сервере.\n\n"
        f"— Svinopass (svinopass.ru)\n"
    )
    return subject, body


def _build_creative_email_content(
    *,
    tier_name: str,
    order_id: str,
    items: list[str],
    bios: list[str],
    kind: str,
    category: str,
) -> tuple[str, str]:
    kind_labels = {
        "nicknames": "ники",
        "names": "имена",
        "social": "соцпак",
    }
    kind_label = kind_labels.get(kind, "варианты")
    subject = f"Svinopass — ваши {kind_label} ({tier_name})"
    numbered = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))
    body = (
        f"Здравствуйте!\n\n"
        f"Ваш заказ {order_id} (тариф «{tier_name}», стиль «{category}»):\n\n"
        f"{numbered}\n"
    )
    if bios:
        bio_block = "\n".join(f"• {bio}" for bio in bios)
        body += f"\nБио для профиля:\n{bio_block}\n"
    body += (
        "\nМы не храним сгенерированный контент на сервере. "
        "Занятость ников в соцсетях и играх не проверяется.\n\n"
        f"— Svinopass (svinopass.ru)\n"
    )
    return subject, body


def _get_sendpulse_token() -> str | None:
    if settings.sendpulse_api_key:
        return settings.sendpulse_api_key
    if not settings.sendpulse_client_id or not settings.sendpulse_client_secret:
        return None

    global _sendpulse_token
    now = time.time()
    if _sendpulse_token and _sendpulse_token[1] > now:
        return _sendpulse_token[0]

    try:
        response = httpx.post(
            "https://api.sendpulse.com/oauth/access_token",
            json={
                "grant_type": "client_credentials",
                "client_id": settings.sendpulse_client_id,
                "client_secret": settings.sendpulse_client_secret,
            },
            timeout=15.0,
        )
        response.raise_for_status()
        data = response.json()
        token = data["access_token"]
        expires_in = int(data.get("expires_in", 3600))
        _sendpulse_token = (token, now + max(expires_in - 60, 60))
        return token
    except httpx.HTTPError:
        logger.exception("SendPulse OAuth failed")
        return None


def _send_via_postbox_api_key_smtp(*, to: str, subject: str, body: str) -> bool:
    if not settings.yandex_postbox_api_key_id or not settings.yandex_postbox_api_key_secret:
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from
    message["To"] = to
    message.set_content(body)

    for use_ssl, port in ((False, 587), (True, 465)):
        try:
            if use_ssl:
                smtp = smtplib.SMTP_SSL("postbox.cloud.yandex.net", port, timeout=15)
            else:
                smtp = smtplib.SMTP("postbox.cloud.yandex.net", port, timeout=15)
            with smtp:
                if not use_ssl:
                    smtp.starttls()
                smtp.login(settings.yandex_postbox_api_key_id, settings.yandex_postbox_api_key_secret)
                smtp.send_message(message)
            return True
        except (smtplib.SMTPException, OSError):
            logger.exception("Postbox SMTP (%s:%s) failed to %s", "ssl" if use_ssl else "tls", port, to)
    return False


def _send_via_postbox_boto3(*, to: str, subject: str, body: str) -> bool:
    if not settings.yandex_postbox_access_key_id or not settings.yandex_postbox_secret_access_key:
        return False

    try:
        client = boto3.client(
            "sesv2",
            endpoint_url="https://postbox.cloud.yandex.net",
            region_name="ru-central1",
            aws_access_key_id=settings.yandex_postbox_access_key_id,
            aws_secret_access_key=settings.yandex_postbox_secret_access_key,
            config=Config(retries={"max_attempts": 2}),
        )
        message = MIMEMultipart()
        message["Subject"] = subject
        message["From"] = settings.smtp_from
        message["To"] = to
        message.attach(MIMEText(body, "plain", "utf-8"))
        client.send_email(
            FromEmailAddress=settings.smtp_from,
            Destination={"ToAddresses": [to]},
            Content={"Raw": {"Data": message.as_bytes()}},
        )
        return True
    except (BotoCoreError, ClientError):
        logger.exception("Yandex Postbox API delivery failed to %s", to)
        return False


def _send_via_postbox(*, to: str, subject: str, body: str) -> bool:
    if settings.yandex_postbox_access_key_id and settings.yandex_postbox_secret_access_key:
        if _send_via_postbox_boto3(to=to, subject=subject, body=body):
            return True
        return False
    return _send_via_postbox_api_key_smtp(to=to, subject=subject, body=body)


def _postbox_configured() -> bool:
    return bool(
        (settings.yandex_postbox_api_key_id and settings.yandex_postbox_api_key_secret)
        or (settings.yandex_postbox_access_key_id and settings.yandex_postbox_secret_access_key)
    )


def _send_via_sendpulse(*, to: str, subject: str, body: str) -> bool:
    token = _get_sendpulse_token()
    if not token:
        return False

    try:
        response = httpx.post(
            "https://api.sendpulse.com/smtp/emails",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json={
                "email": {
                    "subject": subject,
                    "text": body,
                    "from": {"name": "Svinopass", "email": settings.smtp_from},
                    "to": [{"email": to}],
                }
            },
            timeout=15.0,
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        logger.exception("SendPulse API delivery failed to %s", to)
        return False


def _send_via_haskimail(*, to: str, subject: str, body: str) -> bool:
    if not settings.haskimail_api_key:
        return False

    try:
        response = httpx.post(
            "https://api.haskimail.ru/email",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Haskimail-Server-Token": settings.haskimail_api_key,
            },
            json={
                "From": settings.smtp_from,
                "To": to,
                "Subject": subject,
                "TextBody": body,
            },
            timeout=15.0,
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        logger.exception("HaskiMail API delivery failed to %s", to)
        return False


def _send_via_smtp(*, to: str, subject: str, body: str) -> bool:
    if not settings.smtp_host:
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from
    message["To"] = to
    message.set_content(body)

    try:
        if settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
                if settings.smtp_user:
                    smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
                if settings.smtp_tls:
                    smtp.starttls()
                if settings.smtp_user:
                    smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(message)
    except (smtplib.SMTPException, OSError):
        logger.exception("SMTP delivery failed to %s", to)
        return False

    return True


def _http_email_configured() -> bool:
    return bool(
        _postbox_configured()
        or settings.sendpulse_api_key
        or (settings.sendpulse_client_id and settings.sendpulse_client_secret)
        or settings.haskimail_api_key
    )


def _deliver_email(*, to: str, subject: str, body: str, order_id: str, dev_log: str) -> bool:
    if not settings.smtp_host and not _http_email_configured():
        if settings.env == "production":
            logger.error("Email not configured in production for order %s", order_id)
            return False
        logger.info("DEV email (not configured): %s", dev_log)
        return True

    if settings.email_provider in ("auto", "postbox"):
        if _send_via_postbox(to=to, subject=subject, body=body):
            return True

    if settings.email_provider in ("auto", "sendpulse"):
        if _send_via_sendpulse(to=to, subject=subject, body=body):
            return True

    if settings.email_provider in ("auto", "haskimail"):
        if _send_via_haskimail(to=to, subject=subject, body=body):
            return True

    if settings.email_provider == "smtp" and _send_via_smtp(to=to, subject=subject, body=body):
        return True

    if settings.email_provider == "auto" and settings.smtp_host:
        if _send_via_smtp(to=to, subject=subject, body=body):
            return True

    return False


def send_password_email(*, to: str, password: str, tier_name: str, order_id: str) -> bool:
    subject, body = _build_email_content(tier_name=tier_name, order_id=order_id, password=password)
    return _deliver_email(
        to=to,
        subject=subject,
        body=body,
        order_id=order_id,
        dev_log=f"to={to} order={order_id} tier={tier_name} password_len={len(password)}",
    )


def send_backup_codes_email(
    *, to: str, codes: list[str], tier_name: str, order_id: str
) -> bool:
    subject, body = _build_backup_codes_email_content(
        tier_name=tier_name, order_id=order_id, codes=codes
    )
    return _deliver_email(
        to=to,
        subject=subject,
        body=body,
        order_id=order_id,
        dev_log=f"to={to} order={order_id} tier={tier_name} codes={len(codes)}",
    )


def send_creative_email(
    *,
    to: str,
    items: list[str],
    bios: list[str],
    tier_name: str,
    order_id: str,
    kind: str,
    category: str,
) -> bool:
    subject, body = _build_creative_email_content(
        tier_name=tier_name,
        order_id=order_id,
        items=items,
        bios=bios,
        kind=kind,
        category=category,
    )
    return _deliver_email(
        to=to,
        subject=subject,
        body=body,
        order_id=order_id,
        dev_log=f"to={to} order={order_id} tier={tier_name} creative_items={len(items)}",
    )


def _format_breach_lines(breaches: list[dict]) -> str:
    lines: list[str] = []
    for breach in breaches:
        title = breach.get("title") or breach.get("name") or "Утечка"
        date = breach.get("breach_date") or "?"
        domain = breach.get("domain") or "—"
        lines.append(f"- {title} ({domain}, {date})")
    return "\n".join(lines) if lines else "- Утечек не найдено"


def _format_expires(expires_at) -> str:
    if hasattr(expires_at, "strftime"):
        return expires_at.strftime("%d.%m.%Y")
    return str(expires_at)[:10]


def send_watch_welcome_email(
    *,
    to: str,
    order_id: str,
    monitored_email: str,
    expires_at,
    breaches: list[dict],
) -> bool:
    subject = "Svinopass: Свиной сторож включён"
    breach_lines = _format_breach_lines(breaches)
    action_plan = format_action_plan_text(
        breach_count=len(breaches),
        include_watch_cta=False,
    )
    body = (
        f"Мониторинг email {monitored_email} активен до {_format_expires(expires_at)}.\n\n"
        f"Сейчас в публичных утечках: {len(breaches)}\n"
        f"{breach_lines}\n\n"
        f"{action_plan}\n\n"
        "Раз в неделю мы проверяем новые утечки и пришлём письмо, если появится что-то новое.\n"
        "Продлите подписку на svinopass.ru/watch до окончания срока.\n\n"
        f"Заказ: {order_id}\n"
        "— Svinopass"
    )
    return _deliver_email(
        to=to,
        subject=subject,
        body=body,
        order_id=order_id,
        dev_log=f"to={to} order={order_id} watch welcome breaches={len(breaches)}",
    )


def send_watch_alert_email(
    *,
    to: str,
    monitored_email: str,
    new_breaches: list[dict],
    total_count: int,
    expires_at,
) -> bool:
    subject = f"Svinopass: новые утечки для {monitored_email}"
    breach_lines = _format_breach_lines(new_breaches)
    action_plan = format_action_plan_text(breach_count=total_count, include_watch_cta=False)
    body = (
        f"Свиной сторож нашёл {len(new_breaches)} новых утечек для {monitored_email}.\n\n"
        f"{breach_lines}\n\n"
        f"Всего в базе утечек: {total_count}.\n"
        f"Мониторинг активен до {_format_expires(expires_at)}.\n\n"
        f"{action_plan}\n\n"
        "— Svinopass"
    )
    return _deliver_email(
        to=to,
        subject=subject,
        body=body,
        order_id=f"watch-{monitored_email}",
        dev_log=f"to={to} watch alert new={len(new_breaches)} total={total_count}",
    )
