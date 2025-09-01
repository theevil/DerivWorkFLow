import json
import asyncio
from typing import Any, Callable, Dict, Optional
import websockets
from loguru import logger

class DerivWebSocket:
    def __init__(self, app_id: str, api_token: Optional[str] = None):
        self.app_id = app_id
        self.api_token = api_token
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.callbacks: Dict[str, Callable] = {}
        self.connected = False
        self.authorized = False
        self._connect_lock = asyncio.Lock()
        
    async def connect(self) -> None:
        if self.connected:
            return
            
        async with self._connect_lock:
            if self.connected:  # Double check after acquiring lock
                return
                
            try:
                self.ws = await websockets.connect(
                    f'wss://ws.binaryws.com/websockets/v3?app_id={self.app_id}'
                )
                self.connected = True
                logger.info("Connected to Deriv WebSocket API")
                
                if self.api_token:
                    await self.authorize(self.api_token)
                    
                # Start message handler
                asyncio.create_task(self._message_handler())
                
            except Exception as e:
                logger.error(f"Failed to connect to Deriv WebSocket: {e}")
                self.connected = False
                raise
    
    async def authorize(self, api_token: str) -> None:
        if not self.connected:
            await self.connect()
            
        auth_request = {
            "authorize": api_token
        }
        
        response = await self.send_request(auth_request)
        if response.get("msg_type") == "authorize":
            self.authorized = True
            self.api_token = api_token
            logger.info("Successfully authorized with Deriv API")
        else:
            logger.error(f"Authorization failed: {response}")
            raise Exception("Failed to authorize with Deriv API")
    
    async def subscribe_ticks(self, symbol: str) -> None:
        if not self.connected:
            await self.connect()
            
        request = {
            "ticks": symbol,
            "subscribe": 1
        }
        await self.send_request(request)
        logger.info(f"Subscribed to ticks for {symbol}")
    
    async def buy_contract(
        self,
        contract_type: str,
        symbol: str,
        amount: float,
        duration: int,
        duration_unit: str = "m"
    ) -> Dict[str, Any]:
        if not self.authorized:
            raise Exception("Must be authorized to buy contracts")
            
        request = {
            "buy": "1",
            "price": amount,
            "parameters": {
                "amount": amount,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": duration,
                "duration_unit": duration_unit,
                "symbol": symbol
            }
        }
        
        response = await self.send_request(request)
        if response.get("msg_type") == "buy":
            logger.info(f"Successfully bought contract: {response['buy']}")
            return response["buy"]
        else:
            logger.error(f"Failed to buy contract: {response}")
            raise Exception("Failed to buy contract")
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if not self.connected or not self.ws:
            await self.connect()
            
        try:
            await self.ws.send(json.dumps(request))
            response = await self.ws.recv()
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error sending request to Deriv API: {e}")
            raise
    
    async def _message_handler(self) -> None:
        if not self.ws:
            return
            
        try:
            while True:
                message = await self.ws.recv()
                data = json.loads(message)
                msg_type = data.get("msg_type")
                
                if msg_type in self.callbacks:
                    await self.callbacks[msg_type](data)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Deriv WebSocket connection closed")
            self.connected = False
            self.authorized = False
        except Exception as e:
            logger.error(f"Error in message handler: {e}")
            self.connected = False
            self.authorized = False
    
    def on(self, msg_type: str, callback: Callable) -> None:
        """Register a callback for a specific message type"""
        self.callbacks[msg_type] = callback
    
    async def close(self) -> None:
        """Close the WebSocket connection"""
        if self.ws:
            await self.ws.close()
        self.connected = False
        self.authorized = False
        logger.info("Closed Deriv WebSocket connection")
