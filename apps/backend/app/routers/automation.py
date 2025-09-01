"""
Automation Router for managing background workers and automated trading
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from app.core.database import get_database
from app.routers.auth import get_current_user
from app.models.user import User
from app.workers.market_monitor import market_monitor
from app.workers.trading_executor import trading_executor
from app.workers.celery_app import celery_app
from app.workers.tasks import (
    market_scan_scheduler,
    position_monitor_scheduler,
    process_signal,
    emergency_stop,
    retrain_user_models,
    health_check
)

router = APIRouter()

# Pydantic models for API requests/responses

class AutoTradingConfig(BaseModel):
    enabled: bool = Field(description="Enable/disable auto trading")
    max_concurrent_positions: int = Field(default=5, ge=1, le=10, description="Maximum concurrent positions")
    market_scan_interval: int = Field(default=30, ge=10, le=300, description="Market scan interval in seconds")
    position_monitor_interval: int = Field(default=10, ge=5, le=60, description="Position monitoring interval in seconds")
    auto_stop_loss: bool = Field(default=True, description="Enable automatic stop loss")
    auto_take_profit: bool = Field(default=True, description="Enable automatic take profit")


class EmergencyStopRequest(BaseModel):
    reason: str = Field(description="Reason for emergency stop")
    close_positions: bool = Field(default=True, description="Whether to close all open positions")


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Any] = None
    timestamp: str


class WorkerStatusResponse(BaseModel):
    market_monitor: Dict[str, Any]
    trading_executor: Dict[str, Any]
    celery_active_tasks: int
    redis_connected: bool


@router.get("/status", response_model=WorkerStatusResponse)
async def get_automation_status(
    current_user: User = Depends(get_current_user)
):
    """Get current status of all automation workers"""
    try:
        # Get status from workers
        market_status = market_monitor.get_market_status()
        executor_status = trading_executor.get_execution_status()
        
        # Get Celery status
        celery_inspect = celery_app.control.inspect()
        active_tasks = celery_inspect.active()
        
        # Count active tasks
        active_task_count = 0
        if active_tasks:
            for worker, tasks in active_tasks.items():
                active_task_count += len(tasks)
        
        return WorkerStatusResponse(
            market_monitor=market_status,
            trading_executor=executor_status,
            celery_active_tasks=active_task_count,
            redis_connected=market_status.get("redis_connected", False)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting automation status: {str(e)}"
        )


@router.post("/auto-trading/configure")
async def configure_auto_trading(
    config: AutoTradingConfig,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Configure auto trading settings for the current user"""
    try:
        # Update user's auto trading configuration
        user_config = {
            "auto_trading_enabled": config.enabled,
            "auto_trading_config": config.dict(),
            "auto_trading_updated_at": datetime.utcnow()
        }
        
        await db.users.update_one(
            {"_id": current_user.id},
            {"$set": user_config}
        )
        
        return {
            "message": "Auto trading configuration updated",
            "config": config.dict(),
            "user_id": str(current_user.id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error configuring auto trading: {str(e)}"
        )


@router.get("/auto-trading/config")
async def get_auto_trading_config(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get current auto trading configuration for the user"""
    try:
        user_doc = await db.users.find_one({"_id": current_user.id})
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        auto_config = user_doc.get("auto_trading_config", {})
        
        return {
            "enabled": user_doc.get("auto_trading_enabled", False),
            "config": auto_config,
            "last_updated": user_doc.get("auto_trading_updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting auto trading config: {str(e)}"
        )


@router.post("/emergency-stop")
async def trigger_emergency_stop(
    request: EmergencyStopRequest,
    current_user: User = Depends(get_current_user)
):
    """Trigger emergency stop for the current user"""
    try:
        # Trigger emergency stop task
        task = emergency_stop.delay(str(current_user.id), request.reason)
        
        return {
            "message": "Emergency stop triggered",
            "task_id": task.id,
            "user_id": str(current_user.id),
            "reason": request.reason,
            "close_positions": request.close_positions
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering emergency stop: {str(e)}"
        )


@router.post("/market-scan/trigger")
async def trigger_market_scan(
    current_user: User = Depends(get_current_user)
):
    """Manually trigger a market scan"""
    try:
        # Trigger market scan task
        task = market_scan_scheduler.delay()
        
        return {
            "message": "Market scan triggered",
            "task_id": task.id,
            "status": "scheduled"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering market scan: {str(e)}"
        )


@router.post("/position-monitor/trigger")
async def trigger_position_monitor(
    current_user: User = Depends(get_current_user)
):
    """Manually trigger position monitoring cycle"""
    try:
        # Trigger position monitoring task
        task = position_monitor_scheduler.delay()
        
        return {
            "message": "Position monitoring triggered",
            "task_id": task.id,
            "status": "scheduled"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering position monitor: {str(e)}"
        )


@router.post("/models/retrain")
async def trigger_model_retrain(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Trigger model retraining for the current user"""
    try:
        # Trigger model retraining task
        task = retrain_user_models.delay(str(current_user.id))
        
        return {
            "message": "Model retraining started",
            "task_id": task.id,
            "user_id": str(current_user.id),
            "status": "scheduled"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error triggering model retrain: {str(e)}"
        )


@router.get("/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get status of a specific background task"""
    try:
        # Get task result
        result = celery_app.AsyncResult(task_id)
        
        return TaskStatusResponse(
            task_id=task_id,
            status=result.status,
            result=result.result,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting task status: {str(e)}"
        )


@router.get("/tasks/active")
async def get_active_tasks(
    current_user: User = Depends(get_current_user)
):
    """Get list of currently active background tasks"""
    try:
        # Get active tasks from Celery
        celery_inspect = celery_app.control.inspect()
        active_tasks = celery_inspect.active()
        scheduled_tasks = celery_inspect.scheduled()
        
        # Process active tasks
        processed_active = {}
        if active_tasks:
            for worker, tasks in active_tasks.items():
                processed_active[worker] = [
                    {
                        "id": task["id"],
                        "name": task["name"],
                        "args": task["args"],
                        "kwargs": task["kwargs"],
                        "time_start": task.get("time_start"),
                        "worker": worker
                    }
                    for task in tasks
                ]
        
        # Process scheduled tasks
        processed_scheduled = {}
        if scheduled_tasks:
            for worker, tasks in scheduled_tasks.items():
                processed_scheduled[worker] = [
                    {
                        "id": task["id"],
                        "name": task["task"],
                        "args": task["args"],
                        "kwargs": task["kwargs"],
                        "eta": task.get("eta"),
                        "worker": worker
                    }
                    for task in tasks
                ]
        
        return {
            "active_tasks": processed_active,
            "scheduled_tasks": processed_scheduled,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting active tasks: {str(e)}"
        )


@router.get("/queue-stats")
async def get_queue_stats(
    current_user: User = Depends(get_current_user)
):
    """Get statistics about task queues"""
    try:
        # Get queue statistics using Redis
        import redis
        from app.core.config import settings
        
        redis_client = redis.from_url(settings.redis_url)
        
        # Get queue lengths
        queues = [
            "market_scan",
            "position_monitor", 
            "trading",
            "risk_monitor",
            "signals",
            "training",
            "analysis"
        ]
        
        queue_stats = {}
        for queue in queues:
            queue_key = f"celery.{queue}"
            length = redis_client.llen(queue_key)
            queue_stats[queue] = {
                "length": length,
                "queue_key": queue_key
            }
        
        # Get worker statistics
        celery_inspect = celery_app.control.inspect()
        worker_stats = celery_inspect.stats()
        
        return {
            "queue_lengths": queue_stats,
            "worker_stats": worker_stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting queue stats: {str(e)}"
        )


@router.post("/health-check")
async def run_health_check(
    current_user: User = Depends(get_current_user)
):
    """Run health check on automation system"""
    try:
        # Trigger health check task
        task = health_check.delay()
        
        # Wait for quick response
        result = task.get(timeout=10)
        
        return {
            "health_check": result,
            "task_id": task.id,
            "system_status": "healthy" if result.get("status") == "healthy" else "unhealthy"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running health check: {str(e)}"
        )


@router.get("/alerts")
async def get_user_alerts(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get alerts for the current user"""
    try:
        # Get recent alerts for user
        alerts_cursor = db.alerts.find({
            "user_id": str(current_user.id),
            "timestamp": {"$gte": datetime.utcnow() - timedelta(days=7)}
        }).sort("timestamp", -1).limit(50)
        
        alerts = []
        async for alert in alerts_cursor:
            alerts.append({
                "id": str(alert["_id"]),
                "type": alert["type"],
                "reason": alert["reason"],
                "timestamp": alert["timestamp"],
                "acknowledged": alert.get("acknowledged", False),
                "positions_closed": alert.get("positions_closed", [])
            })
        
        return {
            "alerts": alerts,
            "total_count": len(alerts),
            "unacknowledged_count": len([a for a in alerts if not a["acknowledged"]])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user alerts: {str(e)}"
        )


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Acknowledge an alert"""
    try:
        from bson import ObjectId
        
        # Update alert as acknowledged
        result = await db.alerts.update_one(
            {
                "_id": ObjectId(alert_id),
                "user_id": str(current_user.id)
            },
            {
                "$set": {
                    "acknowledged": True,
                    "acknowledged_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        return {
            "message": "Alert acknowledged",
            "alert_id": alert_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error acknowledging alert: {str(e)}"
        )


@router.get("/performance/summary")
async def get_automation_performance(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get automation performance summary"""
    try:
        from datetime import datetime, timedelta
        
        # Get performance data for the specified period
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get trading statistics
        pipeline = [
            {
                "$match": {
                    "user_id": str(current_user.id),
                    "created_at": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_trades": {"$sum": 1},
                    "profitable_trades": {
                        "$sum": {"$cond": [{"$gt": ["$profit_loss", 0]}, 1, 0]}
                    },
                    "total_profit": {"$sum": "$profit_loss"},
                    "avg_profit": {"$avg": "$profit_loss"},
                    "max_profit": {"$max": "$profit_loss"},
                    "min_profit": {"$min": "$profit_loss"}
                }
            }
        ]
        
        result = await db.trade_positions.aggregate(pipeline).to_list(1)
        
        if result:
            stats = result[0]
            win_rate = stats["profitable_trades"] / stats["total_trades"] if stats["total_trades"] > 0 else 0
        else:
            stats = {
                "total_trades": 0,
                "profitable_trades": 0,
                "total_profit": 0,
                "avg_profit": 0,
                "max_profit": 0,
                "min_profit": 0
            }
            win_rate = 0
        
        return {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": datetime.utcnow().isoformat(),
            "trading_stats": {
                **stats,
                "win_rate": win_rate
            },
            "user_id": str(current_user.id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting automation performance: {str(e)}"
        )


# Add missing import
from datetime import datetime, timedelta
