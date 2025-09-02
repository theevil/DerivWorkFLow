"""
Advanced Market Analyzer using LangChain for intelligent market analysis
"""

from typing import Any, Optional

import numpy as np
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.technical_indicators import TechnicalIndicators


class MarketAnalysisResult(BaseModel):
    """Structured output for market analysis"""
    trend_direction: str = Field(description="Market trend: bullish, bearish, or sideways")
    confidence_score: float = Field(description="Confidence in analysis (0-1)", ge=0, le=1)
    risk_level: str = Field(description="Risk assessment: low, medium, high")
    key_insights: list[str] = Field(description="Key market insights")
    recommended_action: str = Field(description="Recommended action: buy_call, buy_put, hold")
    reasoning: str = Field(description="Detailed reasoning for the recommendation")
    technical_summary: str = Field(description="Summary of technical indicators")


class TradingRecommendation(BaseModel):
    """Trading recommendation output"""
    action: str = Field(description="Trading action: BUY_CALL, BUY_PUT, HOLD")
    confidence: float = Field(description="Confidence level (0-1)", ge=0, le=1)
    position_size_multiplier: float = Field(description="Position size adjustment (0.5-2.0)", ge=0.5, le=2.0)
    time_horizon: str = Field(description="Recommended time horizon: short, medium, long")
    stop_loss_adjustment: float = Field(description="Stop loss adjustment factor", ge=0.5, le=2.0)
    reasoning: str = Field(description="Detailed reasoning")


class AdvancedMarketAnalyzer:
    """Advanced market analyzer using LangChain for intelligent analysis"""

    def __init__(self):
        """Initialize the advanced market analyzer"""
        self.technical_indicators = TechnicalIndicators()

        # Initialize LangChain components
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured. AI analysis will be limited.")
            self.llm = None
        else:
            self.llm = ChatOpenAI(
                model=settings.ai_model,
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens,
                openai_api_key=settings.openai_api_key
            )

        # Setup output parsers
        self.analysis_parser = PydanticOutputParser(pydantic_object=MarketAnalysisResult)
        self.recommendation_parser = PydanticOutputParser(pydantic_object=TradingRecommendation)

        # Create analysis prompt template
        self.analysis_template = ChatPromptTemplate.from_messages([
            SystemMessage(content=self._get_analysis_system_prompt()),
            HumanMessage(content=self._get_analysis_human_prompt())
        ])

        # Create recommendation prompt template
        self.recommendation_template = ChatPromptTemplate.from_messages([
            SystemMessage(content=self._get_recommendation_system_prompt()),
            HumanMessage(content=self._get_recommendation_human_prompt())
        ])

    def _get_analysis_system_prompt(self) -> str:
        """Get system prompt for market analysis"""
        return """You are an expert quantitative analyst specializing in synthetic indices trading on Deriv.

        Your expertise includes:
        - Technical analysis of synthetic indices (R_10, R_25, R_50, etc.)
        - Pattern recognition in price movements
        - Risk assessment and volatility analysis
        - Market sentiment interpretation

        Analyze the provided market data with focus on:
        1. Current market conditions and trends
        2. Technical indicator signals and convergence
        3. Volatility patterns and market sentiment
        4. Risk factors and potential reversals
        5. Entry/exit timing considerations

        Provide clear, actionable insights based on data-driven analysis.
        Be precise about confidence levels and reasoning."""

    def _get_analysis_human_prompt(self) -> str:
        """Get human prompt template for analysis"""
        return """Analyze the following market data for {symbol}:

        CURRENT PRICE: {current_price}
        PRICE HISTORY: {price_summary}

        TECHNICAL INDICATORS:
        - RSI: {rsi} (Oversold: <30, Overbought: >70)
        - MACD: {macd} (Signal: {macd_signal})
        - Bollinger Bands: Upper={bb_upper}, Lower={bb_lower}, Current Position={bb_position}
        - Volatility: {volatility} (Annual)
        - Recent Trend: {trend}

        MARKET CONTEXT:
        - Time Frame: {timeframe}
        - Trading Session: {session}
        - Market Conditions: {market_conditions}

        {format_instructions}

        Provide a comprehensive analysis with specific focus on synthetic indices characteristics."""

    def _get_recommendation_system_prompt(self) -> str:
        """Get system prompt for trading recommendations"""
        return """You are a senior trading strategist for synthetic indices on Deriv platform.

        Your role is to translate market analysis into specific, actionable trading recommendations.

        Consider:
        - Risk-reward ratios for different trade types
        - Optimal position sizing based on volatility and confidence
        - Time horizon selection for maximum probability of success
        - Stop-loss and take-profit level recommendations
        - Market timing and execution considerations

        Synthetic indices characteristics:
        - R_10: High frequency, moderate volatility
        - R_25: Medium frequency, higher volatility
        - R_50: Lower frequency, highest volatility
        - BOOM/CRASH: Spike patterns, extreme volatility

        Provide specific, executable recommendations with clear risk management."""

    def _get_recommendation_human_prompt(self) -> str:
        """Get human prompt for recommendations"""
        return """Based on this market analysis, provide a specific trading recommendation:

        ANALYSIS SUMMARY:
        {analysis_summary}

        USER CONTEXT:
        - Risk Tolerance: {risk_tolerance}
        - Account Balance: ${account_balance}
        - Max Position Size: ${max_position_size}
        - Trading Experience: {experience_level}
        - Current Positions: {current_positions}

        TRADING PARAMETERS:
        - Preferred Time Horizon: {time_horizon}
        - Max Daily Loss: ${max_daily_loss}
        - Profit Target: {profit_target}%

        {format_instructions}

        Provide a specific, actionable trading recommendation with detailed reasoning."""

    async def analyze_market_advanced(
        self,
        symbol: str,
        price_history: list[float],
        current_price: float,
        market_context: Optional[dict[str, Any]] = None
    ) -> MarketAnalysisResult:
        """
        Perform advanced market analysis using LangChain

        Args:
            symbol: Trading symbol
            price_history: Historical price data
            current_price: Current market price
            market_context: Additional market context

        Returns:
            MarketAnalysisResult with AI-powered insights
        """
        try:
            # Calculate technical indicators
            technical_data = self._calculate_comprehensive_indicators(price_history, current_price)

            # If no LLM available, fallback to basic analysis
            if not self.llm:
                return self._fallback_analysis(symbol, technical_data, current_price)

            # Prepare market context
            context = market_context or {}

            # Create price summary
            price_summary = self._create_price_summary(price_history)

            # Determine Bollinger Band position
            bb_position = "middle"
            if technical_data.get('bollinger_upper') and technical_data.get('bollinger_lower'):
                if current_price >= technical_data['bollinger_upper']:
                    bb_position = "above upper band"
                elif current_price <= technical_data['bollinger_lower']:
                    bb_position = "below lower band"
                else:
                    bb_position = "within bands"

            # Format the prompt
            formatted_prompt = self.analysis_template.format(
                symbol=symbol,
                current_price=current_price,
                price_summary=price_summary,
                rsi=technical_data.get('rsi', 'N/A'),
                macd=technical_data.get('macd', 'N/A'),
                macd_signal=technical_data.get('macd_signal', 'N/A'),
                bb_upper=technical_data.get('bollinger_upper', 'N/A'),
                bb_lower=technical_data.get('bollinger_lower', 'N/A'),
                bb_position=bb_position,
                volatility=technical_data.get('volatility', 'N/A'),
                trend=technical_data.get('trend', 'sideways'),
                timeframe=context.get('timeframe', '5-minute'),
                session=context.get('session', 'active'),
                market_conditions=context.get('conditions', 'normal'),
                format_instructions=self.analysis_parser.get_format_instructions()
            )

            # Get AI analysis
            response = await self.llm.ainvoke(formatted_prompt.messages)
            analysis_result = self.analysis_parser.parse(response.content)

            logger.info(f"Advanced AI analysis completed for {symbol}: {analysis_result.recommended_action}")
            return analysis_result

        except Exception as e:
            logger.error(f"Error in advanced market analysis: {e}")
            # Fallback to technical analysis
            return self._fallback_analysis(symbol, technical_data, current_price)

    async def get_trading_recommendation(
        self,
        analysis: MarketAnalysisResult,
        user_context: dict[str, Any]
    ) -> TradingRecommendation:
        """
        Get specific trading recommendation based on analysis

        Args:
            analysis: Market analysis result
            user_context: User trading context and preferences

        Returns:
            TradingRecommendation with specific actions
        """
        try:
            if not self.llm:
                return self._fallback_recommendation(analysis, user_context)

            # Prepare analysis summary
            analysis_summary = f"""
            Trend: {analysis.trend_direction}
            Confidence: {analysis.confidence_score:.2f}
            Risk Level: {analysis.risk_level}
            Recommended Action: {analysis.recommended_action}
            Key Insights: {', '.join(analysis.key_insights)}
            Technical Summary: {analysis.technical_summary}
            Reasoning: {analysis.reasoning}
            """

            # Format recommendation prompt
            formatted_prompt = self.recommendation_template.format(
                analysis_summary=analysis_summary,
                risk_tolerance=user_context.get('risk_tolerance', 'medium'),
                account_balance=user_context.get('account_balance', 1000),
                max_position_size=user_context.get('max_position_size', 100),
                experience_level=user_context.get('experience_level', 'intermediate'),
                current_positions=user_context.get('current_positions', 0),
                time_horizon=user_context.get('time_horizon', 'short'),
                max_daily_loss=user_context.get('max_daily_loss', 50),
                profit_target=user_context.get('profit_target', 20),
                format_instructions=self.recommendation_parser.get_format_instructions()
            )

            # Get AI recommendation
            response = await self.llm.ainvoke(formatted_prompt.messages)
            recommendation = self.recommendation_parser.parse(response.content)

            logger.info(f"Trading recommendation generated: {recommendation.action}")
            return recommendation

        except Exception as e:
            logger.error(f"Error generating trading recommendation: {e}")
            return self._fallback_recommendation(analysis, user_context)

    def _calculate_comprehensive_indicators(self, price_history: list[float], current_price: float) -> dict[str, Any]:
        """Calculate comprehensive technical indicators"""
        indicators = {}

        try:
            # Basic indicators
            indicators['rsi'] = self.technical_indicators.rsi(price_history)

            macd_data = self.technical_indicators.macd(price_history)
            if macd_data:
                indicators.update({
                    'macd': macd_data['macd'],
                    'macd_signal': macd_data['signal'],
                    'macd_histogram': macd_data['histogram']
                })

            bollinger = self.technical_indicators.bollinger_bands(price_history)
            if bollinger:
                indicators.update({
                    'bollinger_upper': bollinger['upper'],
                    'bollinger_lower': bollinger['lower'],
                    'bollinger_middle': bollinger['middle']
                })

            indicators['volatility'] = self.technical_indicators.calculate_volatility(price_history)

            # Trend analysis
            indicators['trend'] = self._analyze_trend(price_history)

            # Additional indicators
            if len(price_history) >= 20:
                indicators['sma_20'] = np.mean(price_history[-20:])
            if len(price_history) >= 50:
                indicators['sma_50'] = np.mean(price_history[-50:])

            # Price momentum
            if len(price_history) >= 10:
                indicators['momentum_10'] = (current_price - price_history[-10]) / price_history[-10] * 100

        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")

        return indicators

    def _analyze_trend(self, prices: list[float]) -> str:
        """Analyze price trend"""
        if len(prices) < 10:
            return "sideways"

        # Short-term trend (last 10 periods)
        recent_prices = prices[-10:]
        short_slope = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]

        # Medium-term trend (last 20 periods if available)
        if len(prices) >= 20:
            medium_prices = prices[-20:]
            medium_slope = np.polyfit(range(len(medium_prices)), medium_prices, 1)[0]
        else:
            medium_slope = short_slope

        # Combine trends
        if short_slope > 0.001 and medium_slope > 0.001:
            return "strong_bullish"
        elif short_slope > 0.001:
            return "bullish"
        elif short_slope < -0.001 and medium_slope < -0.001:
            return "strong_bearish"
        elif short_slope < -0.001:
            return "bearish"
        else:
            return "sideways"

    def _create_price_summary(self, price_history: list[float]) -> str:
        """Create a summary of price history"""
        if len(price_history) < 5:
            return "Insufficient data"

        recent = price_history[-10:]
        high = max(recent)
        low = min(recent)
        change = ((recent[-1] - recent[0]) / recent[0]) * 100

        return f"Recent range: {low:.5f} - {high:.5f}, Change: {change:.2f}%"

    def _fallback_analysis(self, symbol: str, technical_data: dict, current_price: float) -> MarketAnalysisResult:
        """Fallback analysis when LLM is not available"""

        # Basic analysis using technical indicators
        rsi = technical_data.get('rsi', 50)
        trend = technical_data.get('trend', 'sideways')
        volatility = technical_data.get('volatility', 0.2)

        # Determine trend direction
        if 'bullish' in trend:
            trend_direction = "bullish"
        elif 'bearish' in trend:
            trend_direction = "bearish"
        else:
            trend_direction = "sideways"

        # Calculate confidence
        confidence = 0.5
        if rsi and (rsi < 30 or rsi > 70):
            confidence += 0.2
        if 'strong' in trend:
            confidence += 0.2
        if volatility and volatility < 0.3:
            confidence += 0.1

        confidence = min(confidence, 1.0)

        # Determine risk level
        risk_level = "medium"
        if volatility and volatility > 0.4:
            risk_level = "high"
        elif volatility and volatility < 0.2:
            risk_level = "low"

        # Generate recommendation
        if rsi and rsi < 30 and 'bullish' in trend:
            action = "buy_call"
        elif rsi and rsi > 70 and 'bearish' in trend:
            action = "buy_put"
        else:
            action = "hold"

        return MarketAnalysisResult(
            trend_direction=trend_direction,
            confidence_score=confidence,
            risk_level=risk_level,
            key_insights=[
                f"RSI: {rsi:.1f}" if rsi else "RSI: Not available",
                f"Trend: {trend}",
                f"Volatility: {volatility:.3f}" if volatility else "Volatility: Not available"
            ],
            recommended_action=action,
            reasoning=f"Technical analysis suggests {action} based on RSI ({rsi:.1f}) and trend ({trend})",
            technical_summary=f"RSI: {rsi:.1f}, Trend: {trend}, Volatility: {volatility:.3f}" if all([rsi, volatility]) else "Limited technical data available"
        )

    def _fallback_recommendation(self, analysis: MarketAnalysisResult, user_context: dict) -> TradingRecommendation:
        """Fallback recommendation when LLM is not available"""

        action_map = {
            "buy_call": "BUY_CALL",
            "buy_put": "BUY_PUT",
            "hold": "HOLD"
        }

        action = action_map.get(analysis.recommended_action, "HOLD")

        # Adjust position size based on confidence and risk
        size_multiplier = analysis.confidence_score
        if analysis.risk_level == "high":
            size_multiplier *= 0.7
        elif analysis.risk_level == "low":
            size_multiplier *= 1.2

        size_multiplier = max(0.5, min(2.0, size_multiplier))

        return TradingRecommendation(
            action=action,
            confidence=analysis.confidence_score,
            position_size_multiplier=size_multiplier,
            time_horizon="short",
            stop_loss_adjustment=1.0,
            reasoning=f"Based on technical analysis: {analysis.reasoning}"
        )
