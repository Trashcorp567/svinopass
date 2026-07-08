"""Текст плана действий после обнаружения утечек email."""

SITE_URL = "https://svinopass.ru"


def format_action_plan_text(*, breach_count: int, include_watch_cta: bool = True) -> str:
    lines = ["Что делать:", ""]

    if breach_count > 0:
        lines.extend(
            [
                "1. Смените пароль на каждом сервисе из списка. Если пароль был одинаковым — смените его везде.",
                "2. Включите двухфакторную аутентификацию (2FA) на почте, банках и важных аккаунтах.",
                f"3. Проверьте пароли на утечки: {SITE_URL}/check",
                f"4. Закажите уникальные пароли с доставкой на email: {SITE_URL}/#pricing",
            ]
        )
        if include_watch_cta:
            lines.append(f"5. Следите за новыми утечками: {SITE_URL}/watch")
    else:
        lines.extend(
            [
                "1. Пока утечек не найдено, но новые базы появляются регулярно.",
                f"2. Проверяйте пароли: {SITE_URL}/check",
            ]
        )
        if include_watch_cta:
            lines.append(f"3. Подключите мониторинг: {SITE_URL}/watch")

    lines.extend(
        [
            "",
            "Важно: удалить данные из уже утёкших баз невозможно — копии разошлись по сети. "
            "Смените пароли и включите 2FA, чтобы злоумышленники не смогли ими воспользоваться.",
        ]
    )
    return "\n".join(lines)
