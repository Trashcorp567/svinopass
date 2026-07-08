from urllib.parse import urlparse

from app.config import settings


def public_site_base_url() -> str:
    parsed = urlparse(settings.yookassa_return_url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return "https://svinopass.ru"


def build_image_qr_page_url(token: str) -> str:
    return f"{public_site_base_url()}/i/{token}"
