from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    anthropic_api_key: str
    database_url: str = "sqlite:///./oms_support.db"
    chroma_persist_dir: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    ai_confidence_threshold: float = 0.70
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # SLA hours per tier per priority
    sla_config: dict = {
        "L1": {"critical": 1, "high": 4, "medium": 12, "low": 24},
        "L2": {"critical": 4, "high": 12, "medium": 24, "low": 72},
        "L3": {"critical": 8, "high": 24, "medium": 72, "low": 168},
    }

    @property
    def allowed_origins(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
