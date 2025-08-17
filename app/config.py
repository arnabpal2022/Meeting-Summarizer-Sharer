
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_STORAGE = (BASE_DIR / "storage").as_posix()

class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "development")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_STORAGE}/app.db")

    storage_dir: str = os.getenv("STORAGE_DIR", DEFAULT_STORAGE)

    llm_provider: str = os.getenv("LLM_PROVIDER", "groq")
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    # groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")

    smtp_host: Optional[str] = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    smtp_from: Optional[str] = os.getenv("SMTP_FROM")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")

settings = Settings()

# ensure storage directories
Path(settings.storage_dir).mkdir(parents=True, exist_ok=True)
(Path(settings.storage_dir) / "indexes").mkdir(parents=True, exist_ok=True)
