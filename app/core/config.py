from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # App
    APP_NAME: str = "AI BaaS"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ai_baas"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # File Storage
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = "./storage"
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_MIME_TYPES: list = [
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf", "text/plain", "text/csv",
        "application/json", "application/xml",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]
    S3_BUCKET: str = ""
    S3_ENDPOINT: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""

    # LiteLLM
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = ""
    ANTHROPIC_API_KEY: str = ""
    DEFAULT_MODEL: str = ""

    # Tavily
    TAVILY_API_KEY: str = ""

    # Vector Database
    VECTOR_DB_PATH: str = "./vector_db"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"


settings = Settings()
