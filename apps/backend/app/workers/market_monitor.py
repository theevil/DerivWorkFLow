"""
Market Monitor Worker for continuous market analysis and signal generation
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import redis

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from app.core.database import get_database_sync
from app.ai.market_analyzer import AdvancedMarketAnalyzer
from app.ai.decision_engine import TradingDecisionEngine
from app.ai.risk_manager import AIRiskManager
from app.core.ai_analysis import EnhancedTradingSignalGenerator
from app.crud.trading import get_all_active_users, get_user_trading_parameters, get_user_positions
from app.workers.celery_app import celery_app


class MarketMonitorWorker:
    """
    Continuous market monitoring and analysis worker
    """
    
    def __init__(self):
        """Initialize the market monitor worker"""
        self.redis_client = redis.from_url(settings.redis_url)
        self.enhanced_generator = EnhancedTradingSignalGenerator()
        self.market_analyzer = AdvancedMarketAnalyzer()
        self.risk_manager = AIRiskManager()
        
        # Market data cache
        self.market_cache = {}
        self.last_analysis = {}
        
        # Symbols to monitor
        self.symbols = [
            "R_10", "R_25", "R_50", "R_75", "R_100",
            "BOOM_1000", "CRASH_1000", "STEP_10", "STEP_25"
        ]
        
        logger.info("Market Monitor Worker initialized")
    
    async def scan_markets(self) -> Dict[str, Any]:
        """
        Scan all markets for opportunities
        
        Returns:
            Dictionary with scan results
        """
        try:
            scan_results = {
                "timestamp": datetime.utcnow(),
                "symbols_scanned": 0,
                "signals_generated": 0,
                "opportunities": [],
                "errors": []
            }
            
            # Get current market data for all symbols
            market_data = await self._fetch_market_data()
            
            for symbol in self.symbols:
                try:
                    symbol_data = market_data.get(symbol)
                    if not symbol_data:
                        continue
                    
                    scan_results["symbols_scanned"] += 1
                    
                    # Analyze market for this symbol
                    opportunity = await self._analyze_symbol_opportunity(symbol, symbol_data)
                    
                    if opportunity:
                        scan_results["opportunities"].append(opportunity)
                        
                        # Generate signals for eligible users
                        signals = await self._generate_signals_for_symbol(symbol, symbol_data, opportunity)
                        scan_results["signals_generated"] += len(signals)
                
                except Exception as e:
                    logger.error(f"Error scanning symbol {symbol}: {e}")
                    scan_results["errors"].append(f"{symbol}: {str(e)}")
            
            logger.info(f"Market scan completed: {scan_results['symbols_scanned']} symbols, "
                       f"{scan_results['signals_generated']} signals generated")
            
            return scan_results
            
        except Exception as e:
            logger.error(f"Error in market scan: {e}")
            return {"error": str(e), "timestamp": datetime.utcnow()}
    
    async def _fetch_market_data(self) -> Dict[str, Dict]:
        """Fetch current market data for all symbols"""
        market_data = {}
        
        try:
            # In a real implementation, this would fetch from Deriv API
            # For now, we'll simulate market data
            for symbol in self.symbols:
                # Check cache first
                cache_key = f"market_data:{symbol}"
                cached_data = self.redis_client.get(cache_key)
                
                if cached_data:
                    import json
                    market_data[symbol] = json.loads(cached_data)
                else:
                    # Generate simulated market data
                    simulated_data = self._generate_simulated_data(symbol)
                    market_data[symbol] = simulated_data
                    
                    # Cache for 30 seconds
                    self.redis_client.setex(
                        cache_key, 
                        30, 
                        json.dumps(simulated_data, default=str)
                    )
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return {}
    
    def _generate_simulated_data(self, symbol: str) -> Dict:
        """Generate simulated market data for testing"""
        import random
        import numpy as np
        
        # Get base price for symbol
        base_prices = {
            "R_10": 1.0,
            "R_25": 2.5,
            "R_50": 5.0,
            "R_75": 7.5,
            "R_100": 10.0,
            "BOOM_1000": 1000.0,
            "CRASH_1000": 1000.0,
            "STEP_10": 10.0,
            "STEP_25": 25.0
        }
        
        base_price = base_prices.get(symbol, 1.0)
        
        # Generate price history (last 50 ticks)
        price_history = []
        current_price = base_price
        
        for i in range(50):
            # Add random walk with slight trend
            change = random.gauss(0, 0.001) + (0.0001 if random.random() > 0.5 else -0.0001)
            current_price += change
            price_history.append(max(0.001, current_price))  # Ensure positive prices
        
        return {
            "symbol": symbol,
            "current_price": price_history[-1],
            "price_history": price_history,
            "volatility": np.std(price_history[-20:]) if len(price_history) >= 20 else 0.1,
            "timestamp": datetime.utcnow(),
            "volume": random.randint(100, 1000),
            "bid": price_history[-1] * 0.999,
            "ask": price_history[-1] * 1.001
        }
    
    async def _analyze_symbol_opportunity(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """Analyze a symbol for trading opportunities"""
        try:
            # Perform market analysis
            analysis = await self.market_analyzer.analyze_market_advanced(
                symbol=symbol,
                price_history=market_data["price_history"],
                current_price=market_data["current_price"],
                market_context={
                    "volatility": market_data.get("volatility", 0.1),
                    "volume": market_data.get("volume", 500),
                    "session": "active"
                }
            )
            
            # Check if this is a significant opportunity
            if (analysis.confidence_score >= 0.7 and 
                analysis.recommended_action != "hold" and
                analysis.risk_level in ["low", "medium"]):
                
                return {
                    "symbol": symbol,
                    "analysis": analysis,
                    "market_data": market_data,
                    "opportunity_score": analysis.confidence_score,
                    "recommended_action": analysis.recommended_action,
                    "risk_level": analysis.risk_level
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing opportunity for {symbol}: {e}")
            return None
    
    async def _generate_signals_for_symbol(
        self, 
        symbol: str, 
        market_data: Dict, 
        opportunity: Dict
    ) -> List[str]:
        """Generate trading signals for eligible users"""
        signals_generated = []
        
        try:
            # Get database connection
            db = await get_database_sync()
            
            # Get all active users with trading parameters
            active_users = await self._get_eligible_users(db)
            
            for user_data in active_users:
                try:
                    user_id = user_data["user_id"]
                    trading_params = user_data["trading_params"]
                    positions = user_data["positions"]
                    
                    # Check if user is eligible for new signals
                    if not await self._is_user_eligible_for_signal(user_id, symbol, positions, trading_params):
                        continue
                    
                    # Generate AI signal
                    user_context = {
                        "account_balance": 1000,  # Would be fetched from user account
                        "risk_tolerance": "medium",  # Would be stored in user profile
                        "experience_level": "intermediate",  # Would be stored in user profile
                        "max_daily_loss": trading_params.max_daily_loss,
                        "max_position_size": trading_params.position_size
                    }
                    
                    signal = await self.enhanced_generator.generate_ai_signal(
                        user_id=user_id,
                        symbol=symbol,
                        price_history=market_data["price_history"],
                        current_price=market_data["current_price"],
                        user_context=user_context,
                        account_balance=user_context["account_balance"],
                        current_positions=positions
                    )
                    
                    if signal:
                        # Queue signal for execution
                        await self._queue_signal_for_execution(signal, user_context)
                        signals_generated.append(user_id)
                        
                        logger.info(f"Signal generated for user {user_id}, symbol {symbol}: {signal.signal_type}")
                
                except Exception as e:
                    logger.error(f"Error generating signal for user {user_data.get('user_id', 'unknown')}: {e}")
            
            return signals_generated
            
        except Exception as e:
            logger.error(f"Error generating signals for symbol {symbol}: {e}")
            return []
    
    async def _get_eligible_users(self, db: AsyncIOMotorDatabase) -> List[Dict]:
        """Get all users eligible for trading signals"""
        try:
            eligible_users = []
            
            # Get all users with trading parameters (simplified query)
            # In a real implementation, this would be a proper database query
            users_cursor = db.users.find({"active": {"$ne": False}})
            
            async for user in users_cursor:
                user_id = str(user["_id"])
                
                # Get trading parameters
                trading_params = await get_user_trading_parameters(db, user_id)
                if not trading_params:
                    continue
                
                # Get current positions
                positions = await get_user_positions(db, user_id, "open")
                
                # Check if auto trading is enabled for user
                # This would be stored in user preferences
                auto_trading_enabled = user.get("auto_trading_enabled", False)
                if not auto_trading_enabled and not settings.auto_trading_enabled:
                    continue
                
                eligible_users.append({
                    "user_id": user_id,
                    "trading_params": trading_params,
                    "positions": positions,
                    "user_profile": user
                })
            
            return eligible_users
            
        except Exception as e:
            logger.error(f"Error getting eligible users: {e}")
            return []
    
    async def _is_user_eligible_for_signal(
        self, 
        user_id: str, 
        symbol: str, 
        positions: List, 
        trading_params
    ) -> bool:
        """Check if user is eligible for a new signal"""
        try:
            # Check position limits
            open_positions = len([p for p in positions if p.status == "open"])
            if open_positions >= settings.max_concurrent_positions:
                return False
            
            # Check if user already has position in this symbol
            symbol_positions = [p for p in positions if p.symbol == symbol and p.status == "open"]
            if len(symbol_positions) > 0:
                return False  # One position per symbol
            
            # Check daily loss limits
            today = datetime.utcnow().date()
            daily_positions = [p for p in positions if p.created_at.date() == today]
            daily_pnl = sum(p.profit_loss or 0 for p in daily_positions)
            
            if daily_pnl <= -trading_params.max_daily_loss * 0.8:
                return False  # Close to daily loss limit
            
            # Check if user had recent signal for this symbol
            recent_signals_key = f"recent_signals:{user_id}:{symbol}"
            if self.redis_client.exists(recent_signals_key):
                return False  # Too recent
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking user eligibility: {e}")
            return False
    
    async def _queue_signal_for_execution(self, signal, user_context: Dict):
        """Queue trading signal for execution"""
        try:
            from app.workers.tasks import process_signal
            
            # Create signal data for task
            signal_data = {
                "user_id": signal.user_id,
                "symbol": signal.symbol,
                "signal_type": signal.signal_type,
                "recommended_amount": signal.recommended_amount,
                "recommended_duration": signal.recommended_duration,
                "confidence": signal.confidence,
                "reasoning": signal.reasoning,
                "user_context": user_context,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Queue the signal processing task
            task = process_signal.apply_async(
                args=[signal_data],
                countdown=settings.signal_execution_delay_seconds,
                queue="signals"
            )
            
            # Mark that user had recent signal for this symbol
            recent_signals_key = f"recent_signals:{signal.user_id}:{signal.symbol}"
            self.redis_client.setex(recent_signals_key, 300, "1")  # 5 minutes
            
            logger.info(f"Signal queued for execution: {task.id}")
            
        except Exception as e:
            logger.error(f"Error queueing signal: {e}")
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market monitoring status"""
        try:
            status = {
                "active": True,
                "symbols_monitored": len(self.symbols),
                "last_scan": self.last_analysis.get("timestamp"),
                "cache_status": {},
                "redis_connected": self.redis_client.ping(),
                "monitoring_intervals": {
                    "market_scan": settings.market_scan_interval_seconds,
                    "position_monitor": settings.position_monitor_interval_seconds
                }
            }
            
            # Check cache status for each symbol
            for symbol in self.symbols:
                cache_key = f"market_data:{symbol}"
                status["cache_status"][symbol] = self.redis_client.exists(cache_key)
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            return {"active": False, "error": str(e)}


# Create global instance
market_monitor = MarketMonitorWorker()
