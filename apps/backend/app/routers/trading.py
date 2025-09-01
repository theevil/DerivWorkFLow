from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.trading import (
    TradingParameters,
    TradingParametersCreate,
    TradingParametersUpdate,
    TradePosition,
    TradePositionCreate,
    MarketAnalysis,
    TradingSignal,
)
from app.crud.trading import (
    create_trading_parameters,
    get_user_trading_parameters,
    update_trading_parameters,
    create_trade_position,
    get_user_positions,
    get_position_by_id,
    update_position,
    get_latest_market_analysis,
    get_market_analysis_history,
    get_user_signals,
    get_user_trading_stats,
)

router = APIRouter()


# Trading Parameters endpoints
@router.post("/parameters", response_model=TradingParameters)
async def create_user_trading_parameters(
    params: TradingParametersCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Create trading parameters for the current user"""
    # Check if parameters already exist
    existing = await get_user_trading_parameters(db, current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trading parameters already exist. Use PUT to update."
        )
    
    db_params = await create_trading_parameters(db, current_user.id, params)
    return TradingParameters(
        id=str(db_params.id),
        user_id=str(db_params.user_id),
        **db_params.model_dump(exclude=["id", "user_id"])
    )


@router.get("/parameters", response_model=Optional[TradingParameters])
async def get_trading_parameters(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Get trading parameters for the current user"""
    params = await get_user_trading_parameters(db, current_user.id)
    if not params:
        return None
    
    return TradingParameters(
        id=str(params.id),
        user_id=str(params.user_id),
        **params.model_dump(exclude=["id", "user_id"])
    )


@router.put("/parameters", response_model=TradingParameters)
async def update_user_trading_parameters(
    params_update: TradingParametersUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Update trading parameters for the current user"""
    updated_params = await update_trading_parameters(db, current_user.id, params_update)
    if not updated_params:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trading parameters not found"
        )
    
    return TradingParameters(
        id=str(updated_params.id),
        user_id=str(updated_params.user_id),
        **updated_params.model_dump(exclude=["id", "user_id"])
    )


# Trade Positions endpoints
@router.post("/positions", response_model=TradePosition)
async def create_position(
    trade: TradePositionCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Create a new trade position"""
    db_trade = await create_trade_position(db, current_user.id, trade)
    return TradePosition(
        id=str(db_trade.id),
        user_id=str(db_trade.user_id),
        **db_trade.model_dump(exclude=["id", "user_id"])
    )


@router.get("/positions", response_model=List[TradePosition])
async def get_positions(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Get trade positions for the current user"""
    positions = await get_user_positions(db, current_user.id, status)
    return [
        TradePosition(
            id=str(pos.id),
            user_id=str(pos.user_id),
            **pos.model_dump(exclude=["id", "user_id"])
        )
        for pos in positions
    ]


@router.get("/positions/{position_id}", response_model=TradePosition)
async def get_position(
    position_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Get a specific trade position"""
    position = await get_position_by_id(db, position_id, current_user.id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )
    
    return TradePosition(
        id=str(position.id),
        user_id=str(position.user_id),
        **position.model_dump(exclude=["id", "user_id"])
    )


@router.put("/positions/{position_id}/close")
async def close_position(
    position_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Close a trade position"""
    position = await get_position_by_id(db, position_id, current_user.id)
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )
    
    if position.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position is not open"
        )
    
    updated_position = await update_position(
        db, position_id, current_user.id, {"status": "closed"}
    )
    
    return {"message": "Position closed successfully"}


# Market Analysis endpoints
@router.get("/analysis/{symbol}", response_model=Optional[MarketAnalysis])
async def get_market_analysis(
    symbol: str,
    db = Depends(get_database),
):
    """Get latest market analysis for a symbol"""
    analysis = await get_latest_market_analysis(db, symbol)
    if not analysis:
        return None
    
    return MarketAnalysis(
        id=str(analysis.id),
        **analysis.model_dump(exclude=["id"])
    )


@router.get("/analysis/{symbol}/history", response_model=List[MarketAnalysis])
async def get_analysis_history(
    symbol: str,
    limit: int = 100,
    db = Depends(get_database),
):
    """Get historical market analysis for a symbol"""
    analyses = await get_market_analysis_history(db, symbol, limit)
    return [
        MarketAnalysis(
            id=str(analysis.id),
            **analysis.model_dump(exclude=["id"])
        )
        for analysis in analyses
    ]


# Trading Signals endpoints
@router.get("/signals", response_model=List[TradingSignal])
async def get_trading_signals(
    executed: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Get trading signals for the current user"""
    signals = await get_user_signals(db, current_user.id, executed)
    return [
        TradingSignal(
            id=str(signal.id),
            user_id=str(signal.user_id),
            trade_id=str(signal.trade_id) if signal.trade_id else None,
            **signal.model_dump(exclude=["id", "user_id", "trade_id"])
        )
        for signal in signals
    ]


# Analytics endpoints
@router.get("/stats")
async def get_trading_statistics(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Get comprehensive trading statistics for the current user"""
    return await get_user_trading_stats(db, current_user.id)
