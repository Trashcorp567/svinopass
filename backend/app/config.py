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


settings = Settings()