import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    APP_NAME: str = "Multimodal Agent Inspector"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
    CONFIDENCE_THRESHOLD: float = 0.85
    STRICT_VALIDATION: bool = True

settings = Settings()
