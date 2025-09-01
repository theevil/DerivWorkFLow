"""
Celery tasks for background processing
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

from app.workers.celery_app import celery_app
from app.workers.market_monitor import market_monitor
from app.workers.trading_executor import trading_executor
from app.core.config import settings


def run_async(coro):
    """Helper to run async functions in Celery tasks"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, name="app.workers.tasks.market_scan_scheduler")
def market_scan_scheduler(self):
    """Scheduled task for market scanning"""
    try:
        logger.info("Starting scheduled market scan")
        result = run_async(market_monitor.scan_markets())
        logger.info(f"Market scan completed: {result.get('symbols_scanned', 0)} symbols scanned")
        return result
    except Exception as e:
        logger.error(f"Error in market scan scheduler: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="app.workers.tasks.position_monitor_scheduler")
def position_monitor_scheduler(self):
    """Scheduled task for position monitoring"""
    try:
        logger.debug("Starting position monitoring cycle")
        
        # Get all active positions that need monitoring
        active_positions = run_async(_get_active_positions_for_monitoring())
        
        results = []
        for position_data in active_positions:
            try:
                result = run_async(
                    trading_executor.monitor_position(
                        position_data["position_id"],
                        position_data["user_id"]
                    )
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error monitoring position {position_data['position_id']}: {e}")
        
        return {
            "positions_monitored": len(results),
            "timestamp": datetime.utcnow().isoformat(),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in position monitor scheduler: {e}")
        raise self.retry(exc=e, countdown=30, max_retries=5)


@celery_app.task(bind=True, name="app.workers.tasks.risk_monitor_scheduler")
def risk_monitor_scheduler(self):
    """Scheduled task for risk monitoring"""
    try:
        logger.info("Starting risk monitoring cycle")
        
        # Get all users with active positions
        users_with_positions = run_async(_get_users_with_active_positions())
        
        risk_alerts = []
        for user_data in users_with_positions:
            try:
                risk_status = run_async(_check_user_risk_status(user_data))
                if risk_status.get("alert_required"):
                    risk_alerts.append(risk_status)
            except Exception as e:
                logger.error(f"Error checking risk for user {user_data.get('user_id')}: {e}")
        
        return {
            "users_checked": len(users_with_positions),
            "risk_alerts": len(risk_alerts),
            "alerts": risk_alerts,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in risk monitor scheduler: {e}")
        raise self.retry(exc=e, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="app.workers.tasks.process_signal")
def process_signal(self, signal_data: Dict[str, Any]):
    """Process a trading signal for execution"""
    try:
        logger.info(f"Processing signal for user {signal_data['user_id']}, symbol {signal_data['symbol']}")
        
        # Execute the trading signal
        result = run_async(trading_executor.execute_trade_signal(signal_data))
        
        if result["success"]:
            logger.info(f"Signal executed successfully: {result['trade_id']}")
        else:
            logger.warning(f"Signal execution failed: {result['reason']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing signal: {e}")
        raise self.retry(exc=e, countdown=30, max_retries=3)


@celery_app.task(bind=True, name="app.workers.tasks.monitor_position")
def monitor_position(self, position_id: str, user_id: str):
    """Monitor a specific trading position"""
    try:
        logger.debug(f"Monitoring position {position_id} for user {user_id}")
        
        result = run_async(trading_executor.monitor_position(position_id, user_id))
        
        return result
        
    except Exception as e:
        logger.error(f"Error monitoring position {position_id}: {e}")
        raise self.retry(exc=e, countdown=30, max_retries=5)


@celery_app.task(bind=True, name="app.workers.tasks.model_retrain_scheduler")
def model_retrain_scheduler(self):
    """Scheduled task for AI model retraining"""
    try:
        logger.info("Starting model retraining check")
        
        # Check which users need model retraining
        users_needing_retrain = run_async(_get_users_needing_retrain())
        
        retrain_results = []
        for user_id in users_needing_retrain:
            try:
                # Start retraining for user
                retrain_task = retrain_user_models.delay(user_id)
                retrain_results.append({
                    "user_id": user_id,
                    "task_id": retrain_task.id,
                    "status": "started"
                })
            except Exception as e:
                logger.error(f"Error starting retrain for user {user_id}: {e}")
                retrain_results.append({
                    "user_id": user_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "users_checked": len(users_needing_retrain),
            "retraining_started": len([r for r in retrain_results if r["status"] == "started"]),
            "results": retrain_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in model retrain scheduler: {e}")
        raise self.retry(exc=e, countdown=3600, max_retries=3)  # Retry in 1 hour


@celery_app.task(bind=True, name="app.workers.tasks.retrain_user_models")
def retrain_user_models(self, user_id: str):
    """Retrain AI models for a specific user"""
    try:
        logger.info(f"Starting model retraining for user {user_id}")
        
        from app.ai.learning_system import HistoricalLearningSystem
        from app.core.database import get_database_sync
        
        learning_system = HistoricalLearningSystem()
        db = run_async(get_database_sync())
        
        # Train models for user
        performance = run_async(learning_system.train_models(db, user_id))
        
        logger.info(f"Model retraining completed for user {user_id}")
        
        return {
            "user_id": user_id,
            "performance": performance,
            "timestamp": datetime.utcnow().isoformat(),
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error retraining models for user {user_id}: {e}")
        raise self.retry(exc=e, countdown=1800, max_retries=2)  # Retry in 30 minutes


@celery_app.task(bind=True, name="app.workers.tasks.daily_portfolio_analysis")
def daily_portfolio_analysis(self):
    """Daily portfolio analysis for all users"""
    try:
        logger.info("Starting daily portfolio analysis")
        
        users_with_trading = run_async(_get_all_trading_users())
        
        analysis_results = []
        for user_data in users_with_trading:
            try:
                analysis = run_async(_analyze_user_portfolio(user_data))
                analysis_results.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing portfolio for user {user_data.get('user_id')}: {e}")
        
        return {
            "users_analyzed": len(analysis_results),
            "timestamp": datetime.utcnow().isoformat(),
            "analyses": analysis_results
        }
        
    except Exception as e:
        logger.error(f"Error in daily portfolio analysis: {e}")
        raise self.retry(exc=e, countdown=3600, max_retries=2)


@celery_app.task(bind=True, name="app.workers.tasks.weekly_performance_review")
def weekly_performance_review(self):
    """Weekly performance review and optimization"""
    try:
        logger.info("Starting weekly performance review")
        
        # Analyze overall system performance
        performance_data = run_async(_analyze_system_performance())
        
        # Generate performance report
        report = {
            "week_ending": datetime.utcnow().isoformat(),
            "total_trades": performance_data.get("total_trades", 0),
            "success_rate": performance_data.get("success_rate", 0),
            "total_profit": performance_data.get("total_profit", 0),
            "active_users": performance_data.get("active_users", 0),
            "model_performance": performance_data.get("model_performance", {}),
            "recommendations": performance_data.get("recommendations", [])
        }
        
        logger.info(f"Weekly performance review completed: {report['total_trades']} trades analyzed")
        
        return report
        
    except Exception as e:
        logger.error(f"Error in weekly performance review: {e}")
        raise self.retry(exc=e, countdown=7200, max_retries=2)  # Retry in 2 hours


@celery_app.task(bind=True, name="app.workers.tasks.emergency_stop")
def emergency_stop(self, user_id: str, reason: str):
    """Emergency stop trading for a user"""
    try:
        logger.warning(f"Emergency stop triggered for user {user_id}: {reason}")
        
        # Close all open positions for user
        closed_positions = run_async(_emergency_close_positions(user_id))
        
        # Disable auto trading for user
        run_async(_disable_auto_trading(user_id))
        
        # Send alert notification
        run_async(_send_emergency_alert(user_id, reason, closed_positions))
        
        return {
            "user_id": user_id,
            "reason": reason,
            "positions_closed": len(closed_positions),
            "timestamp": datetime.utcnow().isoformat(),
            "auto_trading_disabled": True
        }
        
    except Exception as e:
        logger.error(f"Error in emergency stop for user {user_id}: {e}")
        # Don't retry emergency stops - they need to be immediate
        return {
            "user_id": user_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "success": False
        }


# Helper functions (async)

async def _get_active_positions_for_monitoring() -> List[Dict]:
    """Get all active positions that need monitoring"""
    try:
        from app.core.database import get_database_sync
        from app.crud.trading import get_all_open_positions
        
        db = await get_database_sync()
        positions = await get_all_open_positions(db)
        
        return [
            {
                "position_id": str(pos.id),
                "user_id": pos.user_id,
                "symbol": pos.symbol,
                "created_at": pos.created_at
            }
            for pos in positions
        ]
        
    except Exception as e:
        logger.error(f"Error getting active positions: {e}")
        return []


async def _get_users_with_active_positions() -> List[Dict]:
    """Get all users with active positions"""
    try:
        from app.core.database import get_database_sync
        
        db = await get_database_sync()
        
        # Aggregate query to get users with open positions
        pipeline = [
            {"$match": {"status": "open"}},
            {"$group": {
                "_id": "$user_id",
                "position_count": {"$sum": 1},
                "total_exposure": {"$sum": "$amount"},
                "positions": {"$push": "$$ROOT"}
            }}
        ]
        
        users_with_positions = []
        async for result in db.trade_positions.aggregate(pipeline):
            users_with_positions.append({
                "user_id": str(result["_id"]),
                "position_count": result["position_count"],
                "total_exposure": result["total_exposure"],
                "positions": result["positions"]
            })
        
        return users_with_positions
        
    except Exception as e:
        logger.error(f"Error getting users with positions: {e}")
        return []


async def _check_user_risk_status(user_data: Dict) -> Dict:
    """Check risk status for a user"""
    try:
        from app.ai.risk_manager import AIRiskManager
        from app.crud.trading import get_user_trading_parameters
        from app.core.database import get_database_sync
        
        risk_manager = AIRiskManager()
        db = await get_database_sync()
        
        user_id = user_data["user_id"]
        trading_params = await get_user_trading_parameters(db, user_id)
        
        if not trading_params:
            return {"user_id": user_id, "alert_required": False}
        
        # Assess portfolio risk
        portfolio_risk = await risk_manager.assess_portfolio_risk(
            positions=user_data["positions"],
            account_balance=1000,  # Would be fetched from user account
            trading_params=trading_params
        )
        
        # Check if halt trading is needed
        daily_pnl = sum(pos.get("profit_loss", 0) for pos in user_data["positions"])
        should_halt, halt_reason = risk_manager.should_halt_trading(
            portfolio_risk, daily_pnl, trading_params.max_daily_loss
        )
        
        if should_halt:
            # Trigger emergency stop
            emergency_stop.delay(user_id, halt_reason)
        
        return {
            "user_id": user_id,
            "alert_required": should_halt,
            "risk_score": portfolio_risk.overall_risk_score,
            "halt_reason": halt_reason if should_halt else None,
            "portfolio_risk": portfolio_risk.dict() if hasattr(portfolio_risk, 'dict') else {}
        }
        
    except Exception as e:
        logger.error(f"Error checking user risk status: {e}")
        return {"user_id": user_data.get("user_id"), "alert_required": False, "error": str(e)}


async def _get_users_needing_retrain() -> List[str]:
    """Get users who need model retraining"""
    try:
        from app.ai.learning_system import HistoricalLearningSystem
        from app.core.database import get_database_sync
        
        learning_system = HistoricalLearningSystem()
        db = await get_database_sync()
        
        # Get all users with trading activity
        users_cursor = db.users.find({"active": {"$ne": False}})
        users_needing_retrain = []
        
        async for user in users_cursor:
            user_id = str(user["_id"])
            if learning_system.should_retrain(user_id):
                users_needing_retrain.append(user_id)
        
        return users_needing_retrain
        
    except Exception as e:
        logger.error(f"Error getting users needing retrain: {e}")
        return []


async def _get_all_trading_users() -> List[Dict]:
    """Get all users with trading activity"""
    try:
        from app.core.database import get_database_sync
        
        db = await get_database_sync()
        
        # Get users who have made trades
        pipeline = [
            {"$group": {
                "_id": "$user_id",
                "trade_count": {"$sum": 1},
                "last_trade": {"$max": "$created_at"}
            }},
            {"$match": {"trade_count": {"$gt": 0}}}
        ]
        
        trading_users = []
        async for result in db.trade_positions.aggregate(pipeline):
            trading_users.append({
                "user_id": str(result["_id"]),
                "trade_count": result["trade_count"],
                "last_trade": result["last_trade"]
            })
        
        return trading_users
        
    except Exception as e:
        logger.error(f"Error getting trading users: {e}")
        return []


async def _analyze_user_portfolio(user_data: Dict) -> Dict:
    """Analyze portfolio for a user"""
    try:
        from app.ai.learning_system import HistoricalLearningSystem
        from app.core.database import get_database_sync
        
        learning_system = HistoricalLearningSystem()
        db = await get_database_sync()
        
        user_id = user_data["user_id"]
        patterns = await learning_system.analyze_trading_patterns(db, user_id)
        
        return {
            "user_id": user_id,
            "analysis_date": datetime.utcnow().isoformat(),
            "patterns": patterns
        }
        
    except Exception as e:
        logger.error(f"Error analyzing user portfolio: {e}")
        return {"user_id": user_data.get("user_id"), "error": str(e)}


async def _analyze_system_performance() -> Dict:
    """Analyze overall system performance"""
    try:
        from app.core.database import get_database_sync
        
        db = await get_database_sync()
        
        # Get performance metrics for the last week
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Total trades
        total_trades = await db.trade_positions.count_documents({
            "created_at": {"$gte": week_ago}
        })
        
        # Success rate calculation
        closed_trades = db.trade_positions.find({
            "created_at": {"$gte": week_ago},
            "status": "closed",
            "profit_loss": {"$exists": True}
        })
        
        profitable_trades = 0
        total_profit = 0
        trade_count = 0
        
        async for trade in closed_trades:
            trade_count += 1
            if trade.get("profit_loss", 0) > 0:
                profitable_trades += 1
            total_profit += trade.get("profit_loss", 0)
        
        success_rate = profitable_trades / trade_count if trade_count > 0 else 0
        
        # Active users
        active_users = await db.users.count_documents({
            "last_login": {"$gte": week_ago}
        })
        
        return {
            "total_trades": total_trades,
            "success_rate": success_rate,
            "total_profit": total_profit,
            "active_users": active_users,
            "model_performance": {},  # Would include ML model metrics
            "recommendations": []  # Would include optimization recommendations
        }
        
    except Exception as e:
        logger.error(f"Error analyzing system performance: {e}")
        return {}


async def _emergency_close_positions(user_id: str) -> List[str]:
    """Emergency close all positions for a user"""
    try:
        from app.core.database import get_database_sync
        from app.crud.trading import get_user_positions, update_position
        from app.core.deriv import websocket_manager
        
        db = await get_database_sync()
        
        # Get all open positions
        positions = await get_user_positions(db, user_id, "open")
        closed_positions = []
        
        # Get Deriv connection
        deriv_ws = await websocket_manager.get_connection(user_id)
        
        for position in positions:
            try:
                # Attempt to close via Deriv API
                if deriv_ws and position.contract_id:
                    await deriv_ws.sell_contract(position.contract_id)
                
                # Update position status
                await update_position(
                    db,
                    str(position.id),
                    user_id,
                    {
                        "status": "closed",
                        "exit_time": datetime.utcnow(),
                        "exit_spot": position.current_spot or position.entry_spot
                    }
                )
                
                closed_positions.append(str(position.id))
                
            except Exception as e:
                logger.error(f"Error closing position {position.id}: {e}")
        
        return closed_positions
        
    except Exception as e:
        logger.error(f"Error in emergency close positions: {e}")
        return []


async def _disable_auto_trading(user_id: str):
    """Disable auto trading for a user"""
    try:
        from app.core.database import get_database_sync
        
        db = await get_database_sync()
        
        # Update user settings to disable auto trading
        await db.users.update_one(
            {"_id": user_id},
            {"$set": {"auto_trading_enabled": False, "auto_trading_disabled_at": datetime.utcnow()}}
        )
        
        logger.info(f"Auto trading disabled for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error disabling auto trading for user {user_id}: {e}")


async def _send_emergency_alert(user_id: str, reason: str, closed_positions: List[str]):
    """Send emergency alert to user"""
    try:
        # In a real implementation, this would send email/SMS/push notification
        logger.warning(f"EMERGENCY ALERT for user {user_id}: {reason}. Closed {len(closed_positions)} positions.")
        
        # Store alert in database
        from app.core.database import get_database_sync
        
        db = await get_database_sync()
        
        alert_record = {
            "user_id": user_id,
            "type": "emergency_stop",
            "reason": reason,
            "positions_closed": closed_positions,
            "timestamp": datetime.utcnow(),
            "acknowledged": False
        }
        
        await db.alerts.insert_one(alert_record)
        
    except Exception as e:
        logger.error(f"Error sending emergency alert: {e}")


# Task status monitoring
@celery_app.task(bind=True, name="app.workers.tasks.get_task_status")
def get_task_status(self, task_id: str):
    """Get status of a specific task"""
    try:
        result = celery_app.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"task_id": task_id, "error": str(e)}


@celery_app.task(name="app.workers.tasks.health_check")
def health_check():
    """Health check task for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "worker_id": health_check.request.id
    }
