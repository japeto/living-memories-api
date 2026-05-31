from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

    PROJECT_NAME: str = "Mi Recuerdo Vivo API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Supabase — populated via .env when features are implemented
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None


settings = Settings()
