from fastapi import APIRouter, Depends, HTTPException, WebSocket, status
from app.core.database import get_database
from app.core.deriv import DerivWebSocket
from app.crud.users import get_user_by_email
from app.models.user import User
from app.routers.auth import get_current_user
from app.models import DerivTokenRequest

router = APIRouter()

# Store WebSocket connections per user
user_connections: dict[str, DerivWebSocket] = {}

@router.post("/token")
async def set_deriv_token(
    token_request: DerivTokenRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Set or update a user's Deriv API token"""
    try:
        token = token_request.token
        # Test the token by creating a connection
        ws = DerivWebSocket(app_id="1089", api_token=token)
        await ws.connect()
        await ws.authorize(token)
        await ws.disconnect()

        # Update user's token in database
        user = await get_user_by_email(db, current_user.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.deriv_token = token
        await db.users.update_one(
            {"email": user.email},
            {"$set": {"deriv_token": token}}
        )

        return {"message": "Deriv API token updated successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Deriv API token: {str(e)}"
        )

@router.websocket("/ws/deriv/{user_id}")
async def deriv_websocket(
    websocket: WebSocket,
    user_id: str,
    db = Depends(get_database),
):
    """WebSocket endpoint for real-time Deriv data"""
    await websocket.accept()

    try:
        # Get user and validate
        user = await get_user_by_email(db, user_id)
        if not user or not user.deriv_token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Create Deriv connection if doesn't exist
        if user_id not in user_connections:
            deriv_ws = DerivWebSocket(app_id="1089", api_token=user.deriv_token)
            await deriv_ws.connect()
            await deriv_ws.authorize(user.deriv_token)
            user_connections[user_id] = deriv_ws

        deriv_ws = user_connections[user_id]

        # Handle incoming messages
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "subscribe_ticks":
                symbol = data.get("symbol")
                if symbol:
                    await deriv_ws.subscribe_ticks(symbol)

            elif data.get("type") == "buy":
                params = data.get("params", {})
                result = await deriv_ws.buy_contract(
                    contract_type=params.get("contract_type"),
                    symbol=params.get("symbol"),
                    amount=params.get("amount"),
                    duration=params.get("duration"),
                    duration_unit=params.get("duration_unit", "m")
                )
                await websocket.send_json({"type": "buy_result", "data": result})

    except Exception:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

    finally:
        # Cleanup connection
        if user_id in user_connections:
            await user_connections[user_id].disconnect()
            del user_connections[user_id]
