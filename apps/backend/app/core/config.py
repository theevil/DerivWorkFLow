from pydantic_settings import BaseSettings
from typing import List
from datetime import timedelta


class Settings(BaseSettings):
    app_name: str = "Deriv Workflow API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    mongodb_uri: str = "mongodb://mongodb:27017"
    mongodb_db: str = "deriv"
    
    # Security
    secret_key: str = "your-secret-key-here"  # Change in production
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()