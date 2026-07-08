from datetime import datetime
from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_CANDIDATES = (
    Path(__file__).resolve().parent.parent / "data" / "DejaVuSans.ttf",
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
    Path("C:/Windows/Fonts/Arial.ttf"),
)

CHECKLIST = [
    "Смените этот пароль на других сервисах, если использовали похожий.",
    "Не используйте один пароль для нескольких аккаунтов.",
    "Храните пароль в менеджере паролей (Bitwarden, 1Password и т.п.).",
    "Включите двухфакторную аутентификацию, где это возможно.",
    "Мы не храним пароль на сервере — повторно получить его нельзя.",
]

_font_name: str | None = None


def _ensure_font() -> str:
    global _font_name
    if _font_name:
        return _font_name
    for path in FONT_CANDIDATES:
        if path.is_file():
            _font_name = "SvinopassPdfFont"
            pdfmetrics.registerFont(TTFont(_font_name, str(path)))
            return _font_name
    raise FileNotFoundError("No Cyrillic font found for PDF generation")


def build_svino_report_pdf(
    *,
    order_id: str,
    tier_name: str,
    paid_at: datetime | None,
    entropy_bits: float,
    password_length: int,
    generation_mode: str,
    password: str | None = None,
) -> bytes:
    font = _ensure_font()
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    _width, height = A4
    y = height - 25 * mm

    c.setFont(font, 20)
    c.drawString(25 * mm, y, "Svinopass — Свинорепорт")
    y -= 12 * mm

    c.setFont(font, 11)
    paid_label = paid_at.strftime("%d.%m.%Y %H:%M UTC") if paid_at else "—"
    mode_label = "passphrase (слова)" if generation_mode == "passphrase" else "случайный CSPRNG"
    lines = [
        f"Заказ: {order_id[:8]}…",
        f"Тариф: {tier_name}",
        f"Оплачен: {paid_label}",
        f"Энтропия: {entropy_bits} бит",
        f"Длина пароля: {password_length} символов",
        f"Режим: {mode_label}",
        "Политика: 32 символа, буквы, цифры, спецсимволы",
    ]
    for line in lines:
        c.drawString(25 * mm, y, line)
        y -= 7 * mm

    y -= 5 * mm
    c.setFont(font, 13)
    c.drawString(25 * mm, y, "Чеклист безопасности")
    y -= 9 * mm
    c.setFont(font, 10)

    for item in CHECKLIST:
        c.drawString(30 * mm, y, f"• {item}")
        y -= 7 * mm

    y -= 5 * mm
    c.setFont(font, 9)
    c.drawString(
        25 * mm,
        y,
        "Пароль в этот отчёт не входит. Проверьте email или одноразовый показ на сайте.",
    )

    if password:
        raise ValueError("Password must not be included in report PDF")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
