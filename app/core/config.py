from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "WarrantyGuard AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database (Supabase PostgreSQL)
    DATABASE_URL: str
    
    # Supabase config
    SUPABASE_URL: str
    SUPABASE_KEY: str
    STORAGE_BUCKET: str = "evidence"
    
    # Storage (Local fallback / max size)
    STORAGE_PATH: str = "./app/storage"
    MAX_UPLOAD_SIZE: int = 5242880 # 5MB

    # Auth / JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8501"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
