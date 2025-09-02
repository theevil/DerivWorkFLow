"""
Historical Learning System for improving AI trading decisions over time
"""

import json
from datetime import datetime, timedelta
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

from app.core.config import settings
from app.crud.trading import get_market_analysis_history, get_user_positions


class TradingPattern(dict):
    """Trading pattern data structure"""


class ModelPerformance(dict):
    """Model performance metrics"""


class HistoricalLearningSystem:
    """
    System for learning from historical trading data to improve AI decisions
    """

    def __init__(self):
        """Initialize the historical learning system"""
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.model_performance = {}
        self.last_training_time = {}

        # Model configurations
        self.model_configs = {
            "trend_classifier": RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            ),
            "signal_classifier": GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42
            ),
            "risk_classifier": RandomForestClassifier(
                n_estimators=80,
                max_depth=8,
                random_state=42
            )
        }

    async def train_models(self, db: AsyncIOMotorDatabase, user_id: Optional[str] = None) -> dict[str, ModelPerformance]:
        """
        Train all ML models using historical data

        Args:
            db: Database connection
            user_id: Optional user ID to train user-specific models

        Returns:
            Dictionary of model performance metrics
        """
        try:
            logger.info(f"Starting model training for user: {user_id or 'global'}")

            # Collect training data
            training_data = await self._collect_training_data(db, user_id)

            if len(training_data) < settings.min_training_samples:
                logger.warning(f"Insufficient training data: {len(training_data)} samples (minimum: {settings.min_training_samples})")
                return {}

            # Prepare features and targets
            features_df = await self._prepare_features(training_data)

            if features_df.empty:
                logger.warning("No features could be prepared from training data")
                return {}

            # Train individual models
            performance_results = {}

            # Train trend classification model
            if "trend_target" in features_df.columns:
                trend_performance = await self._train_trend_classifier(features_df)
                performance_results["trend_classifier"] = trend_performance

            # Train signal classification model
            if "signal_target" in features_df.columns:
                signal_performance = await self._train_signal_classifier(features_df)
                performance_results["signal_classifier"] = signal_performance

            # Train risk classification model
            if "risk_target" in features_df.columns:
                risk_performance = await self._train_risk_classifier(features_df)
                performance_results["risk_classifier"] = risk_performance

            # Update training timestamp
            model_key = user_id or "global"
            self.last_training_time[model_key] = datetime.utcnow()

            # Save models to disk
            await self._save_models(model_key)

            logger.info(f"Model training completed. Performance: {performance_results}")
            return performance_results

        except Exception as e:
            logger.error(f"Error in model training: {e}")
            return {}

    async def _collect_training_data(self, db: AsyncIOMotorDatabase, user_id: Optional[str]) -> list[dict]:
        """Collect historical trading data for training"""
        try:
            training_data = []

            # Get date range for training data
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=settings.learning_data_lookback_days)

            # Collect trade data
            if user_id:
                positions = await get_user_positions(db, user_id)
            else:
                # Get global data - this would need to be implemented
                positions = []  # For now, user-specific only

            # Collect market analysis data
            symbols = ["R_10", "R_25", "R_50", "R_75", "R_100", "BOOM_1000", "CRASH_1000"]

            for symbol in symbols:
                try:
                    analyses = await get_market_analysis_history(db, symbol, limit=1000)

                    for analysis in analyses:
                        if analysis.timestamp >= start_date:
                            # Find corresponding trades
                            related_trades = [
                                pos for pos in positions
                                if pos.symbol == symbol and
                                   abs((pos.created_at - analysis.timestamp).total_seconds()) < 3600  # Within 1 hour
                            ]

                            training_data.append({
                                "symbol": symbol,
                                "timestamp": analysis.timestamp,
                                "analysis": analysis,
                                "trades": related_trades
                            })
                except Exception as e:
                    logger.warning(f"Error collecting data for {symbol}: {e}")

            logger.info(f"Collected {len(training_data)} training samples")
            return training_data

        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            return []

    async def _prepare_features(self, training_data: list[dict]) -> pd.DataFrame:
        """Prepare features for ML training"""
        try:
            features_list = []

            for sample in training_data:
                analysis = sample["analysis"]
                trades = sample["trades"]

                # Basic features from analysis
                features = {
                    "symbol": sample["symbol"],
                    "hour": sample["timestamp"].hour,
                    "day_of_week": sample["timestamp"].weekday(),
                    "rsi": analysis.rsi or 50.0,
                    "macd": analysis.macd or 0.0,
                    "bollinger_upper": analysis.bollinger_upper or 0.0,
                    "bollinger_lower": analysis.bollinger_lower or 0.0,
                    "volatility": analysis.volatility or 0.2,
                    "current_price": analysis.current_price,
                    "confidence": analysis.confidence or 0.5
                }

                # Price movement features
                if analysis.price_history and len(analysis.price_history) >= 10:
                    prices = analysis.price_history[-10:]
                    features.update({
                        "price_change_1": (prices[-1] - prices[-2]) / prices[-2] if len(prices) >= 2 else 0,
                        "price_change_5": (prices[-1] - prices[-5]) / prices[-5] if len(prices) >= 5 else 0,
                        "price_change_10": (prices[-1] - prices[-10]) / prices[-10] if len(prices) >= 10 else 0,
                        "price_std": np.std(prices),
                        "price_mean": np.mean(prices)
                    })
                else:
                    features.update({
                        "price_change_1": 0,
                        "price_change_5": 0,
                        "price_change_10": 0,
                        "price_std": 0,
                        "price_mean": analysis.current_price
                    })

                # Target variables based on actual trade outcomes
                if trades:
                    # Calculate success metrics
                    profitable_trades = [t for t in trades if t.profit_loss and t.profit_loss > 0]
                    total_profit = sum(t.profit_loss for t in trades if t.profit_loss)

                    features.update({
                        "trend_target": self._determine_trend_target(analysis.trend or "sideways"),
                        "signal_target": self._determine_signal_target(trades),
                        "risk_target": self._determine_risk_target(trades, total_profit),
                        "success_rate": len(profitable_trades) / len(trades) if trades else 0,
                        "avg_profit": total_profit / len(trades) if trades else 0
                    })
                else:
                    # No trades - neutral targets
                    features.update({
                        "trend_target": 1,  # sideways
                        "signal_target": 2,  # hold
                        "risk_target": 1,   # medium risk
                        "success_rate": 0,
                        "avg_profit": 0
                    })

                features_list.append(features)

            # Convert to DataFrame
            df = pd.DataFrame(features_list)

            # Handle missing values
            df = df.fillna(0)

            logger.info(f"Prepared features DataFrame with shape: {df.shape}")
            return df

        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return pd.DataFrame()

    def _determine_trend_target(self, trend: str) -> int:
        """Convert trend to numerical target"""
        trend_map = {
            "strong_bullish": 3,
            "bullish": 2,
            "sideways": 1,
            "bearish": 0,
            "strong_bearish": -1
        }
        return trend_map.get(trend, 1)

    def _determine_signal_target(self, trades: list) -> int:
        """Determine signal target based on trade outcomes"""
        if not trades:
            return 2  # hold

        # Analyze trade types and success
        call_trades = [t for t in trades if t.contract_type == "CALL"]
        put_trades = [t for t in trades if t.contract_type == "PUT"]

        call_profit = sum(t.profit_loss for t in call_trades if t.profit_loss and t.profit_loss > 0)
        put_profit = sum(t.profit_loss for t in put_trades if t.profit_loss and t.profit_loss > 0)

        if call_profit > put_profit and call_profit > 0:
            return 1  # buy_call
        elif put_profit > call_profit and put_profit > 0:
            return 0  # buy_put
        else:
            return 2  # hold

    def _determine_risk_target(self, trades: list, total_profit: float) -> int:
        """Determine risk target based on trade outcomes"""
        if not trades:
            return 1  # medium

        # Calculate risk based on profit volatility and drawdown
        profits = [t.profit_loss for t in trades if t.profit_loss is not None]

        if not profits:
            return 1

        profit_std = np.std(profits)
        max_loss = min(profits) if profits else 0

        # High risk if high volatility or large losses
        if profit_std > 20 or max_loss < -50:
            return 2  # high risk
        elif profit_std < 10 and max_loss > -20:
            return 0  # low risk
        else:
            return 1  # medium risk

    async def _train_trend_classifier(self, features_df: pd.DataFrame) -> ModelPerformance:
        """Train trend classification model"""
        try:
            # Prepare features and target
            feature_cols = [col for col in features_df.columns if col not in ["trend_target", "signal_target", "risk_target", "symbol"]]
            X = features_df[feature_cols]
            y = features_df["trend_target"]

            # Encode categorical variables
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

            # Train model
            model = self.model_configs["trend_classifier"]
            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_test)
            performance = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
                "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
                "f1": f1_score(y_test, y_pred, average="weighted", zero_division=0),
                "cross_val_score": cross_val_score(model, X_scaled, y, cv=5).mean(),
                "feature_importance": dict(zip(feature_cols, model.feature_importances_)) if hasattr(model, "feature_importances_") else {}
            }

            # Store model and scaler
            self.models["trend_classifier"] = model
            self.scalers["trend_classifier"] = scaler
            self.model_performance["trend_classifier"] = performance

            logger.info(f"Trend classifier trained. Accuracy: {performance['accuracy']:.3f}")
            return performance

        except Exception as e:
            logger.error(f"Error training trend classifier: {e}")
            return {}

    async def _train_signal_classifier(self, features_df: pd.DataFrame) -> ModelPerformance:
        """Train signal classification model"""
        try:
            # Similar to trend classifier but for signals
            feature_cols = [col for col in features_df.columns if col not in ["trend_target", "signal_target", "risk_target", "symbol"]]
            X = features_df[feature_cols]
            y = features_df["signal_target"]

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

            model = self.model_configs["signal_classifier"]
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)
            performance = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
                "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
                "f1": f1_score(y_test, y_pred, average="weighted", zero_division=0),
                "cross_val_score": cross_val_score(model, X_scaled, y, cv=5).mean(),
                "feature_importance": dict(zip(feature_cols, model.feature_importances_)) if hasattr(model, "feature_importances_") else {}
            }

            self.models["signal_classifier"] = model
            self.scalers["signal_classifier"] = scaler
            self.model_performance["signal_classifier"] = performance

            logger.info(f"Signal classifier trained. Accuracy: {performance['accuracy']:.3f}")
            return performance

        except Exception as e:
            logger.error(f"Error training signal classifier: {e}")
            return {}

    async def _train_risk_classifier(self, features_df: pd.DataFrame) -> ModelPerformance:
        """Train risk classification model"""
        try:
            feature_cols = [col for col in features_df.columns if col not in ["trend_target", "signal_target", "risk_target", "symbol"]]
            X = features_df[feature_cols]
            y = features_df["risk_target"]

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

            model = self.model_configs["risk_classifier"]
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)
            performance = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
                "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
                "f1": f1_score(y_test, y_pred, average="weighted", zero_division=0),
                "cross_val_score": cross_val_score(model, X_scaled, y, cv=5).mean(),
                "feature_importance": dict(zip(feature_cols, model.feature_importances_)) if hasattr(model, "feature_importances_") else {}
            }

            self.models["risk_classifier"] = model
            self.scalers["risk_classifier"] = scaler
            self.model_performance["risk_classifier"] = performance

            logger.info(f"Risk classifier trained. Accuracy: {performance['accuracy']:.3f}")
            return performance

        except Exception as e:
            logger.error(f"Error training risk classifier: {e}")
            return {}

    async def predict_trend(self, features: dict[str, Any]) -> tuple[str, float]:
        """Predict market trend using trained model"""
        try:
            if "trend_classifier" not in self.models:
                return "sideways", 0.5

            model = self.models["trend_classifier"]
            scaler = self.scalers["trend_classifier"]

            # Prepare features
            feature_vector = self._prepare_prediction_features(features)
            feature_scaled = scaler.transform([feature_vector])

            # Predict
            prediction = model.predict(feature_scaled)[0]
            confidence = max(model.predict_proba(feature_scaled)[0])

            # Convert back to trend string
            trend_map = {3: "strong_bullish", 2: "bullish", 1: "sideways", 0: "bearish", -1: "strong_bearish"}
            trend = trend_map.get(prediction, "sideways")

            return trend, confidence

        except Exception as e:
            logger.error(f"Error predicting trend: {e}")
            return "sideways", 0.5

    async def predict_signal(self, features: dict[str, Any]) -> tuple[str, float]:
        """Predict trading signal using trained model"""
        try:
            if "signal_classifier" not in self.models:
                return "HOLD", 0.5

            model = self.models["signal_classifier"]
            scaler = self.scalers["signal_classifier"]

            feature_vector = self._prepare_prediction_features(features)
            feature_scaled = scaler.transform([feature_vector])

            prediction = model.predict(feature_scaled)[0]
            confidence = max(model.predict_proba(feature_scaled)[0])

            signal_map = {1: "BUY_CALL", 0: "BUY_PUT", 2: "HOLD"}
            signal = signal_map.get(prediction, "HOLD")

            return signal, confidence

        except Exception as e:
            logger.error(f"Error predicting signal: {e}")
            return "HOLD", 0.5

    async def predict_risk(self, features: dict[str, Any]) -> tuple[str, float]:
        """Predict risk level using trained model"""
        try:
            if "risk_classifier" not in self.models:
                return "medium", 0.5

            model = self.models["risk_classifier"]
            scaler = self.scalers["risk_classifier"]

            feature_vector = self._prepare_prediction_features(features)
            feature_scaled = scaler.transform([feature_vector])

            prediction = model.predict(feature_scaled)[0]
            confidence = max(model.predict_proba(feature_scaled)[0])

            risk_map = {0: "low", 1: "medium", 2: "high"}
            risk = risk_map.get(prediction, "medium")

            return risk, confidence

        except Exception as e:
            logger.error(f"Error predicting risk: {e}")
            return "medium", 0.5

    def _prepare_prediction_features(self, features: dict[str, Any]) -> list[float]:
        """Prepare features for prediction"""
        # Extract expected features in correct order
        expected_features = [
            "hour", "day_of_week", "rsi", "macd", "bollinger_upper", "bollinger_lower",
            "volatility", "current_price", "confidence", "price_change_1", "price_change_5",
            "price_change_10", "price_std", "price_mean", "success_rate", "avg_profit"
        ]

        feature_vector = []
        for feature in expected_features:
            value = features.get(feature, 0)
            feature_vector.append(float(value) if value is not None else 0.0)

        return feature_vector

    async def _save_models(self, model_key: str):
        """Save trained models to disk"""
        try:
            import os
            os.makedirs("models", exist_ok=True)

            for model_name, model in self.models.items():
                joblib.dump(model, f"models/{model_key}_{model_name}.pkl")

            for scaler_name, scaler in self.scalers.items():
                joblib.dump(scaler, f"models/{model_key}_{scaler_name}_scaler.pkl")

            # Save performance metrics
            with open(f"models/{model_key}_performance.json", "w") as f:
                json.dump(self.model_performance, f, indent=2, default=str)

            logger.info(f"Models saved for {model_key}")

        except Exception as e:
            logger.error(f"Error saving models: {e}")

    async def load_models(self, model_key: str) -> bool:
        """Load trained models from disk"""
        try:
            import os

            model_files = {
                "trend_classifier": f"models/{model_key}_trend_classifier.pkl",
                "signal_classifier": f"models/{model_key}_signal_classifier.pkl",
                "risk_classifier": f"models/{model_key}_risk_classifier.pkl"
            }

            scaler_files = {
                "trend_classifier": f"models/{model_key}_trend_classifier_scaler.pkl",
                "signal_classifier": f"models/{model_key}_signal_classifier_scaler.pkl",
                "risk_classifier": f"models/{model_key}_risk_classifier_scaler.pkl"
            }

            # Load models
            for model_name, file_path in model_files.items():
                if os.path.exists(file_path):
                    self.models[model_name] = joblib.load(file_path)

            # Load scalers
            for scaler_name, file_path in scaler_files.items():
                if os.path.exists(file_path):
                    self.scalers[scaler_name] = joblib.load(file_path)

            # Load performance metrics
            perf_file = f"models/{model_key}_performance.json"
            if os.path.exists(perf_file):
                with open(perf_file) as f:
                    self.model_performance = json.load(f)

            logger.info(f"Models loaded for {model_key}: {list(self.models.keys())}")
            return len(self.models) > 0

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return False

    def should_retrain(self, model_key: str) -> bool:
        """Check if models should be retrained"""
        if model_key not in self.last_training_time:
            return True

        time_since_training = datetime.utcnow() - self.last_training_time[model_key]
        return time_since_training.total_seconds() > settings.retrain_interval_hours * 3600

    def get_model_performance(self) -> dict[str, ModelPerformance]:
        """Get current model performance metrics"""
        return self.model_performance.copy()

    async def analyze_trading_patterns(self, db: AsyncIOMotorDatabase, user_id: str) -> dict[str, Any]:
        """Analyze user trading patterns for insights"""
        try:
            # Get user trade history
            positions = await get_user_positions(db, user_id)

            if not positions:
                return {"message": "No trading history available"}

            # Analyze patterns
            patterns = {
                "total_trades": len(positions),
                "profitable_trades": len([p for p in positions if p.profit_loss and p.profit_loss > 0]),
                "losing_trades": len([p for p in positions if p.profit_loss and p.profit_loss < 0]),
                "total_profit": sum(p.profit_loss for p in positions if p.profit_loss),
                "avg_profit_per_trade": np.mean([p.profit_loss for p in positions if p.profit_loss]) if positions else 0,
                "best_trade": max([p.profit_loss for p in positions if p.profit_loss], default=0),
                "worst_trade": min([p.profit_loss for p in positions if p.profit_loss], default=0),
            }

            # Win rate
            if patterns["total_trades"] > 0:
                patterns["win_rate"] = patterns["profitable_trades"] / patterns["total_trades"]
            else:
                patterns["win_rate"] = 0

            # Symbol analysis
            symbol_performance = {}
            for position in positions:
                symbol = position.symbol
                if symbol not in symbol_performance:
                    symbol_performance[symbol] = {"trades": 0, "profit": 0}
                symbol_performance[symbol]["trades"] += 1
                if position.profit_loss:
                    symbol_performance[symbol]["profit"] += float(position.profit_loss)

            patterns["symbol_performance"] = symbol_performance

            # Time analysis
            trade_hours = [p.created_at.hour for p in positions]
            if trade_hours:
                patterns["most_active_hour"] = max(set(trade_hours), key=trade_hours.count)
                patterns["hourly_distribution"] = {h: trade_hours.count(h) for h in range(24)}

            logger.info(f"Trading patterns analyzed for user {user_id}")
            return patterns

        except Exception as e:
            logger.error(f"Error analyzing trading patterns: {e}")
            return {"error": str(e)}
