import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # App Configuration
    app_name: str = "Deriv Workflow API"
    environment: str = os.getenv("ENVIRONMENT", "development")
    api_v1_prefix: str = "/api/v1"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"

    # CORS Configuration
    backend_cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Database Configuration
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
    mongodb_db: str = os.getenv("MONGODB_DB", "deriv")

    # Security Configuration
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))  # 30 days

    # Deriv API Configuration
    deriv_app_id: str = os.getenv("DERIV_APP_ID", "98998")
    deriv_api_url: str = os.getenv("DERIV_API_URL", "wss://ws.binaryws.com/websockets/v3")

    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "app.log")

    # Rate Limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

    # AI Analysis Configuration
    ai_confidence_threshold: float = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.6"))
    ai_analysis_interval: int = int(os.getenv("AI_ANALYSIS_INTERVAL", "30"))  # seconds
    max_positions_per_user: int = int(os.getenv("MAX_POSITIONS_PER_USER", "10"))

    # LangChain & LangGraph Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    langchain_api_key: str = os.getenv("LANGCHAIN_API_KEY", "")
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "deriv-trading")
    ai_model: str = os.getenv("AI_MODEL", "gpt-4o-mini")
    ai_temperature: float = float(os.getenv("AI_TEMPERATURE", "0.1"))
    ai_max_tokens: int = int(os.getenv("AI_MAX_TOKENS", "1000"))

    # Local AI Configuration
    local_ai_enabled: bool = os.getenv("LOCAL_AI_ENABLED", "True").lower() == "true"
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    default_ai_model: str = os.getenv("DEFAULT_AI_MODEL", "phi-3-mini")
    local_ai_fallback_enabled: bool = os.getenv("LOCAL_AI_FALLBACK_ENABLED", "True").lower() == "true"
    local_ai_timeout: int = int(os.getenv("LOCAL_AI_TIMEOUT", "30"))  # seconds
    local_ai_max_retries: int = int(os.getenv("LOCAL_AI_MAX_RETRIES", "3"))

    # Historical Learning Configuration
    learning_data_lookback_days: int = int(os.getenv("LEARNING_DATA_LOOKBACK_DAYS", "30"))
    min_training_samples: int = int(os.getenv("MIN_TRAINING_SAMPLES", "100"))
    retrain_interval_hours: int = int(os.getenv("MODEL_RETRAIN_INTERVAL_HOURS", "24"))

    # Background Tasks Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    # Automation Configuration
    auto_trading_enabled: bool = os.getenv("AUTO_TRADING_ENABLED", "False").lower() == "true"
    market_scan_interval_seconds: int = int(os.getenv("MARKET_SCAN_INTERVAL_SECONDS", "30"))
    position_monitor_interval_seconds: int = int(os.getenv("POSITION_MONITOR_INTERVAL_SECONDS", "10"))
    signal_execution_delay_seconds: int = int(os.getenv("SIGNAL_EXECUTION_DELAY_SECONDS", "5"))
    max_concurrent_positions: int = int(os.getenv("MAX_CONCURRENT_POSITIONS", "5"))

    # Risk Management Automation
    auto_stop_loss_enabled: bool = os.getenv("AUTO_STOP_LOSS_ENABLED", "True").lower() == "true"
    auto_take_profit_enabled: bool = os.getenv("AUTO_TAKE_PROFIT_ENABLED", "True").lower() == "true"
    emergency_stop_enabled: bool = os.getenv("EMERGENCY_STOP_ENABLED", "True").lower() == "true"
    circuit_breaker_enabled: bool = os.getenv("CIRCUIT_BREAKER_ENABLED", "True").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
