from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from bson import ObjectId


class TradingParametersBase(BaseModel):
    profit_top: float = Field(ge=0.1, le=100.0, description="Profit target percentage")
    profit_loss: float = Field(ge=0.1, le=100.0, description="Stop loss percentage")
    stop_loss: float = Field(ge=0.1, le=100.0, description="Maximum stop loss")
    take_profit: float = Field(ge=0.1, le=100.0, description="Take profit percentage")
    max_daily_loss: float = Field(ge=1.0, le=10000.0, description="Maximum daily loss amount")
    position_size: float = Field(ge=1.0, le=10000.0, description="Position size in USD")


class TradingParametersCreate(TradingParametersBase):
    pass


class TradingParametersUpdate(BaseModel):
    profit_top: Optional[float] = Field(None, ge=0.1, le=100.0)
    profit_loss: Optional[float] = Field(None, ge=0.1, le=100.0)
    stop_loss: Optional[float] = Field(None, ge=0.1, le=100.0)
    take_profit: Optional[float] = Field(None, ge=0.1, le=100.0)
    max_daily_loss: Optional[float] = Field(None, ge=1.0, le=10000.0)
    position_size: Optional[float] = Field(None, ge=1.0, le=10000.0)


class TradingParametersInDB(TradingParametersBase):
    id: Any = Field(default_factory=lambda: ObjectId(), alias="_id")
    user_id: Any
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class TradingParameters(TradingParametersBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_encoders": {ObjectId: str}
    }


class TradePositionBase(BaseModel):
    symbol: str = Field(description="Trading symbol (e.g., R_10, R_25)")
    contract_type: str = Field(description="Contract type (CALL, PUT)")
    amount: float = Field(ge=1.0, description="Trade amount in USD")
    duration: int = Field(ge=1, description="Trade duration")
    duration_unit: str = Field(default="m", description="Duration unit (m, h, d)")


class TradePositionCreate(TradePositionBase):
    pass


class TradePositionInDB(TradePositionBase):
    id: Any = Field(default_factory=lambda: ObjectId(), alias="_id")
    user_id: Any
    contract_id: Optional[str] = None
    entry_spot: Optional[float] = None
    exit_spot: Optional[float] = None
    current_spot: Optional[float] = None
    profit_loss: Optional[float] = None
    status: str = Field(default="pending", description="pending, open, closed, cancelled")
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class TradePosition(TradePositionBase):
    id: str
    user_id: str
    contract_id: Optional[str] = None
    entry_spot: Optional[float] = None
    exit_spot: Optional[float] = None
    current_spot: Optional[float] = None
    profit_loss: Optional[float] = None
    status: str
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_encoders": {ObjectId: str}
    }


class MarketAnalysisBase(BaseModel):
    symbol: str
    rsi: Optional[float] = None
    macd: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "sideways"
    volatility: Optional[float] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


class MarketAnalysisInDB(MarketAnalysisBase):
    id: Any = Field(default_factory=lambda: ObjectId(), alias="_id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    current_price: float
    price_history: List[float] = Field(default_factory=list)

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class MarketAnalysis(MarketAnalysisBase):
    id: str
    timestamp: datetime
    current_price: float
    price_history: List[float]

    model_config = {
        "json_encoders": {ObjectId: str}
    }


class TradingSignalBase(BaseModel):
    symbol: str
    signal_type: str = Field(description="BUY_CALL, BUY_PUT, HOLD")
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_amount: float = Field(ge=1.0)
    recommended_duration: int = Field(ge=1)
    reasoning: str = Field(description="AI reasoning for the signal")


class TradingSignalInDB(TradingSignalBase):
    id: Any = Field(default_factory=lambda: ObjectId(), alias="_id")
    user_id: Any
    created_at: datetime = Field(default_factory=datetime.utcnow)
    executed: bool = Field(default=False)
    trade_id: Optional[Any] = None

    model_config = {
        "json_encoders": {ObjectId: str},
        "populate_by_name": True,
        "arbitrary_types_allowed": True
    }


class TradingSignal(TradingSignalBase):
    id: str
    user_id: str
    created_at: datetime
    executed: bool
    trade_id: Optional[str] = None

    model_config = {
        "json_encoders": {ObjectId: str}
    }
