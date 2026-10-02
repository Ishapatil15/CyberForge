from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    app_name: str = "CyberForge"
    secret_key: str = "dev-secret-change-me"
    flag_pepper: str = "dev-flag-pepper-change-me"
    access_token_expire_minutes: int = 720
    cookie_name: str = "cyberforge_session"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    cors_origins: str = "http://localhost:5173"
    database_url: str = "postgresql+psycopg://ctf:ctf@localhost:5432/ctf"
    admin_username: str = "admin"
    admin_email: str = "admin@local.ctf"
    admin_password: str = "ChangeMeAdmin!23"
    upload_dir: str = "./uploads"
    max_upload_mb: int = 10
    login_rate_limit: str = "8/minute"
    submit_rate_limit: str = "20/minute"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
