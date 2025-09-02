from typing import Optional
from pydantic import BaseModel, Field


class UserSettings(BaseModel):
    """User settings model"""
    # Deriv API Configuration
    deriv_token: Optional[str] = None
    deriv_app_id: str = Field(default="1089")

    # AI Configuration
    ai_confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    ai_analysis_interval: int = Field(default=30, ge=10, le=300)
    max_positions_per_user: int = Field(default=10, ge=1, le=50)
    ai_model: str = Field(default="gpt-4o-mini")
    ai_temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    ai_max_tokens: int = Field(default=1000, ge=100, le=4000)

    # OpenAI Configuration (stored encrypted)
    openai_api_key: Optional[str] = None
    langchain_api_key: Optional[str] = None
    langsmith_project: str = Field(default="deriv-trading")

    # Risk Management
    auto_stop_loss_enabled: bool = Field(default=True)
    auto_take_profit_enabled: bool = Field(default=True)
    emergency_stop_enabled: bool = Field(default=True)
    circuit_breaker_enabled: bool = Field(default=True)

    # Automation Settings
    auto_trading_enabled: bool = Field(default=False)
    market_scan_interval: int = Field(default=30, ge=5, le=300)
    position_monitor_interval: int = Field(default=10, ge=1, le=60)
    signal_execution_delay: int = Field(default=5, ge=0, le=30)
    max_concurrent_positions: int = Field(default=5, ge=1, le=20)

    # Learning Configuration
    learning_data_lookback_days: int = Field(default=30, ge=1, le=365)
    min_training_samples: int = Field(default=100, ge=10, le=1000)
    retrain_interval_hours: int = Field(default=24, ge=1, le=168)


class SettingsUpdate(BaseModel):
    """Settings update model with optional fields"""
    # Deriv API Configuration
    deriv_token: Optional[str] = None
    deriv_app_id: Optional[str] = None

    # AI Configuration
    ai_confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    ai_analysis_interval: Optional[int] = Field(None, ge=10, le=300)
    max_positions_per_user: Optional[int] = Field(None, ge=1, le=50)
    ai_model: Optional[str] = None
    ai_temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    ai_max_tokens: Optional[int] = Field(None, ge=100, le=4000)

    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    langchain_api_key: Optional[str] = None
    langsmith_project: Optional[str] = None

    # Risk Management
    auto_stop_loss_enabled: Optional[bool] = None
    auto_take_profit_enabled: Optional[bool] = None
    emergency_stop_enabled: Optional[bool] = None
    circuit_breaker_enabled: Optional[bool] = None

    # Automation Settings
    auto_trading_enabled: Optional[bool] = None
    market_scan_interval: Optional[int] = Field(None, ge=5, le=300)
    position_monitor_interval: Optional[int] = Field(None, ge=1, le=60)
    signal_execution_delay: Optional[int] = Field(None, ge=0, le=30)
    max_concurrent_positions: Optional[int] = Field(None, ge=1, le=20)

    # Learning Configuration
    learning_data_lookback_days: Optional[int] = Field(None, ge=1, le=365)
    min_training_samples: Optional[int] = Field(None, ge=10, le=1000)
    retrain_interval_hours: Optional[int] = Field(None, ge=1, le=168)
