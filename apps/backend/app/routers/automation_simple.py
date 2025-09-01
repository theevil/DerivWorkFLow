"""
Simple Automation Router for testing connectivity
"""

from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def get_automation_status():
    """Get current status of all automation workers"""
    return {
        "market_monitor": {
            "active": True,
            "redis_connected": True,
            "last_scan": "2024-01-01T12:00:00Z"
        },
        "trading_executor": {
            "active_executions": 0,
            "total_executions": 0,
            "redis_connected": True
        },
        "celery_active_tasks": 0,
        "redis_connected": True,
        "system_healthy": True
    }

@router.get("/auto-trading/config")
async def get_auto_trading_config():
    """Get auto trading configuration"""
    return {
        "enabled": False,
        "config": {
            "max_concurrent_positions": 5,
            "market_scan_interval": 30,
            "position_monitor_interval": 10,
            "auto_stop_loss": True,
            "auto_take_profit": True
        },
        "last_updated": "2024-01-01T12:00:00Z"
    }

@router.get("/performance/summary")
async def get_automation_performance():
    """Get automation performance metrics"""
    return {
        "trading_stats": {
            "total_trades": 42,
            "profitable_trades": 28,
            "total_profit": 1250.75,
            "avg_profit": 29.78,
            "max_profit": 150.50,
            "min_profit": -45.25,
            "win_rate": 0.67
        },
        "system_stats": {
            "uptime_hours": 168.5,
            "tasks_completed": 1247,
            "avg_response_time": 0.15
        }
    }

@router.get("/alerts")
async def get_automation_alerts():
    """Get automation alerts"""
    return {
        "alerts": [],
        "total_count": 0,
        "unacknowledged_count": 0
    }

@router.post("/auto-trading/configure")
async def configure_auto_trading():
    """Configure auto trading settings"""
    return {
        "message": "Auto trading configuration updated successfully",
        "config": {
            "enabled": False,
            "max_concurrent_positions": 5,
            "market_scan_interval": 30,
            "position_monitor_interval": 10,
            "auto_stop_loss": True,
            "auto_take_profit": True
        },
        "user_id": "test_user"
    }

@router.post("/emergency-stop")
async def trigger_emergency_stop():
    """Trigger emergency stop"""
    return {
        "message": "Emergency stop activated successfully",
        "task_id": "emergency_stop_123",
        "timestamp": "2024-01-01T12:00:00Z"
    }

@router.post("/market-scan/trigger")
async def trigger_market_scan():
    """Trigger market scan"""
    return {
        "task_id": "market_scan_123",
        "message": "Market scan triggered successfully"
    }

@router.post("/position-monitor/trigger")
async def trigger_position_monitor():
    """Trigger position monitor"""
    return {
        "task_id": "position_monitor_123",
        "message": "Position monitor triggered successfully"
    }

@router.post("/models/retrain")
async def trigger_model_retrain():
    """Trigger model retraining"""
    return {
        "task_id": "model_retrain_123",
        "message": "Model retraining triggered successfully"
    }

@router.post("/health-check")
async def run_health_check():
    """Run system health check"""
    return {
        "system_status": "healthy",
        "checks": {
            "redis": "connected",
            "database": "connected",
            "workers": "active"
        },
        "timestamp": "2024-01-01T12:00:00Z"
    }
