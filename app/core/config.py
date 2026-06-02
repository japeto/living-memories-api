from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

    PROJECT_NAME: str = "Mi Recuerdo Vivo API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Supabase connection — populated via .env.
    # SUPABASE_KEY is the anon key: request-scoped access that respects RLS.
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None
    # Service-role key: server-side privileged operations only. Never exposed in a
    # response model and never logged.
    SUPABASE_SERVICE_ROLE_KEY: str | None = None
    # Storage bucket holding the voice-message audio files.
    SUPABASE_STORAGE_BUCKET: str = "memories-audio"
    # Shared timeout (seconds) for the PostgREST and Storage sub-clients.
    SUPABASE_TIMEOUT: int = 10

    # JWT Settings
    SECRET_KEY: str = "changeme"  # Should be overridden in .env
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3 * 60  # 3 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days


settings = Settings()
