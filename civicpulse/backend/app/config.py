from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/civicpulse"
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    UPLOAD_DIR: str = "uploads"

    # Weighted Priority Engine Initial Weights (Round 2 Spec)
    WEIGHT_SEVERITY: float = 0.40
    WEIGHT_SUPPORT: float = 0.25
    WEIGHT_WAITING_TIME: float = 0.20
    WEIGHT_REPETITION: float = 0.15

    # Duplicate Candidate Thresholds
    DUPLICATE_RADIUS_METERS: float = 150.0
    DUPLICATE_TEXT_SIMILARITY: float = 0.35

    class Config:
        env_file = ".env"


settings = Settings()