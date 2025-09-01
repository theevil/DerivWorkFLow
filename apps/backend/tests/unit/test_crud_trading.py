"""
Unit tests for app.crud.trading module.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId

from app.crud.trading import (
    create_trading_parameters,
    get_user_trading_parameters,
    update_trading_parameters,
    create_trade_position,
    get_user_positions,
    get_position_by_id,
    update_position,
    create_market_analysis,
    get_latest_market_analysis,
    get_market_analysis_history,
    create_trading_signal,
    get_user_signals,
    update_signal_executed,
    get_user_trading_stats
)
from app.models.trading import (
    TradingParametersCreate,
    TradingParametersInDB,
    TradingParametersUpdate,
    TradePositionCreate,
    TradePositionInDB,
    MarketAnalysisInDB,
    TradingSignalInDB
)


class TestTradingParametersCRUD:
    """Test trading parameters CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_trading_parameters(self):
        """Test creating trading parameters."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        params_create = TradingParametersCreate(
            profit_top=10.0,
            profit_loss=5.0,
            stop_loss=15.0,
            take_profit=8.0,
            max_daily_loss=100.0,
            position_size=10.0
        )
        
        inserted_id = ObjectId()
        mock_db.trading_parameters.insert_one.return_value.inserted_id = inserted_id
        
        result = await create_trading_parameters(mock_db, user_id, params_create)
        
        assert result is not None
        assert isinstance(result, TradingParametersInDB)
        assert result.id == inserted_id
        assert result.user_id == ObjectId(user_id)
        assert result.profit_top == 10.0
        assert result.profit_loss == 5.0
        assert result.stop_loss == 15.0
        assert result.take_profit == 8.0
        assert result.max_daily_loss == 100.0
        assert result.position_size == 10.0
        
        # Verify database insert was called
        mock_db.trading_parameters.insert_one.assert_called_once()
        call_args = mock_db.trading_parameters.insert_one.call_args[0][0]
        assert call_args["user_id"] == ObjectId(user_id)
        assert call_args["profit_top"] == 10.0
    
    @pytest.mark.asyncio
    async def test_get_user_trading_parameters_exists(self):
        """Test getting existing trading parameters."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        
        params_data = {
            "_id": ObjectId(),
            "user_id": ObjectId(user_id),
            "profit_top": 10.0,
            "profit_loss": 5.0,
            "stop_loss": 15.0,
            "take_profit": 8.0,
            "max_daily_loss": 100.0,
            "position_size": 10.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        mock_db.trading_parameters.find_one.return_value = params_data
        
        result = await get_user_trading_parameters(mock_db, user_id)
        
        assert result is not None
        assert isinstance(result, TradingParametersInDB)
        assert result.user_id == ObjectId(user_id)
        assert result.profit_top == 10.0
        
        mock_db.trading_parameters.find_one.assert_called_once_with(
            {"user_id": ObjectId(user_id)}
        )
    
    @pytest.mark.asyncio
    async def test_get_user_trading_parameters_not_exists(self):
        """Test getting non-existent trading parameters."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        
        mock_db.trading_parameters.find_one.return_value = None
        
        result = await get_user_trading_parameters(mock_db, user_id)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_trading_parameters(self):
        """Test updating trading parameters."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        params_update = TradingParametersUpdate(
            profit_top=15.0,
            position_size=20.0
        )
        
        updated_params_data = {
            "_id": ObjectId(),
            "user_id": ObjectId(user_id),
            "profit_top": 15.0,
            "profit_loss": 5.0,
            "stop_loss": 15.0,
            "take_profit": 8.0,
            "max_daily_loss": 100.0,
            "position_size": 20.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        mock_db.trading_parameters.find_one_and_update.return_value = updated_params_data
        
        result = await update_trading_parameters(mock_db, user_id, params_update)
        
        assert result is not None
        assert isinstance(result, TradingParametersInDB)
        assert result.profit_top == 15.0
        assert result.position_size == 20.0
        
        # Verify update was called correctly
        mock_db.trading_parameters.find_one_and_update.assert_called_once()
        call_args = mock_db.trading_parameters.find_one_and_update.call_args
        
        assert call_args[0][0] == {"user_id": ObjectId(user_id)}
        update_data = call_args[0][1]["$set"]
        assert update_data["profit_top"] == 15.0
        assert update_data["position_size"] == 20.0
        assert "updated_at" in update_data
    
    @pytest.mark.asyncio
    async def test_update_trading_parameters_not_found(self):
        """Test updating non-existent trading parameters."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        params_update = TradingParametersUpdate(profit_top=15.0)
        
        mock_db.trading_parameters.find_one_and_update.return_value = None
        
        result = await update_trading_parameters(mock_db, user_id, params_update)
        
        assert result is None


class TestTradePositionsCRUD:
    """Test trade positions CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_trade_position(self):
        """Test creating a trade position."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        trade_create = TradePositionCreate(
            symbol="R_10",
            contract_type="CALL",
            amount=10.0,
            duration=5,
            duration_unit="m"
        )
        
        inserted_id = ObjectId()
        mock_db.trade_positions.insert_one.return_value.inserted_id = inserted_id
        
        result = await create_trade_position(mock_db, user_id, trade_create)
        
        assert result is not None
        assert isinstance(result, TradePositionInDB)
        assert result.id == inserted_id
        assert result.user_id == ObjectId(user_id)
        assert result.symbol == "R_10"
        assert result.contract_type == "CALL"
        assert result.amount == 10.0
        assert result.duration == 5
        assert result.duration_unit == "m"
        assert result.status == "pending"  # Default status
        
        # Verify database insert was called
        mock_db.trade_positions.insert_one.assert_called_once()
        call_args = mock_db.trade_positions.insert_one.call_args[0][0]
        assert call_args["user_id"] == ObjectId(user_id)
        assert call_args["symbol"] == "R_10"
    
    @pytest.mark.asyncio
    async def test_get_user_positions_all(self):
        """Test getting all user positions."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        
        position_data = [
            {
                "_id": ObjectId(),
                "user_id": ObjectId(user_id),
                "symbol": "R_10",
                "contract_type": "CALL",
                "amount": 10.0,
                "duration": 5,
                "status": "open",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "user_id": ObjectId(user_id),
                "symbol": "R_25",
                "contract_type": "PUT",
                "amount": 15.0,
                "duration": 10,
                "status": "closed",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.__aiter__.return_value = iter(position_data)
        mock_db.trade_positions.find.return_value.sort.return_value = mock_cursor
        
        result = await get_user_positions(mock_db, user_id)
        
        assert len(result) == 2
        assert all(isinstance(pos, TradePositionInDB) for pos in result)
        assert result[0].symbol == "R_10"
        assert result[1].symbol == "R_25"
        
        # Verify query
        mock_db.trade_positions.find.assert_called_once_with(
            {"user_id": ObjectId(user_id)}
        )
    
    @pytest.mark.asyncio
    async def test_get_user_positions_by_status(self):
        """Test getting user positions by status."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        status = "open"
        
        position_data = [
            {
                "_id": ObjectId(),
                "user_id": ObjectId(user_id),
                "symbol": "R_10",
                "contract_type": "CALL",
                "amount": 10.0,
                "duration": 5,
                "status": "open",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        # Mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.__aiter__.return_value = iter(position_data)
        mock_db.trade_positions.find.return_value.sort.return_value = mock_cursor
        
        result = await get_user_positions(mock_db, user_id, status)
        
        assert len(result) == 1
        assert result[0].status == "open"
        
        # Verify query includes status
        mock_db.trade_positions.find.assert_called_once_with(
            {"user_id": ObjectId(user_id), "status": "open"}
        )
    
    @pytest.mark.asyncio
    async def test_get_position_by_id_exists(self):
        """Test getting position by ID."""
        mock_db = AsyncMock()
        position_id = "507f1f77bcf86cd799439012"
        user_id = "507f1f77bcf86cd799439011"
        
        position_data = {
            "_id": ObjectId(position_id),
            "user_id": ObjectId(user_id),
            "symbol": "R_10",
            "contract_type": "CALL",
            "amount": 10.0,
            "duration": 5,
            "status": "open",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        mock_db.trade_positions.find_one.return_value = position_data
        
        result = await get_position_by_id(mock_db, position_id, user_id)
        
        assert result is not None
        assert isinstance(result, TradePositionInDB)
        assert result.id == ObjectId(position_id)
        assert result.user_id == ObjectId(user_id)
        
        mock_db.trade_positions.find_one.assert_called_once_with({
            "_id": ObjectId(position_id),
            "user_id": ObjectId(user_id)
        })
    
    @pytest.mark.asyncio
    async def test_get_position_by_id_not_exists(self):
        """Test getting non-existent position."""
        mock_db = AsyncMock()
        position_id = "507f1f77bcf86cd799439012"
        user_id = "507f1f77bcf86cd799439011"
        
        mock_db.trade_positions.find_one.return_value = None
        
        result = await get_position_by_id(mock_db, position_id, user_id)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_position(self):
        """Test updating a position."""
        mock_db = AsyncMock()
        position_id = "507f1f77bcf86cd799439012"
        user_id = "507f1f77bcf86cd799439011"
        update_data = {
            "status": "closed",
            "exit_spot": 101.5,
            "profit_loss": 5.0
        }
        
        updated_position_data = {
            "_id": ObjectId(position_id),
            "user_id": ObjectId(user_id),
            "symbol": "R_10",
            "contract_type": "CALL",
            "amount": 10.0,
            "duration": 5,
            "status": "closed",
            "exit_spot": 101.5,
            "profit_loss": 5.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        mock_db.trade_positions.find_one_and_update.return_value = updated_position_data
        
        result = await update_position(mock_db, position_id, user_id, update_data)
        
        assert result is not None
        assert isinstance(result, TradePositionInDB)
        assert result.status == "closed"
        assert result.exit_spot == 101.5
        assert result.profit_loss == 5.0
        
        # Verify update was called correctly
        mock_db.trade_positions.find_one_and_update.assert_called_once()
        call_args = mock_db.trade_positions.find_one_and_update.call_args
        
        assert call_args[0][0] == {
            "_id": ObjectId(position_id),
            "user_id": ObjectId(user_id)
        }
        update_data_call = call_args[0][1]["$set"]
        assert update_data_call["status"] == "closed"
        assert update_data_call["exit_spot"] == 101.5
        assert update_data_call["profit_loss"] == 5.0
        assert "updated_at" in update_data_call


class TestMarketAnalysisCRUD:
    """Test market analysis CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_market_analysis(self):
        """Test creating market analysis."""
        mock_db = AsyncMock()
        analysis = MarketAnalysisInDB(
            symbol="R_10",
            current_price=100.0,
            price_history=[98.0, 99.0, 100.0],
            rsi=65.5,
            trend="up",
            confidence=0.8
        )
        
        inserted_id = ObjectId()
        mock_db.market_analysis.insert_one.return_value.inserted_id = inserted_id
        
        result = await create_market_analysis(mock_db, analysis)
        
        assert result is not None
        assert isinstance(result, MarketAnalysisInDB)
        assert result.id == inserted_id
        assert result.symbol == "R_10"
        assert result.current_price == 100.0
        assert result.rsi == 65.5
        
        # Verify database insert was called
        mock_db.market_analysis.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_latest_market_analysis_exists(self):
        """Test getting latest market analysis."""
        mock_db = AsyncMock()
        symbol = "R_10"
        
        analysis_data = {
            "_id": ObjectId(),
            "symbol": "R_10",
            "current_price": 100.0,
            "price_history": [98.0, 99.0, 100.0],
            "rsi": 65.5,
            "trend": "up",
            "confidence": 0.8,
            "timestamp": datetime.utcnow()
        }
        
        mock_db.market_analysis.find_one.return_value = analysis_data
        
        result = await get_latest_market_analysis(mock_db, symbol)
        
        assert result is not None
        assert isinstance(result, MarketAnalysisInDB)
        assert result.symbol == "R_10"
        assert result.current_price == 100.0
        
        mock_db.market_analysis.find_one.assert_called_once_with(
            {"symbol": symbol}, sort=[("timestamp", -1)]
        )
    
    @pytest.mark.asyncio
    async def test_get_latest_market_analysis_not_exists(self):
        """Test getting non-existent market analysis."""
        mock_db = AsyncMock()
        symbol = "R_10"
        
        mock_db.market_analysis.find_one.return_value = None
        
        result = await get_latest_market_analysis(mock_db, symbol)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_market_analysis_history(self):
        """Test getting market analysis history."""
        mock_db = AsyncMock()
        symbol = "R_10"
        
        analysis_data = [
            {
                "_id": ObjectId(),
                "symbol": "R_10",
                "current_price": 100.0,
                "price_history": [98.0, 99.0, 100.0],
                "timestamp": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "symbol": "R_10",
                "current_price": 99.5,
                "price_history": [97.0, 98.0, 99.5],
                "timestamp": datetime.utcnow()
            }
        ]
        
        # Mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.__aiter__.return_value = iter(analysis_data)
        mock_db.market_analysis.find.return_value.sort.return_value.limit.return_value = mock_cursor
        
        result = await get_market_analysis_history(mock_db, symbol, limit=50)
        
        assert len(result) == 2
        assert all(isinstance(analysis, MarketAnalysisInDB) for analysis in result)
        assert result[0].current_price == 100.0
        assert result[1].current_price == 99.5
        
        # Verify query
        mock_db.market_analysis.find.assert_called_once_with({"symbol": symbol})


class TestTradingSignalsCRUD:
    """Test trading signals CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_trading_signal(self):
        """Test creating a trading signal."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        signal = TradingSignalInDB(
            user_id=ObjectId(user_id),  # Will be overridden
            symbol="R_10",
            signal_type="BUY_CALL",
            confidence=0.8,
            recommended_amount=10.0,
            recommended_duration=5,
            reasoning="RSI indicates oversold conditions"
        )
        
        inserted_id = ObjectId()
        mock_db.trading_signals.insert_one.return_value.inserted_id = inserted_id
        
        result = await create_trading_signal(mock_db, user_id, signal)
        
        assert result is not None
        assert isinstance(result, TradingSignalInDB)
        assert result.id == inserted_id
        assert result.user_id == ObjectId(user_id)
        assert result.symbol == "R_10"
        assert result.signal_type == "BUY_CALL"
        assert result.confidence == 0.8
        
        # Verify database insert was called
        mock_db.trading_signals.insert_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_signals_all(self):
        """Test getting all user signals."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        
        signal_data = [
            {
                "_id": ObjectId(),
                "user_id": ObjectId(user_id),
                "symbol": "R_10",
                "signal_type": "BUY_CALL",
                "confidence": 0.8,
                "recommended_amount": 10.0,
                "recommended_duration": 5,
                "reasoning": "Test reasoning",
                "executed": False,
                "created_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "user_id": ObjectId(user_id),
                "symbol": "R_25",
                "signal_type": "BUY_PUT",
                "confidence": 0.9,
                "recommended_amount": 15.0,
                "recommended_duration": 10,
                "reasoning": "Test reasoning 2",
                "executed": True,
                "created_at": datetime.utcnow()
            }
        ]
        
        # Mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.__aiter__.return_value = iter(signal_data)
        mock_db.trading_signals.find.return_value.sort.return_value = mock_cursor
        
        result = await get_user_signals(mock_db, user_id)
        
        assert len(result) == 2
        assert all(isinstance(signal, TradingSignalInDB) for signal in result)
        assert result[0].signal_type == "BUY_CALL"
        assert result[1].signal_type == "BUY_PUT"
        
        # Verify query
        mock_db.trading_signals.find.assert_called_once_with(
            {"user_id": ObjectId(user_id)}
        )
    
    @pytest.mark.asyncio
    async def test_get_user_signals_by_executed(self):
        """Test getting user signals filtered by executed status."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        executed = False
        
        signal_data = [
            {
                "_id": ObjectId(),
                "user_id": ObjectId(user_id),
                "symbol": "R_10",
                "signal_type": "BUY_CALL",
                "confidence": 0.8,
                "recommended_amount": 10.0,
                "recommended_duration": 5,
                "reasoning": "Test reasoning",
                "executed": False,
                "created_at": datetime.utcnow()
            }
        ]
        
        # Mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.__aiter__.return_value = iter(signal_data)
        mock_db.trading_signals.find.return_value.sort.return_value = mock_cursor
        
        result = await get_user_signals(mock_db, user_id, executed)
        
        assert len(result) == 1
        assert result[0].executed is False
        
        # Verify query includes executed filter
        mock_db.trading_signals.find.assert_called_once_with(
            {"user_id": ObjectId(user_id), "executed": False}
        )
    
    @pytest.mark.asyncio
    async def test_update_signal_executed(self):
        """Test updating signal as executed."""
        mock_db = AsyncMock()
        signal_id = "507f1f77bcf86cd799439012"
        trade_id = "507f1f77bcf86cd799439013"
        
        updated_signal_data = {
            "_id": ObjectId(signal_id),
            "user_id": ObjectId(),
            "symbol": "R_10",
            "signal_type": "BUY_CALL",
            "confidence": 0.8,
            "recommended_amount": 10.0,
            "recommended_duration": 5,
            "reasoning": "Test reasoning",
            "executed": True,
            "trade_id": ObjectId(trade_id),
            "created_at": datetime.utcnow()
        }
        
        mock_db.trading_signals.find_one_and_update.return_value = updated_signal_data
        
        result = await update_signal_executed(mock_db, signal_id, trade_id)
        
        assert result is not None
        assert isinstance(result, TradingSignalInDB)
        assert result.executed is True
        assert result.trade_id == ObjectId(trade_id)
        
        # Verify update was called correctly
        mock_db.trading_signals.find_one_and_update.assert_called_once()
        call_args = mock_db.trading_signals.find_one_and_update.call_args
        
        assert call_args[0][0] == {"_id": ObjectId(signal_id)}
        update_data = call_args[0][1]["$set"]
        assert update_data["executed"] is True
        assert update_data["trade_id"] == ObjectId(trade_id)


class TestTradingStatistics:
    """Test trading statistics functions."""
    
    @pytest.mark.asyncio
    async def test_get_user_trading_stats_with_data(self):
        """Test getting trading stats when user has trades."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        
        # Mock aggregation result
        stats_data = {
            "_id": None,
            "total_trades": 10,
            "winning_trades": 6,
            "losing_trades": 4,
            "total_profit": 50.0,
            "avg_profit": 5.0,
            "max_profit": 25.0,
            "max_loss": -15.0
        }
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [stats_data]
        mock_db.trade_positions.aggregate.return_value = mock_cursor
        
        result = await get_user_trading_stats(mock_db, user_id)
        
        assert result is not None
        assert result["total_trades"] == 10
        assert result["winning_trades"] == 6
        assert result["losing_trades"] == 4
        assert result["total_profit"] == 50.0
        assert result["avg_profit"] == 5.0
        assert result["max_profit"] == 25.0
        assert result["max_loss"] == -15.0
        assert result["win_rate"] == 0.6  # 6/10
        
        # Verify aggregation pipeline
        mock_db.trade_positions.aggregate.assert_called_once()
        pipeline = mock_db.trade_positions.aggregate.call_args[0][0]
        
        # Check match stage
        match_stage = pipeline[0]
        assert match_stage["$match"]["user_id"] == ObjectId(user_id)
        
        # Check group stage
        group_stage = pipeline[1]
        assert "$group" in group_stage
        assert group_stage["$group"]["_id"] is None
    
    @pytest.mark.asyncio
    async def test_get_user_trading_stats_no_data(self):
        """Test getting trading stats when user has no trades."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        
        # Mock empty aggregation result
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = []
        mock_db.trade_positions.aggregate.return_value = mock_cursor
        
        result = await get_user_trading_stats(mock_db, user_id)
        
        assert result is not None
        assert result["total_trades"] == 0
        assert result["winning_trades"] == 0
        assert result["losing_trades"] == 0
        assert result["total_profit"] == 0
        assert result["avg_profit"] == 0
        assert result["max_profit"] == 0
        assert result["max_loss"] == 0
        assert result["win_rate"] == 0
    
    @pytest.mark.asyncio
    async def test_get_user_trading_stats_zero_trades_win_rate(self):
        """Test that win rate is 0 when total trades is 0."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        
        # Mock result with zero trades
        stats_data = {
            "_id": None,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_profit": 0,
            "avg_profit": 0,
            "max_profit": 0,
            "max_loss": 0
        }
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [stats_data]
        mock_db.trade_positions.aggregate.return_value = mock_cursor
        
        result = await get_user_trading_stats(mock_db, user_id)
        
        assert result["win_rate"] == 0  # Should handle division by zero


class TestTradingCRUDIntegration:
    """Integration tests for trading CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_and_get_trading_parameters_cycle(self):
        """Test creating and retrieving trading parameters."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        
        # Create parameters
        params_create = TradingParametersCreate(
            profit_top=10.0,
            profit_loss=5.0,
            stop_loss=15.0,
            take_profit=8.0,
            max_daily_loss=100.0,
            position_size=10.0
        )
        
        inserted_id = ObjectId()
        mock_db.trading_parameters.insert_one.return_value.inserted_id = inserted_id
        
        created_params = await create_trading_parameters(mock_db, user_id, params_create)
        
        # Mock retrieval
        params_data = {
            "_id": inserted_id,
            "user_id": ObjectId(user_id),
            "profit_top": 10.0,
            "profit_loss": 5.0,
            "stop_loss": 15.0,
            "take_profit": 8.0,
            "max_daily_loss": 100.0,
            "position_size": 10.0,
            "created_at": created_params.created_at,
            "updated_at": created_params.updated_at
        }
        mock_db.trading_parameters.find_one.return_value = params_data
        
        retrieved_params = await get_user_trading_parameters(mock_db, user_id)
        
        assert retrieved_params is not None
        assert retrieved_params.id == created_params.id
        assert retrieved_params.profit_top == created_params.profit_top
        assert retrieved_params.user_id == created_params.user_id
    
    @pytest.mark.asyncio
    async def test_create_position_and_update_cycle(self):
        """Test creating a position and then updating it."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        
        # Create position
        trade_create = TradePositionCreate(
            symbol="R_10",
            contract_type="CALL",
            amount=10.0,
            duration=5
        )
        
        position_id = ObjectId()
        mock_db.trade_positions.insert_one.return_value.inserted_id = position_id
        
        created_position = await create_trade_position(mock_db, user_id, trade_create)
        
        # Update position
        update_data = {"status": "closed", "profit_loss": 5.0}
        
        updated_position_data = {
            "_id": position_id,
            "user_id": ObjectId(user_id),
            "symbol": "R_10",
            "contract_type": "CALL",
            "amount": 10.0,
            "duration": 5,
            "status": "closed",
            "profit_loss": 5.0,
            "created_at": created_position.created_at,
            "updated_at": datetime.utcnow()
        }
        mock_db.trade_positions.find_one_and_update.return_value = updated_position_data
        
        updated_position = await update_position(
            mock_db, str(position_id), user_id, update_data
        )
        
        assert updated_position is not None
        assert updated_position.id == created_position.id
        assert updated_position.status == "closed"
        assert updated_position.profit_loss == 5.0
