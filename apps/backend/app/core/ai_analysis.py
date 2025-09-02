from datetime import datetime
from typing import Any, Optional

import numpy as np
from loguru import logger

from app.ai.decision_engine import TradingDecisionEngine
from app.ai.learning_system import HistoricalLearningSystem
from app.ai.market_analyzer import AdvancedMarketAnalyzer
from app.ai.risk_manager import AIRiskManager
from app.core.technical_indicators import TechnicalIndicators
from app.models.trading import MarketAnalysisInDB, TradingSignalInDB


class MarketAnalyzer:
    """AI-powered market analysis engine"""

    def __init__(self):
        self.indicators = TechnicalIndicators()

    def analyze_market(self, symbol: str, price_history: list[float], current_price: float) -> MarketAnalysisInDB:
        """Perform comprehensive market analysis"""
        analysis = MarketAnalysisInDB(
            symbol=symbol,
            current_price=current_price,
            price_history=price_history[-100:],  # Keep last 100 prices
        )

        # Calculate technical indicators
        analysis.rsi = self.indicators.rsi(price_history)

        macd_data = self.indicators.macd(price_history)
        if macd_data:
            analysis.macd = macd_data["macd"]

        bollinger = self.indicators.bollinger_bands(price_history)
        if bollinger:
            analysis.bollinger_upper = bollinger["upper"]
            analysis.bollinger_lower = bollinger["lower"]

        analysis.volatility = self.indicators.calculate_volatility(price_history)

        # Determine trend
        analysis.trend = self._determine_trend(price_history)

        # Calculate confidence score
        analysis.confidence = self._calculate_confidence(analysis)

        logger.info(f"Market analysis completed for {symbol}: trend={analysis.trend}, confidence={analysis.confidence}")
        return analysis

    def _determine_trend(self, prices: list[float]) -> str:
        """Determine market trend"""
        if len(prices) < 10:
            return "sideways"

        recent_prices = prices[-10:]
        slope = np.polyfit(range(len(recent_prices)), recent_prices, 1)[0]

        if slope > 0.001:
            return "up"
        elif slope < -0.001:
            return "down"
        else:
            return "sideways"

    def _calculate_confidence(self, analysis: MarketAnalysisInDB) -> float:
        """Calculate confidence score based on multiple indicators"""
        confidence_factors = []

        # RSI confidence
        if analysis.rsi is not None:
            if analysis.rsi < 30 or analysis.rsi > 70:
                confidence_factors.append(0.8)  # Strong signal
            elif 40 <= analysis.rsi <= 60:
                confidence_factors.append(0.3)  # Weak signal
            else:
                confidence_factors.append(0.6)  # Medium signal

        # Bollinger Bands confidence
        if analysis.bollinger_upper and analysis.bollinger_lower:
            current_price = analysis.current_price
            if current_price >= analysis.bollinger_upper or current_price <= analysis.bollinger_lower:
                confidence_factors.append(0.7)  # Strong signal
            else:
                confidence_factors.append(0.4)  # Weak signal

        # Volatility confidence
        if analysis.volatility is not None:
            if analysis.volatility > 0.3:
                confidence_factors.append(0.5)  # High volatility = lower confidence
            else:
                confidence_factors.append(0.8)  # Low volatility = higher confidence

        return float(np.mean(confidence_factors)) if confidence_factors else 0.5


class EnhancedTradingSignalGenerator:
    """Enhanced trading signal generator with AI integration"""

    def __init__(self):
        self.analyzer = MarketAnalyzer()
        self.advanced_analyzer = AdvancedMarketAnalyzer()
        self.decision_engine = TradingDecisionEngine()
        self.learning_system = HistoricalLearningSystem()
        self.risk_manager = AIRiskManager()

    async def generate_ai_signal(
        self,
        user_id: str,
        symbol: str,
        price_history: list[float],
        current_price: float,
        user_context: dict[str, Any],
        account_balance: float,
        current_positions: Optional[list[Any]] = None
    ) -> Optional[TradingSignalInDB]:
        """
        Generate trading signal using AI analysis and decision engine

        Args:
            user_id: User identifier
            symbol: Trading symbol
            price_history: Historical price data
            current_price: Current market price
            user_context: User trading context and preferences
            account_balance: User's account balance
            current_positions: Current open positions

        Returns:
            Enhanced trading signal with AI insights
        """
        try:
            logger.info(f"Generating AI signal for {symbol} (user: {user_id})")

            # Step 1: Enhanced market analysis
            market_analysis = await self.advanced_analyzer.analyze_market_advanced(
                symbol=symbol,
                price_history=price_history,
                current_price=current_price,
                market_context={
                    "timeframe": "5m",
                    "session": "active",
                    "conditions": "normal"
                }
            )

            # Step 2: AI-powered trading decision
            trading_decision = await self.decision_engine.make_trading_decision(
                symbol=symbol,
                price_history=price_history,
                current_price=current_price,
                user_context=user_context
            )

            # Step 3: Risk assessment
            portfolio_context = {
                "position_count": len(current_positions) if current_positions else 0,
                "total_exposure": sum(pos.amount for pos in current_positions if hasattr(pos, 'amount')) if current_positions else 0,
                "daily_pnl": 0,  # Would be calculated from actual positions
                "max_daily_loss": user_context.get("max_daily_loss", 100)
            }

            market_data = {
                "current_price": current_price,
                "volatility": market_analysis.confidence or 0.2,
                "trend": market_analysis.trend_direction,
                "session": "active",
                "rsi": 50,  # Would come from technical analysis
                "macd": 0,
                "bollinger_position": "middle"
            }

            risk_assessment = await self.risk_manager.assess_position_risk(
                symbol=symbol,
                position_size=trading_decision.position_size,
                account_balance=account_balance,
                market_data=market_data,
                user_context=user_context,
                portfolio_context=portfolio_context
            )

            # Step 4: Apply risk management
            if risk_assessment.recommended_action in ["halt_trading", "emergency_stop"]:
                logger.warning(f"Trading halted for {symbol} due to risk: {risk_assessment.reasoning}")
                return None

            if trading_decision.action == "HOLD":
                logger.info(f"AI decision: HOLD for {symbol}")
                return None

            # Step 5: Apply ML predictions if available
            try:
                # Prepare features for ML prediction
                ml_features = {
                    "hour": datetime.utcnow().hour,
                    "day_of_week": datetime.utcnow().weekday(),
                    "rsi": 50,  # Would come from technical indicators
                    "macd": 0,
                    "bollinger_upper": 0,
                    "bollinger_lower": 0,
                    "volatility": market_analysis.confidence or 0.2,
                    "current_price": current_price,
                    "confidence": trading_decision.confidence,
                    "price_change_1": 0,
                    "price_change_5": 0,
                    "price_change_10": 0,
                    "price_std": 0,
                    "price_mean": current_price,
                    "success_rate": 0,
                    "avg_profit": 0
                }

                # Get ML predictions
                ml_signal, ml_confidence = await self.learning_system.predict_signal(ml_features)
                ml_risk, ml_risk_confidence = await self.learning_system.predict_risk(ml_features)

                # Combine AI decision with ML predictions
                if ml_confidence > 0.7 and ml_signal != "HOLD":
                    # ML has high confidence, use ML signal
                    final_action = ml_signal
                    combined_confidence = (trading_decision.confidence + ml_confidence) / 2
                    logger.info(f"Using ML signal: {ml_signal} (confidence: {ml_confidence:.3f})")
                else:
                    # Use AI decision
                    final_action = trading_decision.action
                    combined_confidence = trading_decision.confidence

            except Exception as e:
                logger.warning(f"ML prediction failed, using AI decision: {e}")
                final_action = trading_decision.action
                combined_confidence = trading_decision.confidence

            # Step 6: Apply final risk adjustments
            adjusted_position_size = trading_decision.position_size * risk_assessment.position_size_adjustment

            # Only generate signal if confidence is above threshold
            if combined_confidence < 0.6:
                logger.info(f"Signal confidence too low: {combined_confidence:.3f}")
                return None

            # Step 7: Create enhanced trading signal
            signal = TradingSignalInDB(
                user_id=user_id,
                symbol=symbol,
                signal_type=final_action,
                confidence=combined_confidence,
                recommended_amount=adjusted_position_size,
                recommended_duration=trading_decision.duration // 60,  # Convert to minutes
                reasoning=self._create_enhanced_reasoning(
                    market_analysis, trading_decision, risk_assessment, ml_confidence if 'ml_confidence' in locals() else 0
                )
            )

            logger.info(f"AI signal generated: {final_action} for {symbol} with confidence {combined_confidence:.3f}")
            return signal

        except Exception as e:
            logger.error(f"Error generating AI signal: {e}")
            return None

    def _create_enhanced_reasoning(self, market_analysis, trading_decision, risk_assessment, ml_confidence: float) -> str:
        """Create comprehensive reasoning for the trading signal"""

        reasoning_parts = [
            f"Market Analysis: {market_analysis.trend_direction} trend with {market_analysis.confidence_score:.2f} confidence",
            f"AI Decision: {trading_decision.action} based on workflow analysis",
            f"Risk Level: {risk_assessment.risk_level} ({risk_assessment.risk_score:.2f})",
        ]

        if ml_confidence > 0.5:
            reasoning_parts.append(f"ML Validation: {ml_confidence:.2f} confidence")

        reasoning_parts.extend([
            f"Key Insights: {', '.join(market_analysis.key_insights[:2])}",
            f"Risk Factors: {', '.join(risk_assessment.risk_factors[:2])}"
        ])

        return " | ".join(reasoning_parts)

    async def should_use_ai_signal(self, user_id: str, symbol: str) -> bool:
        """Determine if AI signal should be used for this user/symbol"""
        try:
            # Check if models are available and trained
            model_key = user_id  # User-specific models

            # Try to load user-specific models
            models_loaded = await self.learning_system.load_models(model_key)

            if not models_loaded:
                # Try global models
                models_loaded = await self.learning_system.load_models("global")

            # Use AI signal if models are available or if basic AI analysis is sufficient
            return True  # Always try AI signal, fallback to basic if needed

        except Exception as e:
            logger.error(f"Error checking AI signal availability: {e}")
            return False


class TradingSignalGenerator:
    """Generate trading signals based on market analysis (Legacy - kept for compatibility)"""

    def __init__(self):
        self.analyzer = MarketAnalyzer()
        # Initialize enhanced generator for advanced features
        self.enhanced_generator = EnhancedTradingSignalGenerator()

    def generate_signal(
        self,
        user_id: str,
        symbol: str,
        analysis: MarketAnalysisInDB,
        trading_params: dict[str, Any]
    ) -> Optional[TradingSignalInDB]:
        """Generate trading signal based on analysis"""

        signal_type = self._determine_signal_type(analysis)
        if signal_type == "HOLD":
            return None

        confidence = analysis.confidence or 0.5

        # Only generate signals with sufficient confidence
        if confidence < 0.6:
            return None

        recommended_amount = self._calculate_position_size(trading_params, confidence)
        recommended_duration = self._calculate_duration(analysis, trading_params)
        reasoning = self._generate_reasoning(analysis, signal_type)

        signal = TradingSignalInDB(
            user_id=user_id,
            symbol=symbol,
            signal_type=signal_type,
            confidence=confidence,
            recommended_amount=recommended_amount,
            recommended_duration=recommended_duration,
            reasoning=reasoning
        )

        logger.info(f"Generated signal for {symbol}: {signal_type} with confidence {confidence}")
        return signal

    async def generate_enhanced_signal(
        self,
        user_id: str,
        symbol: str,
        analysis: MarketAnalysisInDB,
        trading_params: dict[str, Any],
        user_context: dict[str, Any],
        account_balance: float,
        current_positions: Optional[list[Any]] = None
    ) -> Optional[TradingSignalInDB]:
        """
        Generate enhanced signal using AI if available, fallback to traditional analysis

        Args:
            user_id: User identifier
            symbol: Trading symbol
            analysis: Market analysis result
            trading_params: Trading parameters
            user_context: User context and preferences
            account_balance: User's account balance
            current_positions: Current open positions

        Returns:
            Trading signal with enhanced AI analysis if available
        """
        try:
            # Check if we should use AI signal
            use_ai = await self.enhanced_generator.should_use_ai_signal(user_id, symbol)

            if use_ai and analysis.price_history and len(analysis.price_history) > 10:
                # Try to generate AI signal
                ai_signal = await self.enhanced_generator.generate_ai_signal(
                    user_id=user_id,
                    symbol=symbol,
                    price_history=analysis.price_history,
                    current_price=analysis.current_price,
                    user_context=user_context,
                    account_balance=account_balance,
                    current_positions=current_positions
                )

                if ai_signal:
                    logger.info(f"Using AI-generated signal for {symbol}")
                    return ai_signal
                else:
                    logger.info(f"AI signal not generated for {symbol}, using traditional analysis")

            # Fallback to traditional signal generation
            traditional_signal = self.generate_signal(user_id, symbol, analysis, trading_params)

            if traditional_signal:
                logger.info(f"Using traditional signal for {symbol}")

            return traditional_signal

        except Exception as e:
            logger.error(f"Error in enhanced signal generation: {e}")
            # Final fallback to basic signal
            return self.generate_signal(user_id, symbol, analysis, trading_params)

    def _determine_signal_type(self, analysis: MarketAnalysisInDB) -> str:
        """Determine the type of trading signal"""
        signals = []

        # RSI signals
        if analysis.rsi is not None:
            if analysis.rsi < 30:
                signals.append("BUY_CALL")  # Oversold
            elif analysis.rsi > 70:
                signals.append("BUY_PUT")   # Overbought

        # Bollinger Bands signals
        if analysis.bollinger_upper and analysis.bollinger_lower:
            current_price = analysis.current_price
            if current_price <= analysis.bollinger_lower:
                signals.append("BUY_CALL")  # Price at lower band
            elif current_price >= analysis.bollinger_upper:
                signals.append("BUY_PUT")   # Price at upper band

        # MACD signals
        if analysis.macd is not None:
            if analysis.macd > 0:
                signals.append("BUY_CALL")
            elif analysis.macd < 0:
                signals.append("BUY_PUT")

        # Trend signals
        if analysis.trend == "up":
            signals.append("BUY_CALL")
        elif analysis.trend == "down":
            signals.append("BUY_PUT")

        # Determine final signal based on consensus
        if len(signals) == 0:
            return "HOLD"

        # Count signal types
        call_signals = signals.count("BUY_CALL")
        put_signals = signals.count("BUY_PUT")

        if call_signals > put_signals:
            return "BUY_CALL"
        elif put_signals > call_signals:
            return "BUY_PUT"
        else:
            return "HOLD"

    def _calculate_position_size(self, trading_params: dict[str, Any], confidence: float) -> float:
        """Calculate recommended position size"""
        base_size = trading_params.get("position_size", 10.0)
        # Adjust based on confidence
        return base_size * confidence

    def _calculate_duration(self, analysis: MarketAnalysisInDB, trading_params: dict[str, Any]) -> int:
        """Calculate recommended trade duration"""
        base_duration = 5  # 5 minutes default

        # Adjust based on volatility
        if analysis.volatility and analysis.volatility > 0.3:
            return base_duration // 2  # Shorter duration for high volatility
        elif analysis.volatility and analysis.volatility < 0.1:
            return base_duration * 2   # Longer duration for low volatility

        return base_duration

    def _generate_reasoning(self, analysis: MarketAnalysisInDB, signal_type: str) -> str:
        """Generate human-readable reasoning for the signal"""
        reasons = []

        if analysis.rsi is not None:
            if analysis.rsi < 30:
                reasons.append(f"RSI at {analysis.rsi:.1f} indicates oversold conditions")
            elif analysis.rsi > 70:
                reasons.append(f"RSI at {analysis.rsi:.1f} indicates overbought conditions")

        if analysis.trend:
            reasons.append(f"Market trend is {analysis.trend}")

        if analysis.volatility:
            vol_desc = "high" if analysis.volatility > 0.3 else "low" if analysis.volatility < 0.1 else "moderate"
            reasons.append(f"Volatility is {vol_desc} at {analysis.volatility:.3f}")

        if analysis.macd is not None:
            momentum = "positive" if analysis.macd > 0 else "negative"
            reasons.append(f"MACD shows {momentum} momentum")

        reasoning = f"Signal: {signal_type}. " + ". ".join(reasons)
        return reasoning
