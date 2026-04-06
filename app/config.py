from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "Finance Tracking Backend"
    app_version: str = "1.0.0"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./finance.db")
    enable_docs: bool = os.getenv("ENABLE_DOCS", "false").lower() == "true"


settings = Settings()
