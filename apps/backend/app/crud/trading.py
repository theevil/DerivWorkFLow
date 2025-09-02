from datetime import datetime
from typing import Optional

from bson import ObjectId
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.trading import (
    MarketAnalysisInDB,
    TradePositionCreate,
    TradePositionInDB,
    TradingParametersCreate,
    TradingParametersInDB,
    TradingParametersUpdate,
    TradingSignalInDB,
)


# Trading Parameters CRUD
async def create_trading_parameters(
    db: AsyncIOMotorDatabase, user_id: str, params: TradingParametersCreate
) -> TradingParametersInDB:
    db_params = TradingParametersInDB(
        user_id=ObjectId(user_id),
        **params.model_dump()
    )

    result = await db.trading_parameters.insert_one(
        db_params.model_dump(by_alias=True, exclude=["id"])
    )
    db_params.id = result.inserted_id
    return db_params


async def get_user_trading_parameters(
    db: AsyncIOMotorDatabase, user_id: str
) -> Optional[TradingParametersInDB]:
    if params := await db.trading_parameters.find_one({"user_id": ObjectId(user_id)}):
        return TradingParametersInDB(**params)
    return None


async def update_trading_parameters(
    db: AsyncIOMotorDatabase, user_id: str, params_update: TradingParametersUpdate
) -> Optional[TradingParametersInDB]:
    update_data = params_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()

    if result := await db.trading_parameters.find_one_and_update(
        {"user_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=True,
    ):
        return TradingParametersInDB(**result)
    return None


# Trade Positions CRUD
async def create_trade_position(
    db: AsyncIOMotorDatabase, user_id: str, trade: TradePositionCreate
) -> TradePositionInDB:
    db_trade = TradePositionInDB(
        user_id=ObjectId(user_id),
        **trade.model_dump()
    )

    result = await db.trade_positions.insert_one(
        db_trade.model_dump(by_alias=True, exclude=["id"])
    )
    db_trade.id = result.inserted_id
    return db_trade


async def get_user_positions(
    db: AsyncIOMotorDatabase, user_id: str, status: Optional[str] = None
) -> list[TradePositionInDB]:
    query = {"user_id": ObjectId(user_id)}
    if status:
        query["status"] = status

    cursor = db.trade_positions.find(query).sort("created_at", -1)
    positions = []
    async for position in cursor:
        positions.append(TradePositionInDB(**position))
    return positions


async def get_position_by_id(
    db: AsyncIOMotorDatabase, position_id: str, user_id: str
) -> Optional[TradePositionInDB]:
    if position := await db.trade_positions.find_one({
        "_id": ObjectId(position_id),
        "user_id": ObjectId(user_id)
    }):
        return TradePositionInDB(**position)
    return None


async def update_position(
    db: AsyncIOMotorDatabase, position_id: str, user_id: str, update_data: dict
) -> Optional[TradePositionInDB]:
    update_data["updated_at"] = datetime.utcnow()

    if result := await db.trade_positions.find_one_and_update(
        {"_id": ObjectId(position_id), "user_id": ObjectId(user_id)},
        {"$set": update_data},
        return_document=True,
    ):
        return TradePositionInDB(**result)
    return None


# Market Analysis CRUD
async def create_market_analysis(
    db: AsyncIOMotorDatabase, analysis: MarketAnalysisInDB
) -> MarketAnalysisInDB:
    result = await db.market_analysis.insert_one(
        analysis.model_dump(by_alias=True, exclude=["id"])
    )
    analysis.id = result.inserted_id
    return analysis


async def get_latest_market_analysis(
    db: AsyncIOMotorDatabase, symbol: str
) -> Optional[MarketAnalysisInDB]:
    if analysis := await db.market_analysis.find_one(
        {"symbol": symbol}, sort=[("timestamp", -1)]
    ):
        return MarketAnalysisInDB(**analysis)
    return None


async def get_market_analysis_history(
    db: AsyncIOMotorDatabase, symbol: str, limit: int = 100
) -> list[MarketAnalysisInDB]:
    cursor = db.market_analysis.find({"symbol": symbol}).sort("timestamp", -1).limit(limit)
    analyses = []
    async for analysis in cursor:
        analyses.append(MarketAnalysisInDB(**analysis))
    return analyses


# Trading Signals CRUD
async def create_trading_signal(
    db: AsyncIOMotorDatabase, user_id: str, signal: TradingSignalInDB
) -> TradingSignalInDB:
    signal.user_id = ObjectId(user_id)
    result = await db.trading_signals.insert_one(
        signal.model_dump(by_alias=True, exclude=["id"])
    )
    signal.id = result.inserted_id
    return signal


async def get_user_signals(
    db: AsyncIOMotorDatabase, user_id: str, executed: Optional[bool] = None
) -> list[TradingSignalInDB]:
    query = {"user_id": ObjectId(user_id)}
    if executed is not None:
        query["executed"] = executed

    cursor = db.trading_signals.find(query).sort("created_at", -1)
    signals = []
    async for signal in cursor:
        signals.append(TradingSignalInDB(**signal))
    return signals


async def update_signal_executed(
    db: AsyncIOMotorDatabase, signal_id: str, trade_id: str
) -> Optional[TradingSignalInDB]:
    if result := await db.trading_signals.find_one_and_update(
        {"_id": ObjectId(signal_id)},
        {"$set": {"executed": True, "trade_id": ObjectId(trade_id)}},
        return_document=True,
    ):
        return TradingSignalInDB(**result)
    return None


# Analytics and reporting
async def get_all_open_positions(db: AsyncIOMotorDatabase) -> list[TradePositionInDB]:
    """Get all open positions across all users"""
    try:
        cursor = db.trade_positions.find({"status": "open"})
        positions = []
        async for doc in cursor:
            positions.append(TradePositionInDB(**doc))
        return positions
    except Exception as e:
        logger.error(f"Error getting all open positions: {e}")
        return []


async def get_all_active_users(db: AsyncIOMotorDatabase) -> list[str]:
    """Get all active user IDs"""
    try:
        cursor = db.users.find({"active": {"$ne": False}}, {"_id": 1})
        user_ids = []
        async for doc in cursor:
            user_ids.append(str(doc["_id"]))
        return user_ids
    except Exception as e:
        logger.error(f"Error getting active users: {e}")
        return []


async def get_user_trading_stats(db: AsyncIOMotorDatabase, user_id: str) -> dict:
    """Get comprehensive trading statistics for a user"""
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {
            "$group": {
                "_id": None,
                "total_trades": {"$sum": 1},
                "winning_trades": {
                    "$sum": {"$cond": [{"$gt": ["$profit_loss", 0]}, 1, 0]}
                },
                "losing_trades": {
                    "$sum": {"$cond": [{"$lt": ["$profit_loss", 0]}, 1, 0]}
                },
                "total_profit": {"$sum": "$profit_loss"},
                "avg_profit": {"$avg": "$profit_loss"},
                "max_profit": {"$max": "$profit_loss"},
                "max_loss": {"$min": "$profit_loss"},
            }
        }
    ]

    result = await db.trade_positions.aggregate(pipeline).to_list(1)
    if result:
        stats = result[0]
        stats["win_rate"] = (
            stats["winning_trades"] / stats["total_trades"]
            if stats["total_trades"] > 0 else 0
        )
        return stats

    return {
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "total_profit": 0,
        "avg_profit": 0,
        "max_profit": 0,
        "max_loss": 0,
        "win_rate": 0,
    }
