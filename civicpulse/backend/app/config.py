from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/civicpulse"
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: str = "uploads"

    # Cloud Media Storage (Cloudinary)
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    # Weighted Priority Engine Initial Weights (Round 2 Spec)
    WEIGHT_SEVERITY: float = 0.40
    WEIGHT_SUPPORT: float = 0.25
    WEIGHT_WAITING_TIME: float = 0.20
    WEIGHT_REPETITION: float = 0.15

    # Duplicate Candidate Thresholds
    DUPLICATE_RADIUS_METERS: float = 150.0
    DUPLICATE_TEXT_SIMILARITY: float = 0.35

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()