from typing import Optional, Any
from pydantic import BaseModel, Field


class MarketAnalysisRequest(BaseModel):
    symbol: str = Field(description="Trading symbol")
    price_history: list[float] = Field(description="Historical price data", min_items=10, max_items=1000)
    current_price: float = Field(description="Current market price", gt=0)
    market_context: Optional[dict[str, Any]] = Field(default={}, description="Additional market context")


class TradingDecisionRequest(BaseModel):
    symbol: str = Field(description="Trading symbol")
    price_history: list[float] = Field(description="Historical price data", min_items=10, max_items=1000)
    current_price: float = Field(description="Current market price", gt=0)
    account_balance: float = Field(description="Account balance", gt=0)
    risk_tolerance: str = Field(default="medium", description="Risk tolerance: low, medium, high")
    experience_level: str = Field(default="intermediate", description="Experience: beginner, intermediate, expert")
    max_daily_loss: float = Field(default=100, description="Maximum daily loss limit", gt=0)
    max_position_size: float = Field(default=50, description="Maximum position size", gt=0)


class RiskAssessmentRequest(BaseModel):
    symbol: str = Field(description="Trading symbol")
    position_size: float = Field(description="Position size", gt=0)
    account_balance: float = Field(description="Account balance", gt=0)
    current_price: float = Field(description="Current market price", gt=0)
    volatility: float = Field(default=0.2, description="Market volatility", ge=0, le=2)
    risk_tolerance: str = Field(default="medium", description="Risk tolerance")
    experience_level: str = Field(default="intermediate", description="Experience level")


class TrainingRequest(BaseModel):
    user_specific: bool = Field(default=True, description="Train user-specific models")
    symbols: Optional[list[str]] = Field(default=None, description="Specific symbols to train on")
    lookback_days: Optional[int] = Field(default=30, description="Days of historical data to use")


class SignalGenerationRequest(BaseModel):
    symbol: str = Field(description="Trading symbol")
    price_history: list[float] = Field(description="Historical price data")
    current_price: float = Field(description="Current market price", gt=0)
    use_ai: bool = Field(default=True, description="Use AI analysis")
