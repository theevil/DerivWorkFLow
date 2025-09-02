"""
AI-powered Risk Management System for adaptive risk control
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import numpy as np
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.trading import TradePositionInDB, TradingParametersInDB


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskAction(str, Enum):
    """Risk management actions"""
    ALLOW = "allow"
    REDUCE_POSITION = "reduce_position"
    HALT_TRADING = "halt_trading"
    CLOSE_POSITIONS = "close_positions"
    EMERGENCY_STOP = "emergency_stop"


class RiskAssessment(BaseModel):
    """Risk assessment result"""
    risk_level: RiskLevel
    risk_score: float = Field(ge=0, le=1, description="Risk score from 0 (low) to 1 (high)")
    recommended_action: RiskAction
    position_size_adjustment: float = Field(ge=0, le=2, description="Position size multiplier")
    stop_loss_adjustment: float = Field(ge=0.5, le=2, description="Stop loss adjustment factor")
    confidence: float = Field(ge=0, le=1, description="Confidence in assessment")
    risk_factors: list[str] = Field(description="Identified risk factors")
    warnings: list[str] = Field(description="Risk warnings")
    reasoning: str = Field(description="Detailed reasoning")


class PortfolioRisk(BaseModel):
    """Portfolio risk analysis"""
    total_exposure: float
    max_daily_loss_risk: float
    concentration_risk: float
    correlation_risk: float
    volatility_risk: float
    drawdown_risk: float
    overall_risk_score: float
    recommended_actions: list[str]


class AIRiskManager:
    """
    AI-powered risk management system with adaptive controls
    """

    def __init__(self):
        """Initialize the AI risk manager"""
        # Initialize LLM for risk analysis
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model=settings.ai_model,
                temperature=0.1,  # Lower temperature for risk analysis
                max_tokens=800,
                openai_api_key=settings.openai_api_key
            )
        else:
            self.llm = None
            logger.warning("OpenAI API key not configured. Risk manager will use basic logic.")

        # Risk thresholds
        self.risk_thresholds = {
            "max_position_risk": 0.05,  # 5% of account per position
            "max_daily_loss": 0.1,      # 10% of account per day
            "max_portfolio_risk": 0.2,  # 20% of account total
            "volatility_threshold": 0.5, # 50% annualized volatility
            "correlation_threshold": 0.7, # 70% correlation
            "drawdown_threshold": 0.15,  # 15% drawdown
        }

        # Setup risk analysis prompt
        self.risk_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self._get_risk_system_prompt()),
            HumanMessage(content=self._get_risk_human_prompt())
        ])

    def _get_risk_system_prompt(self) -> str:
        """System prompt for risk analysis"""
        return """You are an expert risk management specialist for synthetic indices trading.

        Your role is to assess trading risk comprehensively and provide specific risk management recommendations.

        Consider these key risk factors:
        1. Position sizing relative to account balance
        2. Market volatility and current conditions
        3. Portfolio concentration and diversification
        4. Correlation between positions
        5. Maximum drawdown potential
        6. Time horizon and market timing
        7. User's risk tolerance and experience
        8. Current market regime (trending vs ranging)

        Synthetic indices characteristics to consider:
        - R_10, R_25, R_50: Predictable volatility patterns
        - BOOM/CRASH: Extreme volatility with spike patterns
        - Higher frequency indices have lower individual trade risk
        - Market sessions affect volatility patterns

        Provide specific, actionable risk management recommendations with clear reasoning.
        Be conservative in uncertain conditions."""

    def _get_risk_human_prompt(self) -> str:
        """Human prompt for risk analysis"""
        return """Analyze the trading risk for this scenario:

        POSITION DETAILS:
        - Symbol: {symbol}
        - Position Size: ${position_size}
        - Account Balance: ${account_balance}
        - Position as % of Account: {position_percentage:.2f}%

        MARKET CONDITIONS:
        - Current Price: {current_price}
        - Volatility: {volatility:.3f}
        - Market Trend: {trend}
        - Market Session: {session}

        PORTFOLIO CONTEXT:
        - Current Positions: {current_positions}
        - Total Exposure: ${total_exposure}
        - Daily P&L: ${daily_pnl}
        - Max Daily Loss Limit: ${max_daily_loss}

        USER PROFILE:
        - Risk Tolerance: {risk_tolerance}
        - Experience Level: {experience}
        - Trading Strategy: {strategy}

        TECHNICAL INDICATORS:
        - RSI: {rsi}
        - MACD: {macd}
        - Bollinger Position: {bb_position}

        Provide risk assessment in this exact JSON format:
        {{
            "risk_level": "low|medium|high|critical",
            "risk_score": 0.0-1.0,
            "recommended_action": "allow|reduce_position|halt_trading|close_positions|emergency_stop",
            "position_size_adjustment": 0.0-2.0,
            "stop_loss_adjustment": 0.5-2.0,
            "confidence": 0.0-1.0,
            "risk_factors": ["factor1", "factor2"],
            "warnings": ["warning1", "warning2"],
            "reasoning": "detailed reasoning"
        }}"""

    async def assess_position_risk(
        self,
        symbol: str,
        position_size: float,
        account_balance: float,
        market_data: dict[str, Any],
        user_context: dict[str, Any],
        portfolio_context: dict[str, Any]
    ) -> RiskAssessment:
        """
        Assess risk for a potential or existing position

        Args:
            symbol: Trading symbol
            position_size: Size of the position
            account_balance: User's account balance
            market_data: Current market conditions
            user_context: User's risk profile
            portfolio_context: Current portfolio state

        Returns:
            RiskAssessment with detailed risk analysis
        """
        try:
            # Calculate basic risk metrics
            position_percentage = (position_size / account_balance) * 100 if account_balance > 0 else 0

            # Use LLM analysis if available, otherwise fallback
            if self.llm:
                risk_assessment = await self._llm_risk_analysis(
                    symbol, position_size, account_balance, position_percentage,
                    market_data, user_context, portfolio_context
                )
            else:
                risk_assessment = self._basic_risk_analysis(
                    symbol, position_size, account_balance, position_percentage,
                    market_data, user_context, portfolio_context
                )

            # Apply additional validations
            risk_assessment = self._validate_and_adjust_risk(risk_assessment, portfolio_context)

            logger.info(f"Risk assessment for {symbol}: {risk_assessment.risk_level} ({risk_assessment.risk_score:.3f})")
            return risk_assessment

        except Exception as e:
            logger.error(f"Error in position risk assessment: {e}")
            return self._emergency_risk_assessment()

    async def _llm_risk_analysis(
        self,
        symbol: str,
        position_size: float,
        account_balance: float,
        position_percentage: float,
        market_data: dict,
        user_context: dict,
        portfolio_context: dict
    ) -> RiskAssessment:
        """Perform LLM-based risk analysis"""

        try:
            # Format the prompt
            formatted_prompt = self.risk_prompt.format(
                symbol=symbol,
                position_size=position_size,
                account_balance=account_balance,
                position_percentage=position_percentage,
                current_price=market_data.get("current_price", 0),
                volatility=market_data.get("volatility", 0.2),
                trend=market_data.get("trend", "sideways"),
                session=market_data.get("session", "active"),
                current_positions=portfolio_context.get("position_count", 0),
                total_exposure=portfolio_context.get("total_exposure", 0),
                daily_pnl=portfolio_context.get("daily_pnl", 0),
                max_daily_loss=user_context.get("max_daily_loss", 100),
                risk_tolerance=user_context.get("risk_tolerance", "medium"),
                experience=user_context.get("experience_level", "intermediate"),
                strategy=user_context.get("strategy", "technical"),
                rsi=market_data.get("rsi", 50),
                macd=market_data.get("macd", 0),
                bb_position=market_data.get("bollinger_position", "middle")
            )

            # Get LLM response
            response = await self.llm.ainvoke(formatted_prompt.messages)

            # Parse JSON response
            import json
            risk_data = json.loads(response.content)

            # Create RiskAssessment object
            risk_assessment = RiskAssessment(**risk_data)

            return risk_assessment

        except Exception as e:
            logger.error(f"Error in LLM risk analysis: {e}")
            return self._basic_risk_analysis(
                symbol, position_size, account_balance, position_percentage,
                market_data, user_context, portfolio_context
            )

    def _basic_risk_analysis(
        self,
        symbol: str,
        position_size: float,
        account_balance: float,
        position_percentage: float,
        market_data: dict,
        user_context: dict,
        portfolio_context: dict
    ) -> RiskAssessment:
        """Basic risk analysis fallback"""

        risk_factors = []
        warnings = []
        risk_score = 0.3  # Base risk

        # Position size risk
        if position_percentage > 10:
            risk_score += 0.3
            risk_factors.append("Large position size relative to account")
            warnings.append(f"Position is {position_percentage:.1f}% of account")
        elif position_percentage > 5:
            risk_score += 0.1
            risk_factors.append("Moderate position size")

        # Market volatility risk
        volatility = market_data.get("volatility", 0.2)
        if volatility > 0.4:
            risk_score += 0.2
            risk_factors.append("High market volatility")
            warnings.append(f"Volatility at {volatility:.1%}")
        elif volatility > 0.3:
            risk_score += 0.1
            risk_factors.append("Elevated volatility")

        # Portfolio concentration risk
        position_count = portfolio_context.get("position_count", 0)
        if position_count > 5:
            risk_score += 0.1
            risk_factors.append("High number of open positions")

        # Daily loss risk
        daily_pnl = portfolio_context.get("daily_pnl", 0)
        max_daily_loss = user_context.get("max_daily_loss", 100)
        if daily_pnl < -max_daily_loss * 0.8:
            risk_score += 0.3
            risk_factors.append("Approaching daily loss limit")
            warnings.append("Close to daily loss limit")
        elif daily_pnl < -max_daily_loss * 0.5:
            risk_score += 0.1
            risk_factors.append("Significant daily losses")

        # User experience adjustment
        experience = user_context.get("experience_level", "intermediate")
        if experience == "beginner":
            risk_score += 0.1
            risk_factors.append("Limited trading experience")
        elif experience == "expert":
            risk_score -= 0.05

        # Risk tolerance adjustment
        risk_tolerance = user_context.get("risk_tolerance", "medium")
        if risk_tolerance == "low":
            risk_score += 0.1
        elif risk_tolerance == "high":
            risk_score -= 0.05

        # Determine risk level and actions
        risk_score = max(0, min(1, risk_score))

        if risk_score > 0.8:
            risk_level = RiskLevel.CRITICAL
            recommended_action = RiskAction.EMERGENCY_STOP
            position_adjustment = 0.0
            stop_loss_adjustment = 0.5
        elif risk_score > 0.6:
            risk_level = RiskLevel.HIGH
            recommended_action = RiskAction.HALT_TRADING
            position_adjustment = 0.3
            stop_loss_adjustment = 0.7
        elif risk_score > 0.4:
            risk_level = RiskLevel.MEDIUM
            recommended_action = RiskAction.REDUCE_POSITION
            position_adjustment = 0.7
            stop_loss_adjustment = 0.8
        else:
            risk_level = RiskLevel.LOW
            recommended_action = RiskAction.ALLOW
            position_adjustment = 1.0
            stop_loss_adjustment = 1.0

        return RiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            recommended_action=recommended_action,
            position_size_adjustment=position_adjustment,
            stop_loss_adjustment=stop_loss_adjustment,
            confidence=0.7,  # Lower confidence for basic analysis
            risk_factors=risk_factors,
            warnings=warnings,
            reasoning=f"Basic risk analysis: Position {position_percentage:.1f}% of account, volatility {volatility:.1%}, risk score {risk_score:.2f}"
        )

    def _validate_and_adjust_risk(self, risk_assessment: RiskAssessment, portfolio_context: dict) -> RiskAssessment:
        """Apply additional validations and adjustments"""

        # Circuit breaker: Force emergency stop if critical conditions met
        daily_pnl = portfolio_context.get("daily_pnl", 0)
        max_daily_loss = portfolio_context.get("max_daily_loss", 100)

        if daily_pnl <= -max_daily_loss:
            risk_assessment.risk_level = RiskLevel.CRITICAL
            risk_assessment.recommended_action = RiskAction.EMERGENCY_STOP
            risk_assessment.position_size_adjustment = 0.0
            risk_assessment.warnings.append("Daily loss limit exceeded - Emergency stop activated")
            risk_assessment.reasoning += " | CIRCUIT BREAKER: Daily loss limit exceeded"

        # Correlation risk adjustment
        correlation_risk = portfolio_context.get("correlation_risk", 0)
        if correlation_risk > 0.8:
            risk_assessment.risk_score = min(1.0, risk_assessment.risk_score + 0.2)
            risk_assessment.risk_factors.append("High correlation between positions")

            if risk_assessment.risk_level == RiskLevel.LOW:
                risk_assessment.risk_level = RiskLevel.MEDIUM

        return risk_assessment

    def _emergency_risk_assessment(self) -> RiskAssessment:
        """Emergency risk assessment when analysis fails"""
        return RiskAssessment(
            risk_level=RiskLevel.CRITICAL,
            risk_score=1.0,
            recommended_action=RiskAction.EMERGENCY_STOP,
            position_size_adjustment=0.0,
            stop_loss_adjustment=0.5,
            confidence=0.1,
            risk_factors=["System error in risk analysis"],
            warnings=["Emergency risk assessment - manual review required"],
            reasoning="Emergency assessment due to system error"
        )

    async def assess_portfolio_risk(
        self,
        positions: list[TradePositionInDB],
        account_balance: float,
        trading_params: TradingParametersInDB
    ) -> PortfolioRisk:
        """
        Assess overall portfolio risk

        Args:
            positions: Current trading positions
            account_balance: Account balance
            trading_params: User's trading parameters

        Returns:
            PortfolioRisk with portfolio-level analysis
        """
        try:
            # Calculate portfolio metrics
            total_exposure = sum(pos.amount for pos in positions if pos.status == "open")
            position_values = [pos.profit_loss or 0 for pos in positions if pos.status == "open"]

            # Risk calculations
            exposure_ratio = total_exposure / account_balance if account_balance > 0 else 1

            # Daily P&L
            today = datetime.utcnow().date()
            daily_positions = [pos for pos in positions if pos.created_at.date() == today]
            daily_pnl = sum(pos.profit_loss or 0 for pos in daily_positions)
            daily_loss_risk = abs(daily_pnl) / trading_params.max_daily_loss if trading_params.max_daily_loss > 0 else 1

            # Concentration risk (symbol diversification)
            symbol_counts: dict[str, int] = {}
            for pos in positions:
                if pos.status == "open":
                    symbol_counts[pos.symbol] = symbol_counts.get(pos.symbol, 0) + 1

            max_symbol_concentration = max(symbol_counts.values()) / len(positions) if positions else 0
            concentration_risk = max_symbol_concentration

            # Volatility risk
            if position_values:
                portfolio_volatility = np.std(position_values) / np.mean([abs(v) for v in position_values]) if position_values else 0
            else:
                portfolio_volatility = 0

            # Drawdown risk
            [v for v in position_values if v > 0]
            [v for v in position_values if v < 0]

            if position_values:
                max_loss = min(position_values) if position_values else 0
                drawdown_risk = abs(max_loss) / total_exposure if total_exposure > 0 else 0
            else:
                drawdown_risk = 0

            # Overall risk score
            risk_components = [
                exposure_ratio * 0.3,
                daily_loss_risk * 0.25,
                concentration_risk * 0.2,
                min(portfolio_volatility, 1.0) * 0.15,
                drawdown_risk * 0.1
            ]
            overall_risk_score = sum(risk_components)

            # Generate recommendations
            recommendations = []

            if exposure_ratio > 0.5:
                recommendations.append("Reduce overall position sizes - portfolio overexposed")

            if daily_loss_risk > 0.8:
                recommendations.append("Approaching daily loss limit - consider stopping trading")

            if concentration_risk > 0.7:
                recommendations.append("High concentration in single symbols - diversify")

            if portfolio_volatility > 0.5:
                recommendations.append("High portfolio volatility - reduce position sizes")

            if not recommendations:
                recommendations.append("Portfolio risk within acceptable limits")

            return PortfolioRisk(
                total_exposure=total_exposure,
                max_daily_loss_risk=daily_loss_risk,
                concentration_risk=concentration_risk,
                correlation_risk=0.0,  # Would need correlation calculation
                volatility_risk=min(portfolio_volatility, 1.0),
                drawdown_risk=drawdown_risk,
                overall_risk_score=min(overall_risk_score, 1.0),
                recommended_actions=recommendations
            )

        except Exception as e:
            logger.error(f"Error in portfolio risk assessment: {e}")
            return PortfolioRisk(
                total_exposure=0,
                max_daily_loss_risk=1.0,
                concentration_risk=1.0,
                correlation_risk=1.0,
                volatility_risk=1.0,
                drawdown_risk=1.0,
                overall_risk_score=1.0,
                recommended_actions=["Error in risk assessment - manual review required"]
            )

    def should_halt_trading(self, portfolio_risk: PortfolioRisk, daily_pnl: float, max_daily_loss: float) -> tuple[bool, str]:
        """
        Determine if trading should be halted

        Returns:
            Tuple of (should_halt, reason)
        """
        # Check daily loss limit
        if daily_pnl <= -max_daily_loss:
            return True, "Daily loss limit exceeded"

        # Check if approaching daily loss limit
        if daily_pnl <= -max_daily_loss * 0.9:
            return True, "Approaching daily loss limit"

        # Check overall portfolio risk
        if portfolio_risk.overall_risk_score > 0.9:
            return True, "Extremely high portfolio risk"

        # Check multiple high risk factors
        high_risk_count = sum([
            portfolio_risk.max_daily_loss_risk > 0.8,
            portfolio_risk.concentration_risk > 0.8,
            portfolio_risk.volatility_risk > 0.8,
            portfolio_risk.drawdown_risk > 0.7
        ])

        if high_risk_count >= 3:
            return True, "Multiple high risk factors detected"

        return False, "Risk levels acceptable"

    async def get_adaptive_stop_loss(
        self,
        symbol: str,
        entry_price: float,
        current_price: float,
        volatility: float,
        time_in_trade: timedelta,
        user_risk_tolerance: str
    ) -> float:
        """
        Calculate adaptive stop loss based on market conditions

        Args:
            symbol: Trading symbol
            entry_price: Original entry price
            current_price: Current market price
            volatility: Current market volatility
            time_in_trade: Time since trade opened
            user_risk_tolerance: User's risk tolerance

        Returns:
            Recommended stop loss level
        """
        try:
            # Base stop loss percentage
            base_stop_loss = 0.02  # 2%

            # Adjust for volatility
            volatility_adjustment = min(volatility * 2, 0.05)  # Max 5% adjustment

            # Adjust for time in trade (trailing stop)
            time_hours = time_in_trade.total_seconds() / 3600
            trailing_factor = min(time_hours / 24, 0.5)  # Tighten over 24 hours

            # Adjust for user risk tolerance
            risk_multipliers = {
                "low": 0.7,
                "medium": 1.0,
                "high": 1.3
            }
            risk_multiplier = risk_multipliers.get(user_risk_tolerance, 1.0)

            # Calculate final stop loss
            stop_loss_pct = (base_stop_loss + volatility_adjustment) * risk_multiplier * (1 - trailing_factor * 0.3)

            # Apply to entry price
            stop_loss_price = entry_price * (1 - stop_loss_pct)

            # Ensure stop loss moves in favorable direction only
            if current_price > entry_price:  # Profitable trade
                # Move stop loss up, but not down
                previous_stop = entry_price * (1 - base_stop_loss)
                stop_loss_price = max(stop_loss_price, previous_stop)

            logger.debug(f"Adaptive stop loss for {symbol}: {stop_loss_price:.5f} ({stop_loss_pct:.2%})")
            return stop_loss_price

        except Exception as e:
            logger.error(f"Error calculating adaptive stop loss: {e}")
            return entry_price * 0.98  # 2% fallback

    def get_risk_limits(self, user_context: dict[str, Any]) -> dict[str, float]:
        """Get risk limits based on user profile"""

        base_limits = {
            "max_position_pct": 5.0,      # 5% of account per position
            "max_daily_loss_pct": 10.0,   # 10% of account per day
            "max_portfolio_pct": 20.0,    # 20% of account total exposure
            "max_correlation": 0.7,       # 70% max correlation
            "max_drawdown_pct": 15.0      # 15% max drawdown
        }

        # Adjust based on experience
        experience = user_context.get("experience_level", "intermediate")
        if experience == "beginner":
            for key in base_limits:
                base_limits[key] *= 0.5  # More conservative for beginners
        elif experience == "expert":
            for key in base_limits:
                base_limits[key] *= 1.2  # More flexible for experts

        # Adjust based on risk tolerance
        risk_tolerance = user_context.get("risk_tolerance", "medium")
        if risk_tolerance == "low":
            for key in base_limits:
                base_limits[key] *= 0.7
        elif risk_tolerance == "high":
            for key in base_limits:
                base_limits[key] *= 1.3

        return base_limits
