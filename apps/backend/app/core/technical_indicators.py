import numpy as np
from typing import Optional


class TechnicalIndicators:
    """Calculate technical indicators for market analysis"""

    @staticmethod
    def rsi(prices: list[float], period: int = 14) -> Optional[float]:
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
    def macd(prices: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[dict[str, float]]:
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
    def bollinger_bands(prices: list[float], period: int = 20, std_dev: float = 2) -> Optional[dict[str, float]]:
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
    def calculate_volatility(prices: list[float], period: int = 20) -> Optional[float]:
        """Calculate price volatility"""
        if len(prices) < period:
            return None

        recent_prices = prices[-period:]
        returns = np.diff(np.log(recent_prices))
        volatility = np.std(returns) * np.sqrt(252)  # Annualized volatility
        return float(volatility)
