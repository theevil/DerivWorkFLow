import json
import time
import asyncio
from typing import Optional, Any
from datetime import datetime

from fastapi import (
    APIRouter,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from loguru import logger

from app.core.deriv import websocket_manager
from app.models.user import User
from app.routers.auth import get_current_user_from_token

router = APIRouter()


class WebSocketConnectionManager:
    """Manage WebSocket connections for real-time updates"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.user_connections: dict[str, str] = {}  # user_id -> connection_id
        self.message_queues: dict[str, list] = {}  # connection_id -> message queue
        self.last_heartbeat: dict[str, float] = {}  # connection_id -> timestamp
        self.connection_tasks: dict[str, list] = {}  # connection_id -> background tasks

        # Configuración
        self.MAX_CONNECTIONS_PER_USER = 1
        self.MESSAGE_BATCH_SIZE = 10
        self.MESSAGE_BATCH_INTERVAL = 0.1  # seconds
        self.HEARTBEAT_INTERVAL = 15  # seconds
        self.CONNECTION_TIMEOUT = 30  # seconds

        logger.info("WebSocketConnectionManager initialized")

    async def connect(self, websocket: WebSocket, user_id: str):
        """Register a WebSocket connection"""
        connection_id = f"ws_{user_id}_{id(websocket)}"

        # Close existing connection if any
        if user_id in self.user_connections:
            old_connection_id = self.user_connections[user_id]
            if old_connection_id in self.active_connections:
                logger.info(f"Closing existing connection for user {user_id}")
                await self.disconnect(old_connection_id)

        # Initialize connection
        self.active_connections[connection_id] = websocket
        self.user_connections[user_id] = connection_id
        self.message_queues[connection_id] = []
        self.last_heartbeat[connection_id] = time.time()
        self.connection_tasks[connection_id] = []

        # Create background tasks
        heartbeat_task = asyncio.create_task(self._heartbeat_monitor(connection_id))
        batch_task = asyncio.create_task(self._message_batch_sender(connection_id))

        # Store tasks for cleanup
        self.connection_tasks[connection_id].extend([heartbeat_task, batch_task])

        logger.info(f"WebSocket connection established for user {user_id}")

        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "WebSocket connection established"
        }, user_id)

        logger.info(f"WebSocket connected for user {user_id}")

        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "message": "WebSocket connection established"
        }, user_id)

    async def _heartbeat_monitor(self, connection_id: str):
        """Monitor connection health through heartbeats"""
        while connection_id in self.active_connections:
            current_time = time.time()
            if current_time - self.last_heartbeat.get(connection_id, 0) > self.CONNECTION_TIMEOUT:
                logger.warning(f"Connection {connection_id} timed out")
                await self.disconnect(connection_id)
                break
            await asyncio.sleep(self.HEARTBEAT_INTERVAL)

    async def _message_batch_sender(self, connection_id: str):
        """Send batched messages periodically"""
        while connection_id in self.active_connections:
            if connection_id in self.message_queues and self.message_queues[connection_id]:
                messages = self.message_queues[connection_id][:self.MESSAGE_BATCH_SIZE]
                self.message_queues[connection_id] = self.message_queues[connection_id][self.MESSAGE_BATCH_SIZE:]

                try:
                    websocket = self.active_connections[connection_id]
                    await websocket.send_json({
                        "type": "batch",
                        "messages": messages,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error sending batch to {connection_id}: {e}")
                    await self.disconnect(connection_id)
                    break

            await asyncio.sleep(self.MESSAGE_BATCH_INTERVAL)

    async def queue_message(self, connection_id: str, message: Any):
        """Queue a message for batched sending"""
        if connection_id in self.message_queues:
            self.message_queues[connection_id].append(message)

    async def disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection and cleanup resources"""
        if connection_id in self.active_connections:
            # Cancel background tasks
            if connection_id in self.connection_tasks:
                for task in self.connection_tasks[connection_id]:
                    try:
                        task.cancel()
                        await task
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        logger.error(f"Error canceling task for {connection_id}: {e}")
                self.connection_tasks.pop(connection_id)

            # Close WebSocket
            try:
                websocket = self.active_connections[connection_id]
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing websocket {connection_id}: {e}")

            # Cleanup resources
            del self.active_connections[connection_id]
            self.message_queues.pop(connection_id, None)
            self.last_heartbeat.pop(connection_id, None)

            # Remove user connection mapping
            for user_id, conn_id in list(self.user_connections.items()):
                if conn_id == connection_id:
                    del self.user_connections[user_id]
                    logger.info(f"WebSocket disconnected for user {user_id}")
                    break

            # Remove from user connections
            for user_id, conn_id in list(self.user_connections.items()):
                if conn_id == connection_id:
                    del self.user_connections[user_id]
                    logger.info(f"WebSocket disconnected for user {user_id}")
                    break

    async def disconnect_user(self, user_id: str):
        """Disconnect a specific user"""
        if user_id in self.user_connections:
            connection_id = self.user_connections[user_id]
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.close()
                except:
                    pass
                await self.disconnect(connection_id)

    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to a specific user"""
        if user_id in self.user_connections:
            connection_id = self.user_connections[user_id]
            if connection_id in self.active_connections:
                try:
                    # Mensajes de control (connection, heartbeat) se envían inmediatamente
                    if message.get("type") in ["connection", "heartbeat"]:
                        await self.active_connections[connection_id].send_json(message)
                    else:
                        # Otros mensajes se encolan para envío por lotes
                        await self.queue_message(connection_id, message)
                    return True
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    await self.disconnect(connection_id)
        return False

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected users"""
        if message.get("type") in ["connection", "heartbeat"]:
            # Mensajes de control se envían inmediatamente
            disconnected = []
            for connection_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {e}")
                    disconnected.append(connection_id)

            # Clean up disconnected connections
            for connection_id in disconnected:
                await self.disconnect(connection_id)
        else:
            # Otros mensajes se encolan para envío por lotes
            for connection_id in self.active_connections:
                await self.queue_message(connection_id, message)

    def get_user_count(self) -> int:
        """Get number of connected users"""
        return len(self.active_connections)


# Global connection manager
connection_manager = WebSocketConnectionManager()


async def get_current_user_websocket(websocket: WebSocket, token: Optional[str] = None) -> User:
    """Get current user from WebSocket token"""
    try:
        if not token:
            logger.error("WebSocket connection attempt without token")
            raise HTTPException(status_code=403, detail="Token required")

        user = await get_current_user_from_token(token)
        if not user:
            logger.error(f"Invalid token provided in WebSocket connection")
            raise HTTPException(status_code=403, detail="Invalid token")

        logger.info(f"WebSocket user authenticated: {user.id}")
        return user

    except HTTPException as e:
        logger.error(f"Authentication failed for WebSocket: {e.detail}")
        try:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        except Exception:
            pass
        raise

    except Exception as e:
        logger.error(f"Unexpected error during WebSocket authentication: {str(e)}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Internal server error")


@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    """Main WebSocket endpoint for real-time communication"""
    user = None
    deriv_ws = None

    try:
        # Validate user first
        user = await get_current_user_websocket(websocket, token)
        if not user:
            logger.error("User validation failed")
            return

        # Accept the WebSocket connection BEFORE any other operations
        await websocket.accept()
        logger.info(f"WebSocket connection accepted for user {user.id}")

        # Initialize Deriv WebSocket connection
        deriv_ws = await websocket_manager.get_connection(f"user_{user.id}")

        # Register the connection with our manager
        await connection_manager.connect(websocket, user.id)
        logger.info(f"WebSocket connection registered for user {user.id}")

        # Connect to our connection manager
        await connection_manager.connect(websocket, user.id)

        # Create Deriv WebSocket connection for this user
        deriv_ws = await websocket_manager.create_connection(user.id, user.deriv_token or None)

        if deriv_ws:
            # Set up Deriv message handlers with proper async wrappers
            async def tick_handler(data): return await handle_tick_data(data, user.id)
            async def portfolio_handler(data): return await handle_portfolio_data(data, user.id)
            async def buy_handler(data): return await handle_buy_response(data, user.id)
            async def sell_handler(data): return await handle_sell_response(data, user.id)

            deriv_ws.add_message_handler("tick", tick_handler)
            deriv_ws.add_message_handler("portfolio", portfolio_handler)
            deriv_ws.add_message_handler("buy", buy_handler)
            deriv_ws.add_message_handler("sell", sell_handler)

            # Subscribe to portfolio updates
            try:
                await deriv_ws.subscribe_portfolio()
            except Exception as e:
                logger.warning(f"Failed to subscribe to portfolio for user {user.id}: {e}")

        # Main message loop
        while True:
            try:
                # Receive message from frontend
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                await handle_websocket_message(message, user.id, deriv_ws)

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for user {user.id}")
                break
            except json.JSONDecodeError:
                await connection_manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, user.id)
            except Exception as e:
                logger.error(f"Error in WebSocket loop: {e}")
                try:
                    await connection_manager.send_personal_message({
                        "type": "error",
                        "message": "Internal server error"
                    }, user.id)
                except:
                    # If we can't send error message, connection is likely broken
                    break

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except:
            pass

    finally:
        # Cleanup
        if user:
            await connection_manager.disconnect_user(user.id)
            if deriv_ws:
                await websocket_manager.close_connection(f"user_{user.id}")


async def handle_websocket_message(message: dict, user_id: str, deriv_ws):
    """Handle incoming WebSocket messages from frontend"""
    try:
        msg_type = message.get("type")

        if msg_type == "ping":
            await connection_manager.send_personal_message({
                "type": "pong",
                "timestamp": message.get("timestamp")
            }, user_id)

        elif msg_type == "subscribe_ticks":
            symbol = message.get("symbol")
            if symbol and deriv_ws:
                await deriv_ws.subscribe_ticks(symbol)
                await connection_manager.send_personal_message({
                    "type": "subscription",
                    "status": "subscribed",
                    "symbol": symbol
                }, user_id)

        elif msg_type == "unsubscribe_ticks":
            symbol = message.get("symbol")
            if symbol and deriv_ws:
                await deriv_ws.unsubscribe_ticks(symbol)
                await connection_manager.send_personal_message({
                    "type": "subscription",
                    "status": "unsubscribed",
                    "symbol": symbol
                }, user_id)

        elif msg_type == "buy_contract":
            if deriv_ws:
                await deriv_ws.buy_contract(
                    contract_type=message.get("contract_type"),
                    symbol=message.get("symbol"),
                    amount=message.get("amount"),
                    duration=message.get("duration"),
                    duration_unit=message.get("duration_unit", "S"),
                    barrier=message.get("barrier")
                )

        elif msg_type == "sell_contract":
            if deriv_ws:
                await deriv_ws.sell_contract(
                    contract_id=message.get("contract_id"),
                    price=message.get("price")
                )

        elif msg_type == "get_portfolio":
            if deriv_ws:
                await deriv_ws.get_portfolio()

        else:
            await connection_manager.send_personal_message({
                "type": "error",
                "message": f"Unknown message type: {msg_type}"
            }, user_id)

    except Exception as e:
        logger.error(f"Error handling WebSocket message: {e}")
        await connection_manager.send_personal_message({
            "type": "error",
            "message": "Failed to process message"
        }, user_id)


async def handle_tick_data(data: dict, user_id: str):
    """Handle tick data from Deriv"""
    await connection_manager.send_personal_message({
        "type": "tick",
        "data": data
    }, user_id)


async def handle_portfolio_data(data: dict, user_id: str):
    """Handle portfolio data from Deriv"""
    await connection_manager.send_personal_message({
        "type": "portfolio",
        "data": data
    }, user_id)


async def handle_buy_response(data: dict, user_id: str):
    """Handle buy contract response from Deriv"""
    await connection_manager.send_personal_message({
        "type": "buy_response",
        "data": data
    }, user_id)


async def handle_sell_response(data: dict, user_id: str):
    """Handle sell contract response from Deriv"""
    await connection_manager.send_personal_message({
        "type": "sell_response",
        "data": data
    }, user_id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "active_connections": connection_manager.get_user_count(),
        "deriv_connections": len(websocket_manager.connections)
    }
