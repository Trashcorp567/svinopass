from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        extra="ignore",
    )

    database_url: str = "postgresql://svinopass:svinopass@localhost:5432/svinopass"
    redis_url: str = "redis://localhost:6379/0"
    env: str = "development"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://svinopass.ru",
    ]
    host: str = "0.0.0.0"
    port: int = 8000

    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""
    yookassa_return_url: str = "http://localhost:5173/payment/success"
    yookassa_mock: bool = True

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@svinopass.ru"
    smtp_tls: bool = True
    smtp_use_ssl: bool = False

    # Email provider: auto, postbox, sendpulse, haskimail, smtp
    email_provider: str = "auto"

    # Yandex Cloud Postbox — static key (HTTPS API via boto3)
    yandex_postbox_access_key_id: str = ""
    yandex_postbox_secret_access_key: str = ""
    # Yandex Cloud Postbox — API key with scope yc.postbox.send (SMTP)
    yandex_postbox_api_key_id: str = ""
    yandex_postbox_api_key_secret: str = ""

    # SendPulse (https://sendpulse.com/ru) — Russian service, HTTPS API
    sendpulse_api_key: str = ""
    sendpulse_client_id: str = ""
    sendpulse_client_secret: str = ""

    # HaskiMail (https://haskimail.ru) — Russian service, HTTPS API
    haskimail_api_key: str = ""

    hibp_api_key: str = ""
    breach_provider: str = "leakcheck"  # leakcheck | hibp | mock
    leakcheck_api_key: str = ""
    watch_cron_secret: str = ""
    watch_check_interval_days: int = 7

    # Creative nicknames — Yandex GPT (fallback to wordlists on error)
    yandex_gpt_api_key: str = ""
    yandex_gpt_folder_id: str = ""
    yandex_gpt_model: str = "yandexgpt-lite"
    creative_ai_enabled: bool = True


settings = Settings()