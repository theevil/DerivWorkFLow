import random
import time
from typing import Dict, List
from fastapi import APIRouter, Depends
from loguru import logger

from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter()

# Simulated market data
MARKET_DATA = {
    'R_10': {'base_price': 1.2345, 'volatility': 0.002},
    'R_25': {'base_price': 2.3456, 'volatility': 0.005},
    'R_50': {'base_price': 3.4567, 'volatility': 0.008},
    'R_75': {'base_price': 4.5678, 'volatility': 0.012},
    'R_100': {'base_price': 5.6789, 'volatility': 0.015},
    'BOOM_1000': {'base_price': 1000.0, 'volatility': 50.0},
    'CRASH_1000': {'base_price': 1000.0, 'volatility': 50.0},
    'STEP_10': {'base_price': 10.0, 'volatility': 0.1},
    'STEP_25': {'base_price': 25.0, 'volatility': 0.25},
}


def generate_tick_data(symbol: str) -> Dict:
    """Generate simulated tick data for a symbol"""
    if symbol not in MARKET_DATA:
        symbol = 'R_10'  # Default fallback
    
    base_data = MARKET_DATA[symbol]
    base_price = base_data['base_price']
    volatility = base_data['volatility']
    
    # Generate random price movement
    change = random.uniform(-volatility, volatility)
    new_price = base_price + change
    
    # Ensure price doesn't go negative
    new_price = max(new_price, base_price * 0.1)
    
    # Update base price for next tick (random walk)
    MARKET_DATA[symbol]['base_price'] = new_price
    
    return {
        'symbol': symbol,
        'tick': round(new_price, 5),
        'ask': round(new_price + volatility * 0.1, 5),
        'bid': round(new_price - volatility * 0.1, 5),
        'quote': round(new_price, 5),
        'epoch': int(time.time()),
        'timestamp': int(time.time() * 1000)
    }


@router.get("/symbols")
async def get_available_symbols(current_user: User = Depends(get_current_user)):
    """Get list of available trading symbols"""
    return {
        "symbols": list(MARKET_DATA.keys()),
        "count": len(MARKET_DATA)
    }


@router.get("/tick/{symbol}")
async def get_current_tick(symbol: str, current_user: User = Depends(get_current_user)):
    """Get current tick data for a symbol"""
    if symbol not in MARKET_DATA:
        return {"error": "Symbol not found"}
    
    tick_data = generate_tick_data(symbol)
    logger.info(f"Generated tick for {symbol}: {tick_data['tick']}")
    
    return tick_data


@router.get("/ticks")
async def get_all_ticks(current_user: User = Depends(get_current_user)):
    """Get current tick data for all symbols"""
    ticks = {}
    for symbol in MARKET_DATA.keys():
        ticks[symbol] = generate_tick_data(symbol)
    
    return {
        "ticks": ticks,
        "timestamp": int(time.time())
    }


@router.get("/history/{symbol}")
async def get_price_history(
    symbol: str, 
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get historical price data for a symbol (simulated)"""
    if symbol not in MARKET_DATA:
        return {"error": "Symbol not found"}
    
    # Generate simulated historical data
    base_data = MARKET_DATA[symbol]
    base_price = base_data['base_price']
    volatility = base_data['volatility']
    
    history = []
    current_time = int(time.time())
    
    for i in range(limit):
        timestamp = current_time - (limit - i) * 60  # 1 minute intervals
        change = random.uniform(-volatility, volatility)
        price = base_price + change + random.uniform(-volatility * 0.5, volatility * 0.5)
        price = max(price, base_price * 0.5)  # Ensure reasonable bounds
        
        history.append({
            "timestamp": timestamp,
            "price": round(price, 5),
            "volume": random.randint(10, 1000)
        })
    
    return {
        "symbol": symbol,
        "history": history,
        "count": len(history)
    }


@router.get("/market-status")
async def get_market_status(current_user: User = Depends(get_current_user)):
    """Get overall market status"""
    return {
        "status": "open",
        "session": "london",
        "next_close": int(time.time()) + 3600,  # 1 hour from now
        "timezone": "UTC",
        "active_symbols": len(MARKET_DATA),
        "message": "Markets are open for trading"
    }
