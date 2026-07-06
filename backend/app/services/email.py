import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger(__name__)


def send_password_email(*, to: str, password: str, tier_name: str, order_id: str) -> bool:
    subject = f"Svinopass — ваш пароль ({tier_name})"
    body = (
        f"Здравствуйте!\n\n"
        f"Ваш пароль по заказу {order_id} (тариф «{tier_name}»):\n\n"
        f"{password}\n\n"
        f"Мы не храним пароли на сервере. Сохраните это письмо в надёжном месте "
        f"или перенесите пароль в менеджер паролей.\n\n"
        f"— Svinopass (svinopass.ru)\n"
    )

    if not settings.smtp_host:
        if settings.env == "production":
            logger.error("SMTP not configured in production for order %s", order_id)
            return False
        logger.info(
            "DEV email (SMTP not configured): to=%s order=%s tier=%s password_len=%d",
            to,
            order_id,
            tier_name,
            len(password),
        )
        return True

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
    except smtplib.SMTPException:
        logger.exception("SMTP delivery failed for order %s to %s", order_id, to)
        return False

    return True