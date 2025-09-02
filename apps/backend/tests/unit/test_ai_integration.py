"""
Unit tests for AI integration functionality
"""

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.ai.decision_engine import TradingDecision, TradingDecisionEngine
from app.ai.learning_system import HistoricalLearningSystem
from app.ai.market_analyzer import AdvancedMarketAnalyzer, MarketAnalysisResult
from app.ai.risk_manager import AIRiskManager, RiskAssessment, RiskLevel
from app.core.ai_analysis import EnhancedTradingSignalGenerator


class TestAdvancedMarketAnalyzer:
    """Test cases for AdvancedMarketAnalyzer"""

    @pytest.fixture
    def analyzer(self):
        return AdvancedMarketAnalyzer()

    @pytest.fixture
    def sample_price_history(self):
        # Generate sample price data with slight upward trend
        np.random.seed(42)
        base_price = 1.0
        prices = []
        for i in range(50):
            base_price += np.random.normal(0, 0.001) + 0.0001  # Small upward trend
            prices.append(base_price)
        return prices

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer is not None
        assert analyzer.technical_indicators is not None
        # Note: analyzer.llm might be None if no API key configured

    @pytest.mark.asyncio
    async def test_analyze_market_without_llm(self, analyzer, sample_price_history):
        """Test market analysis fallback when LLM is not available"""
        # Force LLM to None to test fallback
        analyzer.llm = None

        result = await analyzer.analyze_market_advanced(
            symbol="R_10",
            price_history=sample_price_history,
            current_price=sample_price_history[-1]
        )

        assert isinstance(result, MarketAnalysisResult)
        assert result.trend_direction in ["bullish", "bearish", "sideways", "strong_bullish", "strong_bearish"]
        assert 0 <= result.confidence_score <= 1
        assert result.risk_level in ["low", "medium", "high"]
        assert len(result.key_insights) > 0
        assert result.recommended_action in ["buy_call", "buy_put", "hold"]

    @pytest.mark.asyncio
    async def test_analyze_market_with_mock_llm(self, analyzer, sample_price_history):
        """Test market analysis with mocked LLM"""
        # Mock the LLM
        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = """
        {
            "trend_direction": "bullish",
            "confidence_score": 0.75,
            "risk_level": "medium",
            "key_insights": ["Upward trend detected", "RSI in normal range"],
            "recommended_action": "buy_call",
            "reasoning": "Technical indicators suggest bullish momentum",
            "technical_summary": "RSI: 65, MACD positive, trend: bullish"
        }
        """
        mock_llm.ainvoke.return_value = mock_response
        analyzer.llm = mock_llm

        result = await analyzer.analyze_market_advanced(
            symbol="R_10",
            price_history=sample_price_history,
            current_price=sample_price_history[-1]
        )

        assert result.trend_direction == "bullish"
        assert result.confidence_score == 0.75
        assert result.recommended_action == "buy_call"
        assert mock_llm.ainvoke.called


class TestTradingDecisionEngine:
    """Test cases for TradingDecisionEngine"""

    @pytest.fixture
    def decision_engine(self):
        return TradingDecisionEngine()

    @pytest.fixture
    def sample_user_context(self):
        return {
            "account_balance": 1000,
            "risk_tolerance": "medium",
            "experience_level": "intermediate",
            "max_daily_loss": 100,
            "max_position_size": 50
        }

    @pytest.fixture
    def sample_price_history(self):
        return [1.0 + i * 0.001 for i in range(30)]  # Simple upward trend

    def test_decision_engine_initialization(self, decision_engine):
        """Test decision engine initializes correctly"""
        assert decision_engine is not None
        assert decision_engine.market_analyzer is not None
        assert decision_engine.workflow is not None

    @pytest.mark.asyncio
    async def test_make_trading_decision(self, decision_engine, sample_price_history, sample_user_context):
        """Test trading decision generation"""
        decision = await decision_engine.make_trading_decision(
            symbol="R_10",
            price_history=sample_price_history,
            current_price=sample_price_history[-1],
            user_context=sample_user_context
        )

        assert isinstance(decision, TradingDecision)
        assert decision.action in ["BUY_CALL", "BUY_PUT", "HOLD"]
        assert 0 <= decision.confidence <= 1
        assert decision.position_size >= 0
        assert decision.duration > 0
        assert decision.risk_level in ["low", "medium", "high", "critical"]
        assert len(decision.validation_checks) > 0


class TestHistoricalLearningSystem:
    """Test cases for HistoricalLearningSystem"""

    @pytest.fixture
    def learning_system(self):
        return HistoricalLearningSystem()

    def test_learning_system_initialization(self, learning_system):
        """Test learning system initializes correctly"""
        assert learning_system is not None
        assert len(learning_system.model_configs) > 0
        assert "trend_classifier" in learning_system.model_configs
        assert "signal_classifier" in learning_system.model_configs
        assert "risk_classifier" in learning_system.model_configs

    def test_determine_trend_target(self, learning_system):
        """Test trend target determination"""
        assert learning_system._determine_trend_target("bullish") == 2
        assert learning_system._determine_trend_target("bearish") == 0
        assert learning_system._determine_trend_target("sideways") == 1
        assert learning_system._determine_trend_target("strong_bullish") == 3
        assert learning_system._determine_trend_target("unknown") == 1  # Default

    def test_determine_signal_target(self, learning_system):
        """Test signal target determination"""
        # Mock trade objects
        profitable_call_trade = MagicMock()
        profitable_call_trade.contract_type = "CALL"
        profitable_call_trade.profit_loss = 50

        losing_put_trade = MagicMock()
        losing_put_trade.contract_type = "PUT"
        losing_put_trade.profit_loss = -20

        # Test with profitable CALL trade
        result = learning_system._determine_signal_target([profitable_call_trade])
        assert result == 1  # buy_call

        # Test with no trades
        result = learning_system._determine_signal_target([])
        assert result == 2  # hold

    @pytest.mark.asyncio
    async def test_predict_without_models(self, learning_system):
        """Test prediction fallback when no models are loaded"""
        features = {
            "hour": 10,
            "day_of_week": 1,
            "rsi": 50,
            "volatility": 0.2,
            "current_price": 1.0
        }

        trend, confidence = await learning_system.predict_trend(features)
        assert trend == "sideways"  # Default fallback
        assert confidence == 0.5    # Default fallback

        signal, confidence = await learning_system.predict_signal(features)
        assert signal == "HOLD"     # Default fallback
        assert confidence == 0.5    # Default fallback


class TestAIRiskManager:
    """Test cases for AIRiskManager"""

    @pytest.fixture
    def risk_manager(self):
        return AIRiskManager()

    @pytest.fixture
    def sample_market_data(self):
        return {
            "current_price": 1.0,
            "volatility": 0.2,
            "trend": "bullish",
            "session": "active"
        }

    @pytest.fixture
    def sample_user_context(self):
        return {
            "risk_tolerance": "medium",
            "experience_level": "intermediate",
            "account_balance": 1000
        }

    @pytest.fixture
    def sample_portfolio_context(self):
        return {
            "position_count": 2,
            "total_exposure": 100,
            "daily_pnl": -20
        }

    def test_risk_manager_initialization(self, risk_manager):
        """Test risk manager initializes correctly"""
        assert risk_manager is not None
        assert len(risk_manager.risk_thresholds) > 0
        assert "max_position_risk" in risk_manager.risk_thresholds

    @pytest.mark.asyncio
    async def test_assess_position_risk_basic(
        self,
        risk_manager,
        sample_market_data,
        sample_user_context,
        sample_portfolio_context
    ):
        """Test basic position risk assessment"""
        # Force LLM to None to test basic analysis
        risk_manager.llm = None

        risk_assessment = await risk_manager.assess_position_risk(
            symbol="R_10",
            position_size=50,
            account_balance=1000,
            market_data=sample_market_data,
            user_context=sample_user_context,
            portfolio_context=sample_portfolio_context
        )

        assert isinstance(risk_assessment, RiskAssessment)
        assert isinstance(risk_assessment.risk_level, RiskLevel)
        assert 0 <= risk_assessment.risk_score <= 1
        assert 0 <= risk_assessment.position_size_adjustment <= 2
        assert 0.5 <= risk_assessment.stop_loss_adjustment <= 2
        assert 0 <= risk_assessment.confidence <= 1
        assert len(risk_assessment.risk_factors) >= 0

    def test_should_halt_trading_scenarios(self, risk_manager):
        """Test trading halt decision logic"""
        # Mock portfolio risk
        high_risk_portfolio = MagicMock()
        high_risk_portfolio.overall_risk_score = 0.95
        high_risk_portfolio.max_daily_loss_risk = 0.9
        high_risk_portfolio.concentration_risk = 0.85
        high_risk_portfolio.volatility_risk = 0.8
        high_risk_portfolio.drawdown_risk = 0.75

        # Test daily loss limit exceeded
        should_halt, reason = risk_manager.should_halt_trading(high_risk_portfolio, -100, 100)
        assert should_halt is True
        assert "Daily loss limit exceeded" in reason

        # Test multiple high risk factors
        should_halt, reason = risk_manager.should_halt_trading(high_risk_portfolio, -50, 100)
        assert should_halt is True

        # Test acceptable risk
        low_risk_portfolio = MagicMock()
        low_risk_portfolio.overall_risk_score = 0.3
        low_risk_portfolio.max_daily_loss_risk = 0.2
        low_risk_portfolio.concentration_risk = 0.3
        low_risk_portfolio.volatility_risk = 0.2
        low_risk_portfolio.drawdown_risk = 0.1

        should_halt, reason = risk_manager.should_halt_trading(low_risk_portfolio, -10, 100)
        assert should_halt is False

    @pytest.mark.asyncio
    async def test_adaptive_stop_loss(self, risk_manager):
        """Test adaptive stop loss calculation"""
        from datetime import timedelta

        stop_loss = await risk_manager.get_adaptive_stop_loss(
            symbol="R_10",
            entry_price=1.0,
            current_price=1.01,  # Profitable position
            volatility=0.2,
            time_in_trade=timedelta(hours=2),
            user_risk_tolerance="medium"
        )

        assert stop_loss > 0
        assert stop_loss < 1.0  # Should be below entry price for a call

    def test_get_risk_limits(self, risk_manager):
        """Test risk limits calculation"""
        # Test beginner limits
        beginner_context = {"experience_level": "beginner", "risk_tolerance": "low"}
        limits = risk_manager.get_risk_limits(beginner_context)

        assert "max_position_pct" in limits
        assert limits["max_position_pct"] < 5.0  # Should be more conservative

        # Test expert limits
        expert_context = {"experience_level": "expert", "risk_tolerance": "high"}
        limits = risk_manager.get_risk_limits(expert_context)

        assert limits["max_position_pct"] > 5.0  # Should be more flexible


class TestEnhancedTradingSignalGenerator:
    """Test cases for EnhancedTradingSignalGenerator"""

    @pytest.fixture
    def enhanced_generator(self):
        return EnhancedTradingSignalGenerator()

    @pytest.fixture
    def sample_price_history(self):
        return [1.0 + i * 0.001 for i in range(50)]

    @pytest.fixture
    def sample_user_context(self):
        return {
            "account_balance": 1000,
            "risk_tolerance": "medium",
            "experience_level": "intermediate",
            "max_daily_loss": 100,
            "max_position_size": 50
        }

    def test_enhanced_generator_initialization(self, enhanced_generator):
        """Test enhanced generator initializes correctly"""
        assert enhanced_generator is not None
        assert enhanced_generator.analyzer is not None
        assert enhanced_generator.advanced_analyzer is not None
        assert enhanced_generator.decision_engine is not None
        assert enhanced_generator.learning_system is not None
        assert enhanced_generator.risk_manager is not None

    @pytest.mark.asyncio
    async def test_should_use_ai_signal(self, enhanced_generator):
        """Test AI signal availability check"""
        result = await enhanced_generator.should_use_ai_signal("test_user", "R_10")
        assert isinstance(result, bool)
        # Should return True (always try AI) or False (fallback)

    @pytest.mark.asyncio
    async def test_generate_ai_signal_basic(self, enhanced_generator, sample_price_history, sample_user_context):
        """Test AI signal generation with basic setup"""
        # This test may return None if confidence is too low, which is expected
        signal = await enhanced_generator.generate_ai_signal(
            user_id="test_user",
            symbol="R_10",
            price_history=sample_price_history,
            current_price=sample_price_history[-1],
            user_context=sample_user_context,
            account_balance=1000,
            current_positions=[]
        )

        # Signal may be None if confidence is too low or risk is too high
        if signal is not None:
            assert signal.symbol == "R_10"
            assert signal.user_id == "test_user"
            assert signal.signal_type in ["BUY_CALL", "BUY_PUT", "HOLD"]
            assert 0 <= signal.confidence <= 1
            assert signal.recommended_amount >= 0
            assert len(signal.reasoning) > 0


@pytest.mark.asyncio
async def test_ai_integration_flow():
    """Test complete AI integration flow"""
    # This is an integration test that tests the complete flow
    enhanced_generator = EnhancedTradingSignalGenerator()

    price_history = [1.0 + i * 0.001 for i in range(50)]
    user_context = {
        "account_balance": 1000,
        "risk_tolerance": "medium",
        "experience_level": "intermediate",
        "max_daily_loss": 100,
        "max_position_size": 50
    }

    # Test that the flow doesn't crash
    try:
        signal = await enhanced_generator.generate_ai_signal(
            user_id="integration_test_user",
            symbol="R_10",
            price_history=price_history,
            current_price=price_history[-1],
            user_context=user_context,
            account_balance=1000,
            current_positions=[]
        )

        # The test passes if no exception is raised
        # Signal may be None, which is acceptable
        assert True

    except Exception as e:
        pytest.fail(f"AI integration flow failed: {e}")


# Mock tests for when OpenAI API is not available
@patch('app.core.config.settings.openai_api_key', '')
def test_ai_fallback_without_openai():
    """Test that AI components work without OpenAI API key"""
    analyzer = AdvancedMarketAnalyzer()
    assert analyzer.llm is None

    decision_engine = TradingDecisionEngine()
    assert decision_engine.llm is None

    risk_manager = AIRiskManager()
    assert risk_manager.llm is None

    # Components should still be functional without LLM
