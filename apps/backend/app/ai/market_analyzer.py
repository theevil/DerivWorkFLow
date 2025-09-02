"""
Advanced Market Analyzer using LangChain for intelligent market analysis
"""

from typing import Any, Optional

from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.technical_indicators import TechnicalIndicators
from app.ai.local_ai_manager import local_ai_manager


class MarketAnalysisResult(BaseModel):
    """Structured output for market analysis"""
    trend_direction: str = Field(description="Market trend: bullish, bearish, or sideways")
    confidence_score: float = Field(description="Confidence in analysis (0-1)", ge=0, le=1)
    risk_level: str = Field(description="Risk assessment: low, medium, high")
    key_insights: list[str] = Field(description="Key market insights")
    recommended_action: str = Field(description="Recommended action: buy_call, buy_put, hold")
    reasoning: str = Field(description="Detailed reasoning for the recommendation")
    technical_summary: str = Field(description="Summary of technical indicators")
    ai_provider: str = Field(description="AI provider used: local, openai, fallback")


class TradingRecommendation(BaseModel):
    """Trading recommendation output"""
    action: str = Field(description="Recommended action: buy_call, buy_put, hold")
    confidence: float = Field(description="Confidence in recommendation (0-1)", ge=0, le=1)
    reasoning: str = Field(description="Detailed reasoning")


class AdvancedMarketAnalyzer:
    """Advanced market analyzer using LangChain for intelligent analysis"""

    def __init__(self):
        """Initialize the advanced market analyzer"""
        self.technical_indicators = TechnicalIndicators()

        # Initialize LangChain components for OpenAI
        if settings.openai_api_key:
            self.openai_llm = ChatOpenAI(
                model=settings.ai_model,
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens,
                openai_api_key=settings.openai_api_key
            )
        else:
            self.openai_llm = None
            logger.warning("OpenAI API key not configured.")

        # Initialize local AI
        self.local_ai_enabled = settings.local_ai_enabled
        if self.local_ai_enabled:
            logger.info("Local AI enabled for market analysis")

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
        return """You are an expert financial analyst specializing in binary options and synthetic indices trading.

        Your task is to analyze market data and provide structured insights for microtransactions.

        Key considerations for microtransactions:
        - Focus on short-term price movements (1-5 minutes)
        - Consider volatility and momentum indicators
        - Assess risk-reward ratios for small position sizes
        - Provide clear, actionable recommendations

        Always respond with valid JSON in the exact format specified."""

    def _get_analysis_human_prompt(self) -> str:
        """Get human prompt template for market analysis"""
        return """Analyze the following market data for {symbol}:

        PRICE DATA:
        - Current Price: ${current_price}
        - Price History: {price_summary}
        - Recent Trend: {trend_direction}

        TECHNICAL INDICATORS:
        - RSI: {rsi:.2f}
        - MACD: {macd:.4f}
        - Bollinger Bands Position: {bb_position}
        - Volatility: {volatility:.2f}

        MARKET CONTEXT:
        - Session: {session}
        - Timeframe: {timeframe}
        - Market Conditions: {conditions}

        {format_instructions}

        Provide a comprehensive market analysis with specific focus on microtransaction opportunities."""

    def _get_recommendation_system_prompt(self) -> str:
        """Get system prompt for trading recommendations"""
        return """You are a trading advisor specializing in binary options and synthetic indices.

        Provide specific, actionable trading recommendations based on market analysis.
        Consider the user's risk tolerance and account balance for position sizing.

        Always respond with valid JSON in the exact format specified."""

    def _get_recommendation_human_prompt(self) -> str:
        """Get human prompt template for trading recommendations"""
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
        Perform advanced market analysis using AI (local or OpenAI)

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

            # Determine AI provider to use
            ai_provider = self._determine_ai_provider()

            # If no AI available, fallback to basic analysis
            if ai_provider == "fallback":
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
            formatted_prompt = self._get_analysis_human_prompt().format(
                symbol=symbol,
                current_price=current_price,
                price_summary=price_summary,
                trend_direction=self._determine_trend_direction(price_history),
                rsi=technical_data.get('rsi', 50),
                macd=technical_data.get('macd', 0),
                bb_position=bb_position,
                volatility=technical_data.get('volatility', 0.2),
                session=context.get('session', 'active'),
                timeframe=context.get('timeframe', '5m'),
                conditions=context.get('conditions', 'normal'),
                format_instructions=self.analysis_parser.get_format_instructions()
            )

            # Generate analysis using selected AI provider
            if ai_provider == "local":
                analysis_result = await self._analyze_with_local_ai(formatted_prompt, symbol)
            elif ai_provider == "openai":
                analysis_result = await self._analyze_with_openai(formatted_prompt)
            else:
                analysis_result = self._fallback_analysis(symbol, technical_data, current_price)

            # Add AI provider info
            analysis_result.ai_provider = ai_provider

            return analysis_result

        except Exception as e:
            logger.error(f"Error in advanced market analysis: {e}")
            return self._fallback_analysis(symbol, technical_data, current_price)

    def _determine_ai_provider(self) -> str:
        """Determine which AI provider to use based on settings and availability"""
        # Check user preference
        if hasattr(settings, 'ai_provider'):
            preferred_provider = getattr(settings, 'ai_provider', 'local')
        else:
            preferred_provider = 'local'

        # Check availability
        if preferred_provider == "local" and self.local_ai_enabled:
            available_models = local_ai_manager.get_available_models()
            if available_models:
                return "local"

        if preferred_provider == "openai" and self.openai_llm:
            return "openai"

        # Fallback logic
        if self.local_ai_enabled and local_ai_manager.get_available_models():
            return "local"
        elif self.openai_llm:
            return "openai"
        else:
            return "fallback"

    async def _analyze_with_local_ai(self, prompt: str, symbol: str) -> MarketAnalysisResult:
        """Analyze market using local AI"""
        try:
            system_prompt = self._get_analysis_system_prompt()

            # Use the preferred local model
            preferred_model = settings.default_ai_model
            if preferred_model not in local_ai_manager.get_available_models():
                # Fallback to any available model
                available_models = local_ai_manager.get_available_models()
                if available_models:
                    preferred_model = available_models[0]
                else:
                    raise Exception("No local AI models available")

            response = await local_ai_manager.generate_response(
                prompt=prompt,
                model_name=preferred_model,
                system_prompt=system_prompt,
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens
            )

            # Parse the response
            try:
                # Try to extract JSON from the response
                import json
                import re

                # Look for JSON in the response
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    data = json.loads(json_str)
                else:
                    # If no JSON found, create a basic analysis
                    data = self._create_basic_analysis_from_text(response.content, symbol)

                return MarketAnalysisResult(**data)

            except Exception as parse_error:
                logger.warning(f"Failed to parse local AI response: {parse_error}")
                # Create basic analysis from text response
                return self._create_basic_analysis_from_text(response.content, symbol)

        except Exception as e:
            logger.error(f"Error in local AI analysis: {e}")
            raise

    async def _analyze_with_openai(self, prompt: str) -> MarketAnalysisResult:
        """Analyze market using OpenAI"""
        try:
            formatted_prompt = self.analysis_template.format_prompt(
                symbol=prompt.split("symbol: ")[1].split("\n")[0] if "symbol: " in prompt else "UNKNOWN",
                current_price=0,
                price_summary="",
                trend_direction="",
                rsi=50,
                macd=0,
                bb_position="middle",
                volatility=0.2,
                session="active",
                timeframe="5m",
                conditions="normal",
                format_instructions=self.analysis_parser.get_format_instructions()
            )

            response = await self.openai_llm.ainvoke(formatted_prompt.messages)
            return self.analysis_parser.parse(response.content)

        except Exception as e:
            logger.error(f"Error in OpenAI analysis: {e}")
            raise

    def _create_basic_analysis_from_text(self, text: str, symbol: str) -> dict:
        """Create basic analysis from text response when JSON parsing fails"""
        # Extract key information from text response
        text_lower = text.lower()

        # Determine trend
        if "bullish" in text_lower or "up" in text_lower or "buy" in text_lower:
            trend = "bullish"
        elif "bearish" in text_lower or "down" in text_lower or "sell" in text_lower:
            trend = "bearish"
        else:
            trend = "sideways"

        # Determine action
        if "buy" in text_lower and "call" in text_lower:
            action = "buy_call"
        elif "buy" in text_lower and "put" in text_lower:
            action = "buy_put"
        else:
            action = "hold"

        # Determine risk level
        if "high" in text_lower and "risk" in text_lower:
            risk = "high"
        elif "low" in text_lower and "risk" in text_lower:
            risk = "low"
        else:
            risk = "medium"

        return {
            "trend_direction": trend,
            "confidence_score": 0.6,
            "risk_level": risk,
            "key_insights": [text[:100] + "..." if len(text) > 100 else text],
            "recommended_action": action,
            "reasoning": text,
            "technical_summary": "Analysis based on AI response",
            "ai_provider": "local"
        }

    def _fallback_analysis(self, symbol: str, technical_data: dict, current_price: float) -> MarketAnalysisResult:
        """Fallback analysis when AI is not available"""
        trend = self._determine_trend_direction([current_price] + list(technical_data.get('price_history', [])))

        # Basic trend-based recommendation
        if trend == "bullish":
            action = "buy_call"
        elif trend == "bearish":
            action = "buy_put"
        else:
            action = "hold"

        return MarketAnalysisResult(
            trend_direction=trend,
            confidence_score=0.5,
            risk_level="medium",
            key_insights=["Basic technical analysis", "No AI insights available"],
            recommended_action=action,
            reasoning=f"Basic analysis based on {trend} trend",
            technical_summary="Fallback analysis using technical indicators only",
            ai_provider="fallback"
        )

    def _calculate_comprehensive_indicators(self, price_history: list[float], current_price: float) -> dict:
        """Calculate comprehensive technical indicators"""
        if len(price_history) < 10:
            return {"price_history": price_history}

        return {
            "rsi": self.technical_indicators.rsi(price_history),
            "macd": self.technical_indicators.macd(price_history),
            "bollinger_bands": self.technical_indicators.bollinger_bands(price_history),
            "volatility": self.technical_indicators.calculate_volatility(price_history),
            "price_history": price_history
        }

    def _create_price_summary(self, price_history: list[float]) -> str:
        """Create a summary of price history"""
        if len(price_history) < 2:
            return "Insufficient price data"

        recent_prices = price_history[-20:]  # Last 20 prices
        min_price = min(recent_prices)
        max_price = max(recent_prices)
        avg_price = sum(recent_prices) / len(recent_prices)

        return f"Range: ${min_price:.4f}-${max_price:.4f}, Avg: ${avg_price:.4f}"

    def _determine_trend_direction(self, prices: list[float]) -> str:
        """Determine trend direction from price history"""
        if len(prices) < 5:
            return "sideways"

        recent_prices = prices[-5:]
        if recent_prices[-1] > recent_prices[0]:
            return "bullish"
        elif recent_prices[-1] < recent_prices[0]:
            return "bearish"
        else:
            return "sideways"
