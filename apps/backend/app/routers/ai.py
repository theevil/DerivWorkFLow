"""
AI Router for managing AI analysis, learning, and risk management endpoints
"""


from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.models import (
    MarketAnalysisRequest,
    TradingDecisionRequest,
    RiskAssessmentRequest,
    TrainingRequest,
    SignalGenerationRequest
)
from app.ai.decision_engine import TradingDecision, TradingDecisionEngine
from app.ai.learning_system import HistoricalLearningSystem
from app.ai.market_analyzer import AdvancedMarketAnalyzer, MarketAnalysisResult
from app.ai.risk_manager import AIRiskManager, RiskAssessment
from app.ai.local_ai_manager import local_ai_manager
from app.core.ai_analysis import EnhancedTradingSignalGenerator
from app.core.database import get_database
from app.crud.trading import get_user_positions, get_user_trading_parameters
from app.models.user import User
from app.models.settings import AIConfiguration
from app.routers.auth import get_current_user

router = APIRouter()


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
        decision = await decision_engine.make_trading_decision(
            symbol=request.symbol,
            price_history=request.price_history,
            current_price=request.current_price,
            user_context=request.user_context
        )

        return decision

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating trading decision: {str(e)}"
        )


@router.post("/risk-assessment", response_model=RiskAssessment)
async def assess_risk(
    request: RiskAssessmentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Perform AI-powered risk assessment
    """
    try:
        risk_assessment = await risk_manager.assess_position_risk(
            symbol=request.symbol,
            position_size=request.position_size,
            account_balance=request.account_balance,
            market_data=request.market_data,
            user_context=request.user_context,
            portfolio_context=request.portfolio_context
        )

        return risk_assessment

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in risk assessment: {str(e)}"
        )


@router.post("/train-models")
async def train_models(
    request: TrainingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Train AI models with historical data
    """
    try:
        # Add training task to background queue
        background_tasks.add_task(
            learning_system.train_user_models,
            str(current_user.id),
            request.symbol,
            request.lookback_days
        )

        return {
            "message": "Training started in background",
            "user_id": str(current_user.id),
            "symbol": request.symbol,
            "lookback_days": request.lookback_days
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting training: {str(e)}"
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
        # Get user positions and trading parameters
        positions = await get_user_positions(str(current_user.id), db)
        await get_user_trading_parameters(str(current_user.id), db)

        # Generate signal
        signal = await enhanced_generator.generate_ai_signal(
            user_id=str(current_user.id),
            symbol=request.symbol,
            price_history=request.price_history,
            current_price=request.current_price,
            user_context=request.user_context,
            account_balance=request.account_balance,
            current_positions=positions
        )

        if signal:
            return signal
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to generate trading signal"
            )

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
        local_ai_available = settings.local_ai_enabled and bool(local_ai_manager.get_available_models())

        # Try to load models
        user_models_loaded = await learning_system.load_models(str(current_user.id))
        global_models_loaded = await learning_system.load_models("global")

        status_info = {
            "ai_analysis_available": ai_available or local_ai_available,
            "openai_configured": ai_available,
            "local_ai_configured": local_ai_available,
            "local_ai_models": local_ai_manager.get_available_models(),
            "user_models_loaded": user_models_loaded,
            "global_models_loaded": global_models_loaded,
            "models_available": list(learning_system.models.keys()),
            "model_performance": learning_system.get_model_performance(),
            "should_retrain": learning_system.should_retrain(str(current_user.id)),
            "features": {
                "advanced_market_analysis": ai_available or local_ai_available,
                "ai_decision_workflow": ai_available or local_ai_available,
                "risk_management": True,
                "historical_learning": len(learning_system.models) > 0,
                "adaptive_signals": ai_available or local_ai_available or len(learning_system.models) > 0
            }
        }

        return status_info

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI status: {str(e)}"
        )


@router.get("/ai-configuration", response_model=AIConfiguration)
async def get_ai_configuration(
    current_user: User = Depends(get_current_user)
):
    """
    Get AI configuration options and current settings
    """
    try:
        from app.core.config import settings

        # Test local AI availability
        local_ai_status = "unavailable"
        if settings.local_ai_enabled:
            available_models = local_ai_manager.get_available_models()
            if available_models:
                local_ai_status = "available"
            else:
                local_ai_status = "testing"

        return AIConfiguration(
            available_providers=["local", "openai", "hybrid"],
            current_provider=getattr(settings, 'ai_provider', 'local'),
            local_models=local_ai_manager.get_available_models(),
            openai_models=[
                "gpt-4o-mini",
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-3.5-turbo"
            ],
            recommended_model=settings.default_ai_model,
            local_ai_status=local_ai_status
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting AI configuration: {str(e)}"
        )


@router.post("/test-local-ai")
async def test_local_ai(
    current_user: User = Depends(get_current_user)
):
    """
    Test local AI model connectivity and functionality
    """
    try:
        available_models = local_ai_manager.get_available_models()

        if not available_models:
            return {
                "status": "unavailable",
                "message": "No local AI models available",
                "models": []
            }

        # Test each available model
        test_results = {}
        for model_name in available_models:
            try:
                is_working = await local_ai_manager.test_model_connection(model_name)
                test_results[model_name] = {
                    "available": True,
                    "working": is_working,
                    "status": "working" if is_working else "error"
                }
            except Exception as e:
                test_results[model_name] = {
                    "available": True,
                    "working": False,
                    "status": "error",
                    "error": str(e)
                }

        working_models = [name for name, result in test_results.items() if result["working"]]

        return {
            "status": "available" if working_models else "error",
            "message": f"Found {len(working_models)} working models" if working_models else "No working models found",
            "models": test_results,
            "working_models": working_models
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error testing local AI: {str(e)}"
        )


@router.post("/initialize-local-model/{model_name}")
async def initialize_local_model(
    model_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Initialize a specific local AI model
    """
    try:
        success = await local_ai_manager.initialize_model(model_name)

        if success:
            return {
                "status": "success",
                "message": f"Model {model_name} initialized successfully",
                "model_name": model_name
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to initialize model {model_name}"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing model: {str(e)}"
        )


@router.post("/retrain-check")
async def check_retrain_needed(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Check if models need retraining and start if needed
    """
    try:
        user_id = str(current_user.id)

        # Check if retraining is needed
        needs_retraining = learning_system.should_retrain(user_id)

        if needs_retraining:
            # Start retraining in background
            background_tasks.add_task(
                learning_system.retrain_user_models,
                user_id
            )

            return {
                "retraining_needed": True,
                "message": "Retraining started in background",
                "user_id": user_id
            }
        else:
            return {
                "retraining_needed": False,
                "message": "Models are up to date",
                "user_id": user_id
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking retrain status: {str(e)}"
        )
