"""
Unit tests for app.models.trading module.
"""

from datetime import datetime

import pytest
from bson import ObjectId
from pydantic import ValidationError

from app.models.trading import (
    MarketAnalysisBase,
    MarketAnalysisInDB,
    TradePosition,
    TradePositionBase,
    TradePositionInDB,
    TradingParametersBase,
    TradingParametersCreate,
    TradingParametersInDB,
    TradingParametersUpdate,
    TradingSignalBase,
    TradingSignalInDB,
)


class TestTradingParametersBase:
    """Test the TradingParametersBase model."""

    def test_valid_trading_parameters(self):
        """Test creating valid trading parameters."""
        params_data = {
            "profit_top": 10.0,
            "profit_loss": 5.0,
            "stop_loss": 15.0,
            "take_profit": 8.0,
            "max_daily_loss": 100.0,
            "position_size": 10.0
        }

        params = TradingParametersBase(**params_data)

        assert params.profit_top == 10.0
        assert params.profit_loss == 5.0
        assert params.stop_loss == 15.0
        assert params.take_profit == 8.0
        assert params.max_daily_loss == 100.0
        assert params.position_size == 10.0

    def test_field_validation_ranges(self):
        """Test field validation for acceptable ranges."""
        # Test minimum values
        params_data = {
            "profit_top": 0.1,
            "profit_loss": 0.1,
            "stop_loss": 0.1,
            "take_profit": 0.1,
            "max_daily_loss": 1.0,
            "position_size": 1.0
        }

        params = TradingParametersBase(**params_data)
        assert params.profit_top == 0.1

        # Test maximum values
        params_data = {
            "profit_top": 100.0,
            "profit_loss": 100.0,
            "stop_loss": 100.0,
            "take_profit": 100.0,
            "max_daily_loss": 10000.0,
            "position_size": 10000.0
        }

        params = TradingParametersBase(**params_data)
        assert params.profit_top == 100.0

    def test_profit_top_validation_errors(self):
        """Test profit_top field validation errors."""
        # Below minimum
        with pytest.raises(ValidationError) as exc_info:
            TradingParametersBase(
                profit_top=0.05,  # Below 0.1
                profit_loss=5.0,
                stop_loss=15.0,
                take_profit=8.0,
                max_daily_loss=100.0,
                position_size=10.0
            )
        assert "Input should be greater than or equal to 0.1" in str(exc_info.value)

        # Above maximum
        with pytest.raises(ValidationError) as exc_info:
            TradingParametersBase(
                profit_top=150.0,  # Above 100.0
                profit_loss=5.0,
                stop_loss=15.0,
                take_profit=8.0,
                max_daily_loss=100.0,
                position_size=10.0
            )
        assert "Input should be less than or equal to 100" in str(exc_info.value)

    def test_position_size_validation_errors(self):
        """Test position_size field validation errors."""
        # Below minimum
        with pytest.raises(ValidationError) as exc_info:
            TradingParametersBase(
                profit_top=10.0,
                profit_loss=5.0,
                stop_loss=15.0,
                take_profit=8.0,
                max_daily_loss=100.0,
                position_size=0.5  # Below 1.0
            )
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

        # Above maximum
        with pytest.raises(ValidationError) as exc_info:
            TradingParametersBase(
                profit_top=10.0,
                profit_loss=5.0,
                stop_loss=15.0,
                take_profit=8.0,
                max_daily_loss=100.0,
                position_size=15000.0  # Above 10000.0
            )
        assert "Input should be less than or equal to 10000" in str(exc_info.value)

    def test_missing_required_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError) as exc_info:
            TradingParametersBase(
                profit_top=10.0,
                profit_loss=5.0
                # Missing other fields
            )

        error_msg = str(exc_info.value)
        assert "stop_loss" in error_msg
        assert "Field required" in error_msg


class TestTradingParametersCreate:
    """Test the TradingParametersCreate model."""

    def test_inherits_from_base(self):
        """Test that TradingParametersCreate inherits from base."""
        params_data = {
            "profit_top": 10.0,
            "profit_loss": 5.0,
            "stop_loss": 15.0,
            "take_profit": 8.0,
            "max_daily_loss": 100.0,
            "position_size": 10.0
        }

        params = TradingParametersCreate(**params_data)

        # Should have all base fields
        assert hasattr(params, 'profit_top')
        assert hasattr(params, 'profit_loss')
        assert hasattr(params, 'stop_loss')
        assert hasattr(params, 'take_profit')
        assert hasattr(params, 'max_daily_loss')
        assert hasattr(params, 'position_size')


class TestTradingParametersUpdate:
    """Test the TradingParametersUpdate model."""

    def test_all_fields_optional(self):
        """Test that all fields are optional in update model."""
        params = TradingParametersUpdate()

        assert params.profit_top is None
        assert params.profit_loss is None
        assert params.stop_loss is None
        assert params.take_profit is None
        assert params.max_daily_loss is None
        assert params.position_size is None

    def test_partial_update(self):
        """Test partial update with some fields."""
        params_data = {
            "profit_top": 15.0,
            "position_size": 20.0
        }

        params = TradingParametersUpdate(**params_data)

        assert params.profit_top == 15.0
        assert params.position_size == 20.0
        assert params.profit_loss is None
        assert params.stop_loss is None

    def test_validation_on_provided_fields(self):
        """Test that validation still applies to provided fields."""
        with pytest.raises(ValidationError) as exc_info:
            TradingParametersUpdate(profit_top=150.0)  # Above maximum

        assert "Input should be less than or equal to 100" in str(exc_info.value)


class TestTradingParametersInDB:
    """Test the TradingParametersInDB model."""

    def test_valid_in_db_model(self):
        """Test creating valid TradingParametersInDB."""
        object_id = ObjectId()
        user_id = ObjectId()

        params_data = {
            "_id": object_id,
            "user_id": user_id,
            "profit_top": 10.0,
            "profit_loss": 5.0,
            "stop_loss": 15.0,
            "take_profit": 8.0,
            "max_daily_loss": 100.0,
            "position_size": 10.0
        }

        params = TradingParametersInDB(**params_data)

        assert params.id == object_id
        assert params.user_id == user_id
        assert isinstance(params.created_at, datetime)
        assert isinstance(params.updated_at, datetime)

    def test_default_timestamps(self):
        """Test that timestamps are set by default."""
        params_data = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            "profit_top": 10.0,
            "profit_loss": 5.0,
            "stop_loss": 15.0,
            "take_profit": 8.0,
            "max_daily_loss": 100.0,
            "position_size": 10.0
        }

        params = TradingParametersInDB(**params_data)

        assert params.created_at is not None
        assert params.updated_at is not None


class TestTradePositionBase:
    """Test the TradePositionBase model."""

    def test_valid_trade_position(self):
        """Test creating valid trade position."""
        position_data = {
            "symbol": "R_10",
            "contract_type": "CALL",
            "amount": 10.0,
            "duration": 5,
            "duration_unit": "m"
        }

        position = TradePositionBase(**position_data)

        assert position.symbol == "R_10"
        assert position.contract_type == "CALL"
        assert position.amount == 10.0
        assert position.duration == 5
        assert position.duration_unit == "m"

    def test_default_duration_unit(self):
        """Test default duration unit."""
        position_data = {
            "symbol": "R_10",
            "contract_type": "CALL",
            "amount": 10.0,
            "duration": 5
        }

        position = TradePositionBase(**position_data)
        assert position.duration_unit == "m"  # Default value

    def test_amount_validation(self):
        """Test amount field validation."""
        # Below minimum
        with pytest.raises(ValidationError) as exc_info:
            TradePositionBase(
                symbol="R_10",
                contract_type="CALL",
                amount=0.5,  # Below 1.0
                duration=5
            )
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

    def test_duration_validation(self):
        """Test duration field validation."""
        # Below minimum
        with pytest.raises(ValidationError) as exc_info:
            TradePositionBase(
                symbol="R_10",
                contract_type="CALL",
                amount=10.0,
                duration=0  # Below 1
            )
        assert "Input should be greater than or equal to 1" in str(exc_info.value)


class TestTradePositionInDB:
    """Test the TradePositionInDB model."""

    def test_valid_position_in_db(self):
        """Test creating valid TradePositionInDB."""
        object_id = ObjectId()
        user_id = ObjectId()

        position_data = {
            "_id": object_id,
            "user_id": user_id,
            "symbol": "R_10",
            "contract_type": "CALL",
            "amount": 10.0,
            "duration": 5,
            "contract_id": "12345",
            "entry_spot": 100.5,
            "current_spot": 101.0,
            "profit_loss": 0.5,
            "status": "open"
        }

        position = TradePositionInDB(**position_data)

        assert position.id == object_id
        assert position.user_id == user_id
        assert position.contract_id == "12345"
        assert position.entry_spot == 100.5
        assert position.current_spot == 101.0
        assert position.profit_loss == 0.5
        assert position.status == "open"

    def test_default_status(self):
        """Test default status value."""
        position_data = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            "symbol": "R_10",
            "contract_type": "CALL",
            "amount": 10.0,
            "duration": 5
        }

        position = TradePositionInDB(**position_data)
        assert position.status == "pending"  # Default value

    def test_optional_fields(self):
        """Test that optional fields can be None."""
        position_data = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            "symbol": "R_10",
            "contract_type": "CALL",
            "amount": 10.0,
            "duration": 5
        }

        position = TradePositionInDB(**position_data)

        assert position.contract_id is None
        assert position.entry_spot is None
        assert position.exit_spot is None
        assert position.current_spot is None
        assert position.profit_loss is None
        assert position.entry_time is None
        assert position.exit_time is None


class TestMarketAnalysisBase:
    """Test the MarketAnalysisBase model."""

    def test_valid_market_analysis(self):
        """Test creating valid market analysis."""
        analysis_data = {
            "symbol": "R_10",
            "rsi": 65.5,
            "macd": 0.25,
            "bollinger_upper": 105.0,
            "bollinger_lower": 95.0,
            "trend": "up",
            "volatility": 0.15,
            "confidence": 0.8
        }

        analysis = MarketAnalysisBase(**analysis_data)

        assert analysis.symbol == "R_10"
        assert analysis.rsi == 65.5
        assert analysis.macd == 0.25
        assert analysis.bollinger_upper == 105.0
        assert analysis.bollinger_lower == 95.0
        assert analysis.trend == "up"
        assert analysis.volatility == 0.15
        assert analysis.confidence == 0.8

    def test_optional_fields(self):
        """Test that most fields are optional."""
        analysis_data = {
            "symbol": "R_10"
        }

        analysis = MarketAnalysisBase(**analysis_data)

        assert analysis.symbol == "R_10"
        assert analysis.rsi is None
        assert analysis.macd is None
        assert analysis.bollinger_upper is None
        assert analysis.bollinger_lower is None
        assert analysis.trend is None
        assert analysis.volatility is None
        assert analysis.confidence is None

    def test_confidence_validation(self):
        """Test confidence field validation."""
        # Below minimum
        with pytest.raises(ValidationError) as exc_info:
            MarketAnalysisBase(
                symbol="R_10",
                confidence=-0.1  # Below 0.0
            )
        assert "Input should be greater than or equal to 0" in str(exc_info.value)

        # Above maximum
        with pytest.raises(ValidationError) as exc_info:
            MarketAnalysisBase(
                symbol="R_10",
                confidence=1.5  # Above 1.0
            )
        assert "Input should be less than or equal to 1" in str(exc_info.value)


class TestMarketAnalysisInDB:
    """Test the MarketAnalysisInDB model."""

    def test_valid_analysis_in_db(self):
        """Test creating valid MarketAnalysisInDB."""
        object_id = ObjectId()

        analysis_data = {
            "_id": object_id,
            "symbol": "R_10",
            "current_price": 100.0,
            "price_history": [98.0, 99.0, 100.0, 101.0],
            "rsi": 65.5
        }

        analysis = MarketAnalysisInDB(**analysis_data)

        assert analysis.id == object_id
        assert analysis.current_price == 100.0
        assert analysis.price_history == [98.0, 99.0, 100.0, 101.0]
        assert isinstance(analysis.timestamp, datetime)

    def test_default_timestamp(self):
        """Test that timestamp is set by default."""
        analysis_data = {
            "_id": ObjectId(),
            "symbol": "R_10",
            "current_price": 100.0
        }

        analysis = MarketAnalysisInDB(**analysis_data)
        assert analysis.timestamp is not None
        assert isinstance(analysis.timestamp, datetime)

    def test_default_price_history(self):
        """Test that price_history defaults to empty list."""
        analysis_data = {
            "_id": ObjectId(),
            "symbol": "R_10",
            "current_price": 100.0
        }

        analysis = MarketAnalysisInDB(**analysis_data)
        assert analysis.price_history == []


class TestTradingSignalBase:
    """Test the TradingSignalBase model."""

    def test_valid_trading_signal(self):
        """Test creating valid trading signal."""
        signal_data = {
            "symbol": "R_10",
            "signal_type": "BUY_CALL",
            "confidence": 0.8,
            "recommended_amount": 10.0,
            "recommended_duration": 5,
            "reasoning": "RSI indicates oversold conditions"
        }

        signal = TradingSignalBase(**signal_data)

        assert signal.symbol == "R_10"
        assert signal.signal_type == "BUY_CALL"
        assert signal.confidence == 0.8
        assert signal.recommended_amount == 10.0
        assert signal.recommended_duration == 5
        assert signal.reasoning == "RSI indicates oversold conditions"

    def test_confidence_validation(self):
        """Test confidence field validation."""
        # Valid range
        signal_data = {
            "symbol": "R_10",
            "signal_type": "BUY_CALL",
            "confidence": 0.5,
            "recommended_amount": 10.0,
            "recommended_duration": 5,
            "reasoning": "Test"
        }

        signal = TradingSignalBase(**signal_data)
        assert signal.confidence == 0.5

        # Invalid range
        with pytest.raises(ValidationError):
            TradingSignalBase(
                symbol="R_10",
                signal_type="BUY_CALL",
                confidence=1.5,  # Above 1.0
                recommended_amount=10.0,
                recommended_duration=5,
                reasoning="Test"
            )

    def test_recommended_amount_validation(self):
        """Test recommended_amount field validation."""
        with pytest.raises(ValidationError) as exc_info:
            TradingSignalBase(
                symbol="R_10",
                signal_type="BUY_CALL",
                confidence=0.8,
                recommended_amount=0.5,  # Below 1.0
                recommended_duration=5,
                reasoning="Test"
            )
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

    def test_recommended_duration_validation(self):
        """Test recommended_duration field validation."""
        with pytest.raises(ValidationError) as exc_info:
            TradingSignalBase(
                symbol="R_10",
                signal_type="BUY_CALL",
                confidence=0.8,
                recommended_amount=10.0,
                recommended_duration=0,  # Below 1
                reasoning="Test"
            )
        assert "Input should be greater than or equal to 1" in str(exc_info.value)


class TestTradingSignalInDB:
    """Test the TradingSignalInDB model."""

    def test_valid_signal_in_db(self):
        """Test creating valid TradingSignalInDB."""
        object_id = ObjectId()
        user_id = ObjectId()
        trade_id = ObjectId()

        signal_data = {
            "_id": object_id,
            "user_id": user_id,
            "symbol": "R_10",
            "signal_type": "BUY_CALL",
            "confidence": 0.8,
            "recommended_amount": 10.0,
            "recommended_duration": 5,
            "reasoning": "RSI indicates oversold conditions",
            "executed": True,
            "trade_id": trade_id
        }

        signal = TradingSignalInDB(**signal_data)

        assert signal.id == object_id
        assert signal.user_id == user_id
        assert signal.executed is True
        assert signal.trade_id == trade_id
        assert isinstance(signal.created_at, datetime)

    def test_default_values(self):
        """Test default values for optional fields."""
        signal_data = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            "symbol": "R_10",
            "signal_type": "BUY_CALL",
            "confidence": 0.8,
            "recommended_amount": 10.0,
            "recommended_duration": 5,
            "reasoning": "Test reasoning"
        }

        signal = TradingSignalInDB(**signal_data)

        assert signal.executed is False  # Default value
        assert signal.trade_id is None  # Default value
        assert isinstance(signal.created_at, datetime)


class TestTradingModelInteroperability:
    """Test interoperability between trading models."""

    def test_parameters_create_to_in_db(self):
        """Test converting TradingParametersCreate to InDB."""
        create_data = {
            "profit_top": 10.0,
            "profit_loss": 5.0,
            "stop_loss": 15.0,
            "take_profit": 8.0,
            "max_daily_loss": 100.0,
            "position_size": 10.0
        }

        params_create = TradingParametersCreate(**create_data)

        # Convert to InDB model
        in_db_data = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            **params_create.model_dump()
        }

        params_in_db = TradingParametersInDB(**in_db_data)

        assert params_in_db.profit_top == params_create.profit_top
        assert params_in_db.profit_loss == params_create.profit_loss
        assert params_in_db.stop_loss == params_create.stop_loss

    def test_position_in_db_to_public(self):
        """Test converting TradePositionInDB to public model."""
        object_id = ObjectId()
        user_id = ObjectId()

        in_db_data = {
            "_id": object_id,
            "user_id": user_id,
            "symbol": "R_10",
            "contract_type": "CALL",
            "amount": 10.0,
            "duration": 5,
            "status": "open",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime(2023, 1, 1, 12, 0, 0)
        }

        position_in_db = TradePositionInDB(**in_db_data)

        # Convert to public model
        public_data = {
            "id": str(position_in_db.id),
            "user_id": str(position_in_db.user_id),
            "symbol": position_in_db.symbol,
            "contract_type": position_in_db.contract_type,
            "amount": position_in_db.amount,
            "duration": position_in_db.duration,
            "duration_unit": position_in_db.duration_unit,
            "contract_id": position_in_db.contract_id,
            "entry_spot": position_in_db.entry_spot,
            "exit_spot": position_in_db.exit_spot,
            "current_spot": position_in_db.current_spot,
            "profit_loss": position_in_db.profit_loss,
            "status": position_in_db.status,
            "entry_time": position_in_db.entry_time,
            "exit_time": position_in_db.exit_time,
            "created_at": position_in_db.created_at,
            "updated_at": position_in_db.updated_at
        }

        position = TradePosition(**public_data)

        assert position.id == str(object_id)
        assert position.user_id == str(user_id)
        assert position.symbol == "R_10"
        assert position.status == "open"
