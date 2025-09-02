"""
Trading Executor Worker for automated trade execution and management
"""

from datetime import datetime, timedelta
from typing import Any

import redis
from loguru import logger

from app.ai.risk_manager import AIRiskManager
from app.core.config import settings
from app.core.database import get_database_sync
from app.core.deriv import websocket_manager
from app.crud.trading import (
    create_trade_position,
    get_position_by_id,
    get_user_positions,
    get_user_trading_parameters,
    update_position,
)
from app.crud.users import get_user
from app.models.trading import TradePositionCreate, TradePositionInDB


class TradingExecutorWorker:
    """
    Automated trading execution and management worker
    """

    def __init__(self):
        """Initialize the trading executor worker"""
        self.redis_client = redis.from_url(settings.redis_url)
        self.risk_manager = AIRiskManager()
        self.execution_queue = "trading_queue"
        self.active_executions = {}

        logger.info("Trading Executor Worker initialized")

    async def execute_trade_signal(self, signal_data: dict[str, Any]) -> dict[str, Any]:
        """
        Execute a trading signal

        Args:
            signal_data: Signal information including user_id, symbol, etc.

        Returns:
            Execution result
        """
        try:
            execution_id = f"exec_{signal_data['user_id']}_{datetime.utcnow().timestamp()}"
            self.active_executions[execution_id] = {
                "status": "processing",
                "signal": signal_data,
                "started_at": datetime.utcnow()
            }

            logger.info(f"Starting trade execution {execution_id} for user {signal_data['user_id']}")

            # Step 1: Validate signal and user
            validation_result = await self._validate_execution(signal_data)
            if not validation_result["valid"]:
                return await self._handle_execution_failure(
                    execution_id, "validation_failed", validation_result["reason"]
                )

            # Step 2: Perform final risk check
            risk_check = await self._final_risk_check(signal_data, validation_result["user_data"])
            if not risk_check["approved"]:
                return await self._handle_execution_failure(
                    execution_id, "risk_rejected", risk_check["reason"]
                )

            # Step 3: Execute the trade
            execution_result = await self._execute_trade(signal_data, validation_result["user_data"])

            if execution_result["success"]:
                # Step 4: Record trade in database
                trade_record = await self._record_trade(signal_data, execution_result)

                # Step 5: Set up monitoring for the new position
                await self._setup_position_monitoring(trade_record)

                self.active_executions[execution_id]["status"] = "completed"
                self.active_executions[execution_id]["result"] = execution_result

                logger.info(f"Trade execution {execution_id} completed successfully")

                return {
                    "execution_id": execution_id,
                    "success": True,
                    "trade_id": str(trade_record.id),
                    "contract_id": execution_result.get("contract_id"),
                    "entry_price": execution_result.get("entry_price"),
                    "amount": signal_data["recommended_amount"]
                }
            else:
                return await self._handle_execution_failure(
                    execution_id, "execution_failed", execution_result.get("error", "Unknown error")
                )

        except Exception as e:
            logger.error(f"Error in trade execution: {e}")
            return await self._handle_execution_failure(
                execution_id if 'execution_id' in locals() else "unknown",
                "system_error",
                str(e)
            )

    async def _validate_execution(self, signal_data: dict) -> dict[str, Any]:
        """Validate trade execution prerequisites"""
        try:
            user_id = signal_data["user_id"]

            # Get database connection
            db = await get_database_sync()

            # Get user data
            user = await get_user(db, user_id)
            if not user:
                return {"valid": False, "reason": "User not found"}

            # Check if user has Deriv token
            if not user.deriv_token:
                return {"valid": False, "reason": "User has no Deriv API token"}

            # Get user's trading parameters
            from app.crud.trading import get_user_positions, get_user_trading_parameters

            trading_params = await get_user_trading_parameters(db, user_id)
            if not trading_params:
                return {"valid": False, "reason": "User has no trading parameters"}

            # Get current positions
            positions = await get_user_positions(db, user_id, "open")

            # Check position limits
            if len(positions) >= settings.max_concurrent_positions:
                return {"valid": False, "reason": "Maximum concurrent positions reached"}

            # Check if signal is still valid (not too old)
            signal_age = datetime.utcnow() - datetime.fromisoformat(signal_data["generated_at"])
            if signal_age.total_seconds() > 300:  # 5 minutes
                return {"valid": False, "reason": "Signal too old"}

            # Check daily loss limits
            today = datetime.utcnow().date()
            daily_positions = [p for p in positions if p.created_at.date() == today]
            daily_pnl = sum(p.profit_loss or 0 for p in daily_positions)

            if daily_pnl <= -trading_params.max_daily_loss * 0.9:
                return {"valid": False, "reason": "Daily loss limit approached"}

            return {
                "valid": True,
                "user_data": {
                    "user": user,
                    "trading_params": trading_params,
                    "positions": positions,
                    "daily_pnl": daily_pnl
                }
            }

        except Exception as e:
            logger.error(f"Error validating execution: {e}")
            return {"valid": False, "reason": f"Validation error: {str(e)}"}

    async def _final_risk_check(self, signal_data: dict, user_data: dict) -> dict[str, Any]:
        """Perform final risk assessment before execution"""
        try:
            # Prepare market data
            market_data = {
                "current_price": 1.0,  # Would be fetched from live market
                "volatility": 0.2,     # Would be calculated from recent data
                "trend": "bullish",    # Would come from analysis
                "session": "active"
            }

            # Prepare user context
            user_context = {
                "risk_tolerance": "medium",
                "experience_level": "intermediate",
                "account_balance": 1000  # Would be fetched from user account
            }

            # Prepare portfolio context
            positions = user_data["positions"]
            portfolio_context = {
                "position_count": len(positions),
                "total_exposure": sum(p.amount for p in positions),
                "daily_pnl": user_data["daily_pnl"]
            }

            # Perform risk assessment
            risk_assessment = await self.risk_manager.assess_position_risk(
                symbol=signal_data["symbol"],
                position_size=signal_data["recommended_amount"],
                account_balance=user_context["account_balance"],
                market_data=market_data,
                user_context=user_context,
                portfolio_context=portfolio_context
            )

            # Check if trade should be approved
            if risk_assessment.recommended_action in ["halt_trading", "emergency_stop"]:
                return {
                    "approved": False,
                    "reason": f"Risk management: {risk_assessment.recommended_action}",
                    "risk_assessment": risk_assessment
                }

            # Adjust position size if needed
            adjusted_amount = signal_data["recommended_amount"] * risk_assessment.position_size_adjustment

            return {
                "approved": True,
                "adjusted_amount": adjusted_amount,
                "risk_assessment": risk_assessment
            }

        except Exception as e:
            logger.error(f"Error in final risk check: {e}")
            return {"approved": False, "reason": f"Risk check error: {str(e)}"}

    async def _execute_trade(self, signal_data: dict, user_data: dict) -> dict[str, Any]:
        """Execute the actual trade through Deriv API"""
        try:
            user = user_data["user"]

            # Get or create Deriv WebSocket connection
            deriv_ws = await websocket_manager.get_connection(user.id)

            if not deriv_ws:
                # Create new connection
                deriv_ws = await websocket_manager.create_connection(user.id, user.deriv_token)

                if not deriv_ws:
                    return {"success": False, "error": "Could not establish Deriv connection"}

            # Prepare trade parameters
            contract_type = signal_data["signal_type"]  # BUY_CALL or BUY_PUT
            symbol = signal_data["symbol"]
            amount = signal_data["recommended_amount"]
            duration = signal_data["recommended_duration"] * 60  # Convert to seconds

            # Map signal type to Deriv contract type
            deriv_contract_type = "CALL" if contract_type == "BUY_CALL" else "PUT"

            # Execute the trade
            execution_success = await deriv_ws.buy_contract(
                contract_type=deriv_contract_type,
                symbol=symbol,
                amount=amount,
                duration=duration,
                duration_unit="S"
            )

            if execution_success:
                # In a real implementation, we would wait for the response
                # and get the actual contract ID and entry price
                # For now, we'll simulate the response

                contract_id = f"CONTRACT_{datetime.utcnow().timestamp()}"
                entry_price = 1.0  # Would come from Deriv response

                return {
                    "success": True,
                    "contract_id": contract_id,
                    "entry_price": entry_price,
                    "execution_time": datetime.utcnow(),
                    "deriv_response": {"status": "success"}
                }
            else:
                return {"success": False, "error": "Deriv API execution failed"}

        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return {"success": False, "error": str(e)}

    async def _record_trade(self, signal_data: dict, execution_result: dict) -> TradePositionInDB:
        """Record the executed trade in database"""
        try:
            db = await get_database_sync()

            # Create trade position record
            trade_data = TradePositionCreate(
                symbol=signal_data["symbol"],
                contract_type=signal_data["signal_type"].replace("BUY_", ""),
                amount=signal_data["recommended_amount"],
                duration=signal_data["recommended_duration"],
                duration_unit="m"
            )

            # Create trade position in database
            trade_position = await create_trade_position(db, signal_data["user_id"], trade_data)

            # Update with execution details
            await update_position(
                db,
                str(trade_position.id),
                signal_data["user_id"],
                {
                    "contract_id": execution_result["contract_id"],
                    "entry_spot": execution_result["entry_price"],
                    "status": "open",
                    "entry_time": execution_result["execution_time"]
                }
            )

            # Get updated position
            updated_position = await get_position_by_id(db, str(trade_position.id), signal_data["user_id"])

            logger.info(f"Trade recorded: {trade_position.id} for user {signal_data['user_id']}")

            if updated_position is None:
                raise ValueError(f"Failed to retrieve updated position {trade_position.id}")

            return updated_position

        except Exception as e:
            logger.error(f"Error recording trade: {e}")
            raise

    async def _setup_position_monitoring(self, trade_record: TradePositionInDB):
        """Set up monitoring for the new position"""
        try:
            from app.workers.tasks import monitor_position

            # Schedule position monitoring task
            monitor_position.apply_async(
                args=[str(trade_record.id), trade_record.user_id],
                countdown=10,  # Start monitoring in 10 seconds
                queue="position_monitor"
            )

            logger.info(f"Position monitoring set up for trade {trade_record.id}")

        except Exception as e:
            logger.error(f"Error setting up position monitoring: {e}")

    async def _handle_execution_failure(self, execution_id: str, failure_type: str, reason: str) -> dict[str, Any]:
        """Handle execution failure"""
        logger.warning(f"Trade execution {execution_id} failed: {failure_type} - {reason}")

        if execution_id in self.active_executions:
            self.active_executions[execution_id]["status"] = "failed"
            self.active_executions[execution_id]["failure_type"] = failure_type
            self.active_executions[execution_id]["failure_reason"] = reason

        return {
            "execution_id": execution_id,
            "success": False,
            "failure_type": failure_type,
            "reason": reason,
            "timestamp": datetime.utcnow()
        }

    async def monitor_position(self, position_id: str, user_id: str) -> dict[str, Any]:
        """Monitor an active trading position"""
        try:
            db = await get_database_sync()

            # Get position
            position = await get_position_by_id(db, position_id, user_id)
            if not position or position.status != "open":
                return {"status": "position_not_active"}

            # Get user
            user = await get_user(db, user_id)
            if not user:
                return {"status": "user_not_found"}

            # Get Deriv connection
            deriv_ws = await websocket_manager.get_connection(user_id)
            if not deriv_ws:
                logger.warning(f"No Deriv connection for user {user_id}")
                return {"status": "no_connection"}

            # Get current portfolio/position status
            await deriv_ws.get_portfolio()

            # Calculate current P&L (would come from Deriv response)
            current_price = 1.01  # Simulated current price
            entry_price = position.entry_spot or 1.0

            if position.contract_type == "CALL":
                profit_loss = (current_price - entry_price) * position.amount * 100
            else:  # PUT
                profit_loss = (entry_price - current_price) * position.amount * 100

            # Update position with current P&L
            await update_position(
                db,
                position_id,
                user_id,
                {
                    "current_spot": current_price,
                    "profit_loss": profit_loss,
                    "updated_at": datetime.utcnow()
                }
            )

            # Check if position should be closed
            should_close, close_reason = await self._should_close_position(position, profit_loss, user)

            if should_close:
                await self._close_position(position, user, close_reason)
                return {
                    "status": "position_closed",
                    "reason": close_reason,
                    "final_pnl": profit_loss
                }
            else:
                # Schedule next monitoring check
                from app.workers.tasks import monitor_position
                monitor_position.apply_async(
                    args=[position_id, user_id],
                    countdown=settings.position_monitor_interval_seconds,
                    queue="position_monitor"
                )

                return {
                    "status": "monitoring_continued",
                    "current_pnl": profit_loss,
                    "current_price": current_price
                }

        except Exception as e:
            logger.error(f"Error monitoring position {position_id}: {e}")
            return {"status": "error", "error": str(e)}

    async def _should_close_position(self, position, current_pnl: float, user) -> tuple:
        """Determine if position should be closed"""
        try:
            # Get user's trading parameters
            db = await get_database_sync()
            trading_params = await get_user_trading_parameters(db, position.user_id)

            if not trading_params:
                return False, None

            # Check take profit
            if settings.auto_take_profit_enabled:
                take_profit_amount = position.amount * (trading_params.take_profit / 100)
                if current_pnl >= take_profit_amount:
                    return True, "take_profit_reached"

            # Check stop loss
            if settings.auto_stop_loss_enabled:
                stop_loss_amount = -position.amount * (trading_params.stop_loss / 100)
                if current_pnl <= stop_loss_amount:
                    return True, "stop_loss_triggered"

            # Check position duration (auto-expire)
            if position.entry_time:
                time_in_position = datetime.utcnow() - position.entry_time
                max_duration = timedelta(minutes=position.duration)

                if time_in_position >= max_duration:
                    return True, "duration_expired"

            # Check emergency conditions
            if settings.emergency_stop_enabled:
                # Check if daily loss limit exceeded
                today = datetime.utcnow().date()
                positions = await get_user_positions(db, position.user_id)
                daily_positions = [p for p in positions if p.created_at.date() == today]
                daily_pnl = sum(p.profit_loss or 0 for p in daily_positions)

                if daily_pnl <= -trading_params.max_daily_loss:
                    return True, "daily_loss_limit_exceeded"

            return False, None

        except Exception as e:
            logger.error(f"Error checking position close conditions: {e}")
            return False, None

    async def _close_position(self, position, user, reason: str):
        """Close a trading position"""
        try:
            # Get Deriv connection
            deriv_ws = await websocket_manager.get_connection(position.user_id)

            if deriv_ws and position.contract_id:
                # Attempt to sell the contract
                await deriv_ws.sell_contract(position.contract_id)

            # Update position status in database
            db = await get_database_sync()
            await update_position(
                db,
                str(position.id),
                position.user_id,
                {
                    "status": "closed",
                    "exit_time": datetime.utcnow(),
                    "exit_spot": position.current_spot
                }
            )

            logger.info(f"Position {position.id} closed: {reason}")

        except Exception as e:
            logger.error(f"Error closing position {position.id}: {e}")

    def get_execution_status(self) -> dict[str, Any]:
        """Get current execution status"""
        try:
            active_count = len([e for e in self.active_executions.values() if e["status"] == "processing"])

            return {
                "active_executions": active_count,
                "total_executions": len(self.active_executions),
                "redis_connected": self.redis_client.ping(),
                "auto_trading_enabled": settings.auto_trading_enabled,
                "max_concurrent_positions": settings.max_concurrent_positions
            }

        except Exception as e:
            logger.error(f"Error getting execution status: {e}")
            return {"error": str(e)}


# Create global instance
trading_executor = TradingExecutorWorker()
