import json
import asyncio
import websockets
from typing import Dict, Any, Optional, Callable, Set
from loguru import logger
from websockets.exceptions import ConnectionClosed, WebSocketException

from app.core.config import settings


class DerivWebSocket:
    """WebSocket client for Deriv API"""
    
    def __init__(self, app_id: str = None, api_token: str = None):
        self.app_id = app_id or settings.deriv_app_id
        self.api_token = api_token
        self.websocket = None
        self.is_connected = False
        self.subscriptions: Set[str] = set()
        self.message_handlers: Dict[str, Callable] = {}
        self.request_id = 1000
        
    async def connect(self) -> bool:
        """Connect to Deriv WebSocket API"""
        try:
            url = f"{settings.deriv_api_url}?app_id={self.app_id}"
            self.websocket = await websockets.connect(url)
            self.is_connected = True
            logger.info(f"Connected to Deriv WebSocket: {url}")
            
            # Start message listener
            asyncio.create_task(self._message_listener())
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Deriv WebSocket: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Deriv WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("Disconnected from Deriv WebSocket")
    
    async def _message_listener(self):
        """Listen for incoming messages"""
        try:
            while self.is_connected and self.websocket:
                try:
                    message = await self.websocket.recv()
                    data = json.loads(message)
                    await self._handle_message(data)
                except ConnectionClosed:
                    logger.warning("WebSocket connection closed")
                    self.is_connected = False
                    break
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                except Exception as e:
                    logger.error(f"Error in message listener: {e}")
        except Exception as e:
            logger.error(f"Message listener error: {e}")
    
    async def _handle_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        try:
            msg_type = data.get('msg_type')
            if msg_type and msg_type in self.message_handlers:
                await self.message_handlers[msg_type](data)
            else:
                logger.debug(f"Received message: {data}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    def add_message_handler(self, msg_type: str, handler: Callable):
        """Add a message handler for specific message types"""
        self.message_handlers[msg_type] = handler
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message to Deriv WebSocket"""
        if not self.is_connected or not self.websocket:
            logger.error("Not connected to WebSocket")
            return False
        
        try:
            message['req_id'] = self.request_id
            self.request_id += 1
            
            await self.websocket.send(json.dumps(message))
            logger.debug(f"Sent message: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    async def authorize(self, api_token: str = None) -> bool:
        """Authorize with Deriv API"""
        token = api_token or self.api_token
        if not token:
            logger.error("No API token provided")
            return False
        
        message = {
            "authorize": token
        }
        
        return await self.send_message(message)
    
    async def ping(self) -> bool:
        """Send ping to keep connection alive"""
        message = {"ping": 1}
        return await self.send_message(message)
    
    async def get_account_info(self) -> bool:
        """Get account information"""
        message = {"get_account_status": 1}
        return await self.send_message(message)
    
    async def subscribe_ticks(self, symbol: str) -> bool:
        """Subscribe to tick data for a symbol"""
        message = {
            "ticks": symbol,
            "subscribe": 1
        }
        
        success = await self.send_message(message)
        if success:
            self.subscriptions.add(f"ticks_{symbol}")
        return success
    
    async def unsubscribe_ticks(self, symbol: str) -> bool:
        """Unsubscribe from tick data"""
        message = {
            "forget": f"ticks_{symbol}"
        }
        
        success = await self.send_message(message)
        if success:
            self.subscriptions.discard(f"ticks_{symbol}")
        return success
    
    async def buy_contract(self, 
                          contract_type: str,
                          symbol: str,
                          amount: float,
                          duration: int,
                          duration_unit: str = "S",
                          barrier: Optional[float] = None) -> bool:
        """Buy a contract"""
        message = {
            "buy": 1,
            "parameters": {
                "contract_type": contract_type,
                "symbol": symbol,
                "amount": amount,
                "duration": duration,
                "duration_unit": duration_unit
            }
        }
        
        if barrier:
            message["parameters"]["barrier"] = barrier
        
        return await self.send_message(message)
    
    async def sell_contract(self, contract_id: str, price: Optional[float] = None) -> bool:
        """Sell a contract"""
        message = {
            "sell": contract_id
        }
        
        if price:
            message["price"] = price
        
        return await self.send_message(message)
    
    async def get_portfolio(self) -> bool:
        """Get portfolio information"""
        message = {"portfolio": 1}
        return await self.send_message(message)
    
    async def subscribe_portfolio(self) -> bool:
        """Subscribe to portfolio updates"""
        message = {
            "portfolio": 1,
            "subscribe": 1
        }
        
        success = await self.send_message(message)
        if success:
            self.subscriptions.add("portfolio")
        return success
    
    async def get_active_symbols(self, landing_company: str = "svg") -> bool:
        """Get active symbols"""
        message = {
            "active_symbols": "brief",
            "landing_company": landing_company
        }
        return await self.send_message(message)
    
    async def get_asset_index(self) -> bool:
        """Get asset index"""
        message = {"asset_index": 1}
        return await self.send_message(message)


class DerivWebSocketManager:
    """Manager for multiple Deriv WebSocket connections"""
    
    def __init__(self):
        self.connections: Dict[str, DerivWebSocket] = {}
        self.user_connections: Dict[str, str] = {}  # user_id -> connection_id
    
    async def create_connection(self, user_id: str, api_token: str = None) -> Optional[DerivWebSocket]:
        """Create a new WebSocket connection for a user"""
        try:
            connection_id = f"user_{user_id}"
            
            # Close existing connection if any
            if connection_id in self.connections:
                await self.close_connection(connection_id)
            
            ws = DerivWebSocket(api_token=api_token)
            
            if await ws.connect():
                self.connections[connection_id] = ws
                self.user_connections[user_id] = connection_id
                
                # Authorize if token provided
                if api_token:
                    await ws.authorize(api_token)
                
                logger.info(f"Created WebSocket connection for user {user_id}")
                return ws
            else:
                logger.error(f"Failed to create WebSocket connection for user {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating connection for user {user_id}: {e}")
            return None
    
    async def get_connection(self, user_id: str) -> Optional[DerivWebSocket]:
        """Get WebSocket connection for a user"""
        connection_id = self.user_connections.get(user_id)
        if connection_id and connection_id in self.connections:
            ws = self.connections[connection_id]
            if ws.is_connected:
                return ws
            else:
                # Clean up dead connection
                await self.close_connection(connection_id)
        
        return None
    
    async def close_connection(self, connection_id: str):
        """Close a WebSocket connection"""
        if connection_id in self.connections:
            ws = self.connections[connection_id]
            await ws.disconnect()
            del self.connections[connection_id]
            
            # Remove from user connections
            for user_id, conn_id in list(self.user_connections.items()):
                if conn_id == connection_id:
                    del self.user_connections[user_id]
                    break
            
            logger.info(f"Closed WebSocket connection {connection_id}")
    
    async def close_all_connections(self):
        """Close all WebSocket connections"""
        for connection_id in list(self.connections.keys()):
            await self.close_connection(connection_id)
    
    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]) -> bool:
        """Send a message to a specific user's connection"""
        ws = await self.get_connection(user_id)
        if ws:
            return await ws.send_message(message)
        return False


# Global WebSocket manager instance
websocket_manager = DerivWebSocketManager()