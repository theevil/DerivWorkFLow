"""
Unit tests for app.core.ai_analysis module.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.core.ai_analysis import (
    TechnicalIndicators,
    MarketAnalyzer,
    TradingSignalGenerator
)
from app.models.trading import MarketAnalysisInDB, TradingSignalInDB


class TestTechnicalIndicators:
    """Test the TechnicalIndicators class."""
    
    def test_rsi_calculation(self):
        """Test RSI calculation with known values."""
        # Simple price data for testing
        prices = [10, 12, 11, 13, 15, 14, 16, 18, 17, 19, 20, 18, 21, 19, 22]
        
        rsi = TechnicalIndicators.rsi(prices, period=14)
        
        assert rsi is not None
        assert 0 <= rsi <= 100
        assert isinstance(rsi, float)
    
    def test_rsi_insufficient_data(self):
        """Test RSI with insufficient data."""
        prices = [10, 12, 11]  # Less than period + 1
        
        rsi = TechnicalIndicators.rsi(prices, period=14)
        
        assert rsi is None
    
    def test_rsi_all_gains(self):
        """Test RSI when all price movements are gains."""
        prices = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
        
        rsi = TechnicalIndicators.rsi(prices, period=14)
        
        assert rsi == 100.0
    
    def test_macd_calculation(self):
        """Test MACD calculation."""
        prices = list(range(100, 130))  # Trending prices
        
        macd_data = TechnicalIndicators.macd(prices)
        
        assert macd_data is not None
        assert "macd" in macd_data
        assert "signal" in macd_data
        assert "histogram" in macd_data
        assert all(isinstance(v, float) for v in macd_data.values())
    
    def test_macd_insufficient_data(self):
        """Test MACD with insufficient data."""
        prices = [10, 12, 11]  # Less than slow period
        
        macd_data = TechnicalIndicators.macd(prices)
        
        assert macd_data is None
    
    def test_bollinger_bands_calculation(self):
        """Test Bollinger Bands calculation."""
        prices = [100 + i + np.sin(i/5) * 5 for i in range(25)]  # Oscillating prices
        
        bollinger = TechnicalIndicators.bollinger_bands(prices)
        
        assert bollinger is not None
        assert "upper" in bollinger
        assert "middle" in bollinger
        assert "lower" in bollinger
        assert bollinger["upper"] > bollinger["middle"] > bollinger["lower"]
    
    def test_bollinger_bands_insufficient_data(self):
        """Test Bollinger Bands with insufficient data."""
        prices = [10, 12, 11]  # Less than period
        
        bollinger = TechnicalIndicators.bollinger_bands(prices)
        
        assert bollinger is None
    
    def test_ema_calculation(self):
        """Test EMA calculation."""
        prices = np.array([10, 12, 11, 13, 15, 14, 16, 18])
        
        ema = TechnicalIndicators._ema(prices, period=5)
        
        assert len(ema) == len(prices)
        assert ema[0] == prices[0]  # First value should be the same
        assert all(isinstance(x, (int, float, np.number)) for x in ema)
    
    def test_volatility_calculation(self):
        """Test volatility calculation."""
        prices = [100 + np.random.normal(0, 2) for _ in range(25)]
        
        volatility = TechnicalIndicators.calculate_volatility(prices)
        
        assert volatility is not None
        assert volatility >= 0
        assert isinstance(volatility, float)
    
    def test_volatility_insufficient_data(self):
        """Test volatility with insufficient data."""
        prices = [10, 12, 11]  # Less than period
        
        volatility = TechnicalIndicators.calculate_volatility(prices)
        
        assert volatility is None


class TestMarketAnalyzer:
    """Test the MarketAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = MarketAnalyzer()
        self.sample_prices = [100 + i + np.sin(i/10) * 5 for i in range(50)]
    
    def test_analyzer_initialization(self):
        """Test MarketAnalyzer initialization."""
        assert self.analyzer.indicators is not None
        assert isinstance(self.analyzer.indicators, TechnicalIndicators)
    
    def test_analyze_market(self):
        """Test market analysis."""
        symbol = "R_10"
        current_price = self.sample_prices[-1]
        
        analysis = self.analyzer.analyze_market(symbol, self.sample_prices, current_price)
        
        assert isinstance(analysis, MarketAnalysisInDB)
        assert analysis.symbol == symbol
        assert analysis.current_price == current_price
        assert len(analysis.price_history) <= 100
        assert analysis.trend in ["up", "down", "sideways"]
        assert 0 <= analysis.confidence <= 1
    
    def test_determine_trend_upward(self):
        """Test trend determination for upward trend."""
        upward_prices = list(range(100, 120))  # Clear upward trend
        
        trend = self.analyzer._determine_trend(upward_prices)
        
        assert trend == "up"
    
    def test_determine_trend_downward(self):
        """Test trend determination for downward trend."""
        downward_prices = list(range(120, 100, -1))  # Clear downward trend
        
        trend = self.analyzer._determine_trend(downward_prices)
        
        assert trend == "down"
    
    def test_determine_trend_sideways(self):
        """Test trend determination for sideways trend."""
        sideways_prices = [100] * 15  # Flat prices
        
        trend = self.analyzer._determine_trend(sideways_prices)
        
        assert trend == "sideways"
    
    def test_determine_trend_insufficient_data(self):
        """Test trend determination with insufficient data."""
        prices = [100, 101, 102]  # Less than 10 prices
        
        trend = self.analyzer._determine_trend(prices)
        
        assert trend == "sideways"
    
    def test_calculate_confidence(self):
        """Test confidence calculation."""
        analysis = MarketAnalysisInDB(
            symbol="R_10",
            current_price=100.0,
            price_history=[],
            rsi=75.0,  # Overbought
            bollinger_upper=105.0,
            bollinger_lower=95.0,
            volatility=0.2
        )
        
        confidence = self.analyzer._calculate_confidence(analysis)
        
        assert 0 <= confidence <= 1
        assert isinstance(confidence, float)
    
    def test_calculate_confidence_no_indicators(self):
        """Test confidence calculation with no indicators."""
        analysis = MarketAnalysisInDB(
            symbol="R_10",
            current_price=100.0,
            price_history=[]
        )
        
        confidence = self.analyzer._calculate_confidence(analysis)
        
        assert confidence == 0.5  # Default confidence


class TestTradingSignalGenerator:
    """Test the TradingSignalGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = TradingSignalGenerator()
        self.sample_analysis = MarketAnalysisInDB(
            symbol="R_10",
            current_price=100.0,
            price_history=[],
            rsi=75.0,  # Overbought
            macd=-0.5,
            bollinger_upper=105.0,
            bollinger_lower=95.0,
            trend="down",
            volatility=0.2,
            confidence=0.8
        )
        self.trading_params = {
            "position_size": 10.0,
            "max_daily_loss": 100.0
        }
    
    def test_generator_initialization(self):
        """Test TradingSignalGenerator initialization."""
        assert self.generator.analyzer is not None
        assert isinstance(self.generator.analyzer, MarketAnalyzer)
    
    def test_generate_signal_high_confidence(self):
        """Test signal generation with high confidence."""
        user_id = "test_user"
        
        signal = self.generator.generate_signal(
            user_id, "R_10", self.sample_analysis, self.trading_params
        )
        
        assert signal is not None
        assert isinstance(signal, TradingSignalInDB)
        assert signal.user_id == user_id
        assert signal.symbol == "R_10"
        assert signal.signal_type in ["BUY_CALL", "BUY_PUT"]
        assert signal.confidence >= 0.6
        assert signal.recommended_amount > 0
        assert signal.recommended_duration > 0
        assert len(signal.reasoning) > 0
    
    def test_generate_signal_low_confidence(self):
        """Test signal generation with low confidence."""
        low_confidence_analysis = MarketAnalysisInDB(
            symbol="R_10",
            current_price=100.0,
            price_history=[],
            confidence=0.4  # Below threshold
        )
        
        signal = self.generator.generate_signal(
            "test_user", "R_10", low_confidence_analysis, self.trading_params
        )
        
        assert signal is None
    
    def test_determine_signal_type_buy_call(self):
        """Test signal type determination for BUY_CALL."""
        analysis = MarketAnalysisInDB(
            symbol="R_10",
            current_price=95.0,  # Below lower Bollinger band
            price_history=[],
            rsi=25.0,  # Oversold
            macd=0.5,  # Positive
            bollinger_upper=105.0,
            bollinger_lower=97.0,
            trend="up"
        )
        
        signal_type = self.generator._determine_signal_type(analysis)
        
        assert signal_type == "BUY_CALL"
    
    def test_determine_signal_type_buy_put(self):
        """Test signal type determination for BUY_PUT."""
        analysis = MarketAnalysisInDB(
            symbol="R_10",
            current_price=106.0,  # Above upper Bollinger band
            price_history=[],
            rsi=80.0,  # Overbought
            macd=-0.5,  # Negative
            bollinger_upper=105.0,
            bollinger_lower=95.0,
            trend="down"
        )
        
        signal_type = self.generator._determine_signal_type(analysis)
        
        assert signal_type == "BUY_PUT"
    
    def test_determine_signal_type_hold(self):
        """Test signal type determination for HOLD."""
        analysis = MarketAnalysisInDB(
            symbol="R_10",
            current_price=100.0,
            price_history=[],
            # No clear signals
        )
        
        signal_type = self.generator._determine_signal_type(analysis)
        
        assert signal_type == "HOLD"
    
    def test_calculate_position_size(self):
        """Test position size calculation."""
        confidence = 0.8
        
        position_size = self.generator._calculate_position_size(self.trading_params, confidence)
        
        expected_size = 10.0 * 0.8
        assert position_size == expected_size
    
    def test_calculate_duration_high_volatility(self):
        """Test duration calculation with high volatility."""
        analysis = MarketAnalysisInDB(
            symbol="R_10",
            current_price=100.0,
            price_history=[],
            volatility=0.5  # High volatility
        )
        
        duration = self.generator._calculate_duration(analysis, self.trading_params)
        
        assert duration == 2  # Half of base duration (5 // 2)
    
    def test_calculate_duration_low_volatility(self):
        """Test duration calculation with low volatility."""
        analysis = MarketAnalysisInDB(
            symbol="R_10",
            current_price=100.0,
            price_history=[],
            volatility=0.05  # Low volatility
        )
        
        duration = self.generator._calculate_duration(analysis, self.trading_params)
        
        assert duration == 10  # Double base duration (5 * 2)
    
    def test_calculate_duration_normal_volatility(self):
        """Test duration calculation with normal volatility."""
        analysis = MarketAnalysisInDB(
            symbol="R_10",
            current_price=100.0,
            price_history=[],
            volatility=0.2  # Normal volatility
        )
        
        duration = self.generator._calculate_duration(analysis, self.trading_params)
        
        assert duration == 5  # Base duration
    
    def test_generate_reasoning(self):
        """Test reasoning generation."""
        signal_type = "BUY_PUT"
        
        reasoning = self.generator._generate_reasoning(self.sample_analysis, signal_type)
        
        assert "BUY_PUT" in reasoning
        assert "RSI" in reasoning or "MACD" in reasoning or "trend" in reasoning
        assert len(reasoning) > 20  # Should be descriptive
