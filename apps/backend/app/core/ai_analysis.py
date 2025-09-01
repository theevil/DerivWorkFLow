import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
from loguru import logger

from app.models.trading import MarketAnalysisInDB, TradingSignalInDB


class TechnicalIndicators:
    """Calculate technical indicators for market analysis"""
    
    @staticmethod
    def rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return None
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi)
    
    @staticmethod
    def macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[Dict[str, float]]:
        """Calculate MACD indicator"""
        if len(prices) < slow:
            return None
            
        prices_array = np.array(prices)
        ema_fast = TechnicalIndicators._ema(prices_array, fast)
        ema_slow = TechnicalIndicators._ema(prices_array, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators._ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            "macd": float(macd_line[-1]),
            "signal": float(signal_line[-1]),
            "histogram": float(histogram[-1])
        }
    
    @staticmethod
    def bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Optional[Dict[str, float]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return None
            
        recent_prices = prices[-period:]
        sma = np.mean(recent_prices)
        std = np.std(recent_prices)
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        
        return {
            "upper": float(upper_band),
            "middle": float(sma),
            "lower": float(lower_band)
        }
    
    @staticmethod
    def _ema(prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        alpha = 2 / (period + 1)
        ema = np.zeros_like(prices)
        ema[0] = prices[0]
        
        for i in range(1, len(prices)):
            ema[i] = alpha * prices[i] + (1 - alpha) * ema[i-1]
            
        return ema
    
    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 20) -> Optional[float]:
        """Calculate price volatility"""
        if len(prices) < period:
            return None
            
        recent_prices = prices[-period:]
        returns = np.diff(np.log(recent_prices))
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        return float(volatility)


class MarketAnalyzer:
    """AI-powered market analysis engine"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
    
    def analyze_market(self, symbol: str, price_history: List[float], current_price: float) -> MarketAnalysisInDB:
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
    
    def _determine_trend(self, prices: List[float]) -> str:
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


class TradingSignalGenerator:
    """Generate trading signals based on market analysis"""
    
    def __init__(self):
        self.analyzer = MarketAnalyzer()
    
    def generate_signal(
        self,
        user_id: str,
        symbol: str,
        analysis: MarketAnalysisInDB,
        trading_params: Dict[str, Any]
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
    
    def _calculate_position_size(self, trading_params: Dict[str, Any], confidence: float) -> float:
        """Calculate recommended position size"""
        base_size = trading_params.get("position_size", 10.0)
        # Adjust based on confidence
        return base_size * confidence
    
    def _calculate_duration(self, analysis: MarketAnalysisInDB, trading_params: Dict[str, Any]) -> int:
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
