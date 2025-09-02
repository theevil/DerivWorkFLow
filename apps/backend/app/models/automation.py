from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


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
