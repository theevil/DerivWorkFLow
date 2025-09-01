"""
Celery application configuration for background tasks
"""

import os
from celery import Celery
from celery.schedules import crontab
from loguru import logger

from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "deriv_workflow",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.workers.tasks",
        "app.workers.market_monitor", 
        "app.workers.trading_executor",
        "app.workers.risk_monitor",
        "app.workers.signal_processor"
    ]
)

# Configure Celery
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.workers.tasks.market_scan": {"queue": "market_scan"},
        "app.workers.tasks.position_monitor": {"queue": "position_monitor"},
        "app.workers.tasks.execute_trade": {"queue": "trading"},
        "app.workers.tasks.risk_check": {"queue": "risk_monitor"},
        "app.workers.tasks.process_signal": {"queue": "signals"},
    },
    
    # Task configuration
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task timeouts
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes
    
    # Task retries
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_persistent=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    # Market scanning every 30 seconds
    "market-scan": {
        "task": "app.workers.tasks.market_scan_scheduler",
        "schedule": settings.market_scan_interval_seconds,
        "options": {"queue": "market_scan"}
    },
    
    # Position monitoring every 10 seconds
    "position-monitor": {
        "task": "app.workers.tasks.position_monitor_scheduler", 
        "schedule": settings.position_monitor_interval_seconds,
        "options": {"queue": "position_monitor"}
    },
    
    # Risk monitoring every 60 seconds
    "risk-monitor": {
        "task": "app.workers.tasks.risk_monitor_scheduler",
        "schedule": 60.0,
        "options": {"queue": "risk_monitor"}
    },
    
    # Model retraining check every hour
    "model-retrain-check": {
        "task": "app.workers.tasks.model_retrain_scheduler",
        "schedule": crontab(minute=0),  # Every hour
        "options": {"queue": "training"}
    },
    
    # Daily portfolio analysis
    "daily-portfolio-analysis": {
        "task": "app.workers.tasks.daily_portfolio_analysis",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
        "options": {"queue": "analysis"}
    },
    
    # Weekly model performance review
    "weekly-performance-review": {
        "task": "app.workers.tasks.weekly_performance_review",
        "schedule": crontab(hour=2, minute=0, day_of_week=1),  # Monday 2 AM
        "options": {"queue": "analysis"}
    }
}

# Configure logging
@celery_app.signal.setup_logging.connect
def setup_celery_logging(**kwargs):
    """Setup logging for Celery"""
    logger.info("Setting up Celery logging")

@celery_app.signal.worker_ready.connect
def worker_ready_handler(sender, **kwargs):
    """Handler for when worker is ready"""
    logger.info(f"Celery worker {sender} is ready")

@celery_app.signal.worker_shutdown.connect  
def worker_shutdown_handler(sender, **kwargs):
    """Handler for when worker shuts down"""
    logger.info(f"Celery worker {sender} is shutting down")

@celery_app.signal.task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Handler before task execution"""
    logger.debug(f"Task {task.name} [{task_id}] starting")

@celery_app.signal.task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """Handler after task execution"""
    logger.debug(f"Task {task.name} [{task_id}] finished with state: {state}")

@celery_app.signal.task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """Handler for task failures"""
    logger.error(f"Task {sender.name} [{task_id}] failed: {exception}")
    logger.error(f"Traceback: {traceback}")

# Queue configuration
CELERY_QUEUES = {
    "market_scan": {
        "routing_key": "market_scan",
        "priority": 8
    },
    "position_monitor": {
        "routing_key": "position_monitor", 
        "priority": 9
    },
    "trading": {
        "routing_key": "trading",
        "priority": 10  # Highest priority
    },
    "risk_monitor": {
        "routing_key": "risk_monitor",
        "priority": 9
    },
    "signals": {
        "routing_key": "signals",
        "priority": 7
    },
    "training": {
        "routing_key": "training",
        "priority": 3
    },
    "analysis": {
        "routing_key": "analysis", 
        "priority": 5
    },
    "default": {
        "routing_key": "default",
        "priority": 5
    }
}

# Export the app
__all__ = ["celery_app"]
