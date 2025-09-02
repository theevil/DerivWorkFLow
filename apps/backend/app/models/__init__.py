# Models for the application
# Domain models
from .user import User, UserCreate, UserInDB, TokenResponse, RefreshTokenRequest
from .trading import (
    TradePosition,
    TradePositionCreate,
    TradingParameters,
    TradingParametersCreate,
    TradingParametersUpdate,
    TradingSignal,
    MarketAnalysis
)

# API models
from .deriv import DerivTokenRequest
from .settings import UserSettings, SettingsUpdate
from .ai import (
    MarketAnalysisRequest,
    TradingDecisionRequest,
    RiskAssessmentRequest,
    TrainingRequest,
    SignalGenerationRequest
)
from .automation import (
    AutoTradingConfig,
    EmergencyStopRequest,
    TaskStatusResponse,
    WorkerStatusResponse
)

__all__ = [
    # Domain models
    "User", "UserCreate", "UserInDB", "TokenResponse", "RefreshTokenRequest",
    "TradePosition", "TradePositionCreate",
    "TradingParameters", "TradingParametersCreate", "TradingParametersUpdate",
    "TradingSignal", "MarketAnalysis",
    
    # API models
    "DerivTokenRequest",
    "UserSettings", "SettingsUpdate",
    "MarketAnalysisRequest", "TradingDecisionRequest", "RiskAssessmentRequest",
    "TrainingRequest", "SignalGenerationRequest",
    "AutoTradingConfig", "EmergencyStopRequest", "TaskStatusResponse", "WorkerStatusResponse"
]
