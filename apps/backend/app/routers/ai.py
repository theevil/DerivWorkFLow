"""
AI Router for managing AI analysis, learning, and risk management endpoints
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from app.core.database import get_database
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.trading import TradingParameters
from app.crud.trading import get_user_trading_parameters, get_user_positions
from app.ai.market_analyzer import AdvancedMarketAnalyzer, MarketAnalysisResult
from app.ai.decision_engine import TradingDecisionEngine, TradingDecision
from app.ai.learning_system import HistoricalLearningSystem
from app.ai.risk_manager import AIRiskManager, RiskAssessment, PortfolioRisk
from app.core.ai_analysis import EnhancedTradingSignalGenerator

router = APIRouter()

# Pydantic models for API requests/responses

class MarketAnalysisRequest(BaseModel):
    symbol: str = Field(description="Trading symbol")
    price_history: List[float] = Field(description="Historical price data", min_items=10, max_items=1000)
    current_price: float = Field(description="Current market price", gt=0)
    market_context: Optional[Dict[str, Any]] = Field(default={}, description="Additional market context")


class TradingDecisionRequest(BaseModel):
    symbol: str = Field(description="Trading symbol")
    price_history: List[float] = Field(description="Historical price data", min_items=10, max_items=1000)
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
    symbols: Optional[List[str]] = Field(default=None, description="Specific symbols to train on")
    lookback_days: Optional[int] = Field(default=30, description="Days of historical data to use")


class SignalGenerationRequest(BaseModel):
    symbol: str = Field(description="Trading symbol")
    price_history: List[float] = Field(description="Historical price data")
    current_price: float = Field(description="Current market price", gt=0)
    use_ai: bool = Field(default=True, description="Use AI analysis")


# Initialize AI components
enhanced_generator = EnhancedTradingSignalGenerator()
market_analyzer = AdvancedMarketAnalyzer()
decision_engine = TradingDecisionEngine()
learning_system = HistoricalLearningSystem()
risk_manager = AIRiskManager()


@router.post("/analyze-market", response_model=MarketAnalysisResult)
async def analyze_market(
    request: MarketAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform advanced AI market analysis on the provided data
    """
    try:
        analysis = await market_analyzer.analyze_market_advanced(
            symbol=request.symbol,
            price_history=request.price_history,
            current_price=request.current_price,
            market_context=request.market_context
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in market analysis: {str(e)}"
        )


@router.post("/trading-decision", response_model=TradingDecision)
async def make_trading_decision(
    request: TradingDecisionRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate comprehensive trading decision using AI workflow
    """
    try:
        user_context = {
            "account_balance": request.account_balance,
            "risk_tolerance": request.risk_tolerance,
            "experience_level": request.experience_level,
            "max_daily_loss": request.max_daily_loss,
            "max_position_size": request.max_position_size,
            "current_positions": 0  # Would be fetched from database
        }
        
        decision = await decision_engine.make_trading_decision(
            symbol=request.symbol,
            price_history=request.price_history,
            current_price=request.current_price,
            user_context=user_context
        )
        
        return decision
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in trading decision: {str(e)}"
        )


@router.post("/assess-risk", response_model=RiskAssessment)
async def assess_position_risk(
    request: RiskAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Assess risk for a potential trading position
    """
    try:
        # Get user's current positions for portfolio context
        positions = await get_user_positions(db, str(current_user.id))
        
        market_data = {
            "current_price": request.current_price,
            "volatility": request.volatility,
            "trend": "sideways",  # Would be determined from analysis
            "session": "active"
        }
        
        user_context = {
            "risk_tolerance": request.risk_tolerance,
            "experience_level": request.experience_level,
            "account_balance": request.account_balance
        }
        
        portfolio_context = {
            "position_count": len(positions),
            "total_exposure": sum(pos.amount for pos in positions if pos.status == "open"),
            "daily_pnl": 0  # Would be calculated from actual P&L
        }
        
        risk_assessment = await risk_manager.assess_position_risk(
            symbol=request.symbol,
            position_size=request.position_size,
            account_balance=request.account_balance,
            market_data=market_data,
            user_context=user_context,
            portfolio_context=portfolio_context
        )
        
        return risk_assessment
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in risk assessment: {str(e)}"
        )


@router.get("/portfolio-risk", response_model=PortfolioRisk)
async def assess_portfolio_risk(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Assess overall portfolio risk for the current user
    """
    try:
        # Get user's positions and trading parameters
        positions = await get_user_positions(db, str(current_user.id))
        trading_params = await get_user_trading_parameters(db, str(current_user.id))
        
        if not trading_params:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trading parameters not found. Please configure trading parameters first."
            )
        
        # Estimate account balance (would be fetched from actual account data)
        account_balance = 1000.0  # Default, should be fetched from user's account
        
        portfolio_risk = await risk_manager.assess_portfolio_risk(
            positions=positions,
            account_balance=account_balance,
            trading_params=trading_params
        )
        
        return portfolio_risk
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in portfolio risk assessment: {str(e)}"
        )


@router.post("/train-models")
async def train_ai_models(
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Train AI models using historical data (background task)
    """
    try:
        user_id = str(current_user.id) if request.user_specific else None
        
        # Add training task to background
        background_tasks.add_task(
            learning_system.train_models,
            db,
            user_id
        )
        
        return {
            "message": "Model training started in background",
            "user_specific": request.user_specific,
            "user_id": user_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting model training: {str(e)}"
        )


@router.get("/model-performance")
async def get_model_performance(
    current_user: User = Depends(get_current_user)
):
    """
    Get current AI model performance metrics
    """
    try:
        performance = learning_system.get_model_performance()
        
        return {
            "models": list(performance.keys()),
            "performance": performance,
            "last_training": learning_system.last_training_time.get(str(current_user.id), "Never")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving model performance: {str(e)}"
        )


@router.get("/trading-patterns")
async def analyze_trading_patterns(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Analyze user's trading patterns for insights
    """
    try:
        patterns = await learning_system.analyze_trading_patterns(db, str(current_user.id))
        
        return patterns
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing trading patterns: {str(e)}"
        )


@router.post("/generate-signal")
async def generate_ai_signal(
    request: SignalGenerationRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Generate AI-powered trading signal
    """
    try:
        # Get user context
        trading_params = await get_user_trading_parameters(db, str(current_user.id))
        positions = await get_user_positions(db, str(current_user.id))
        
        if not trading_params:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trading parameters not found"
            )
        
        user_context = {
            "risk_tolerance": "medium",  # Would be stored in user profile
            "experience_level": "intermediate",  # Would be stored in user profile
            "account_balance": 1000.0,  # Would be fetched from account
            "max_daily_loss": trading_params.max_daily_loss,
            "max_position_size": trading_params.position_size
        }
        
        if request.use_ai:
            signal = await enhanced_generator.generate_ai_signal(
                user_id=str(current_user.id),
                symbol=request.symbol,
                price_history=request.price_history,
                current_price=request.current_price,
                user_context=user_context,
                account_balance=user_context["account_balance"],
                current_positions=positions
            )
        else:
            # Use traditional signal generation
            from app.core.ai_analysis import MarketAnalyzer, TradingSignalGenerator
            
            analyzer = MarketAnalyzer()
            signal_generator = TradingSignalGenerator()
            
            # Create market analysis
            analysis = analyzer.analyze_market(
                symbol=request.symbol,
                price_history=request.price_history,
                current_price=request.current_price
            )
            
            signal = signal_generator.generate_signal(
                user_id=str(current_user.id),
                symbol=request.symbol,
                analysis=analysis,
                trading_params=trading_params.dict()
            )
        
        if signal:
            return {
                "signal_generated": True,
                "signal_type": signal.signal_type,
                "confidence": signal.confidence,
                "recommended_amount": signal.recommended_amount,
                "reasoning": signal.reasoning,
                "ai_powered": request.use_ai
            }
        else:
            return {
                "signal_generated": False,
                "message": "No trading signal generated",
                "ai_powered": request.use_ai
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating signal: {str(e)}"
        )


@router.get("/ai-status")
async def get_ai_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get current AI system status and capabilities
    """
    try:
        # Check what AI features are available
        from app.core.config import settings
        
        ai_available = bool(settings.openai_api_key)
        
        # Try to load models
        user_models_loaded = await learning_system.load_models(str(current_user.id))
        global_models_loaded = await learning_system.load_models("global")
        
        status_info = {
            "ai_analysis_available": ai_available,
            "langchain_configured": ai_available,
            "user_models_loaded": user_models_loaded,
            "global_models_loaded": global_models_loaded,
            "models_available": list(learning_system.models.keys()),
            "model_performance": learning_system.get_model_performance(),
            "should_retrain": learning_system.should_retrain(str(current_user.id)),
            "features": {
                "advanced_market_analysis": ai_available,
                "ai_decision_workflow": ai_available,
                "risk_management": True,
                "historical_learning": len(learning_system.models) > 0,
                "adaptive_signals": ai_available or len(learning_system.models) > 0
            }
        }
        
        return status_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI status: {str(e)}"
        )


@router.post("/retrain-check")
async def check_retrain_needed(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Check if models need retraining and optionally start retraining
    """
    try:
        user_id = str(current_user.id)
        should_retrain = learning_system.should_retrain(user_id)
        
        result = {
            "should_retrain": should_retrain,
            "last_training": learning_system.last_training_time.get(user_id, "Never"),
            "retrain_interval_hours": 24
        }
        
        if should_retrain:
            # Start retraining in background
            background_tasks.add_task(
                learning_system.train_models,
                db,
                user_id
            )
            result["retraining_started"] = True
        else:
            result["retraining_started"] = False
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking retrain status: {str(e)}"
        )
