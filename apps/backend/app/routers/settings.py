from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.database import get_database

from app.models.user import User
from app.routers.auth import get_current_user
from app.models import DerivTokenRequest, UserSettings, SettingsUpdate

router = APIRouter()

@router.get("/test")
async def test_settings_endpoint():
    """Test endpoint to verify settings router is working"""
    return {"message": "Settings router is working correctly"}




@router.get("/", response_model=UserSettings)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Get current user settings"""
    try:
        # Get user from database
        user_doc = await db.users.find_one({"email": current_user.email})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user settings (with defaults if not set)
        user_settings = user_doc.get("settings", {})

        # Merge with default values
        settings_data = UserSettings()

        # Update with stored values
        for field_name, field_value in user_settings.items():
            if hasattr(settings_data, field_name):
                setattr(settings_data, field_name, field_value)

        # Add deriv_token from user document
        if user_doc.get("deriv_token"):
            settings_data.deriv_token = "***configured***"  # Don't send actual token

        return settings_data

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving settings: {str(e)}"
        )


@router.put("/")
async def update_user_settings(
    settings_update: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Update user settings"""
    try:
        # Get current user document
        user_doc = await db.users.find_one({"email": current_user.email})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        # Prepare update data
        update_data = {}

        # Convert SettingsUpdate to dict, excluding None values
        settings_dict = settings_update.model_dump(exclude_none=True)

        # Handle deriv_token separately
        if "deriv_token" in settings_dict:
            deriv_token = settings_dict.pop("deriv_token")
            if deriv_token and deriv_token != "***configured***":
                # Validate token before saving
                from app.core.deriv import DerivWebSocket
                try:
                    ws = DerivWebSocket(api_token=deriv_token)
                    await ws.connect()
                    await ws.authorize(deriv_token)
                    await ws.disconnect()
                    update_data["deriv_token"] = deriv_token
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid Deriv API token: {str(e)}"
                    )

        # Store other settings in settings object
        if settings_dict:
            current_settings = user_doc.get("settings", {})
            current_settings.update(settings_dict)
            update_data["settings"] = current_settings

        # Update user document
        if update_data:
            await db.users.update_one(
                {"email": current_user.email},
                {"$set": update_data}
            )

        return {"message": "Settings updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating settings: {str(e)}"
        )


@router.post("/test-deriv-connection")
async def test_deriv_connection(
    token_request: DerivTokenRequest,
    current_user: User = Depends(get_current_user),
):
    """Test Deriv API connection with provided token"""
    try:
        token = token_request.token
        from app.core.deriv import DerivWebSocket

        # Test connection
        ws = DerivWebSocket(api_token=token)
        await ws.connect()
        await ws.authorize(token)

        # Get basic account info to verify connection
        await ws.get_account_info()
        await ws.disconnect()

        return {
            "status": "success",
            "message": "Deriv API connection successful"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Deriv API connection failed: {str(e)}"
        )


@router.get("/system-status")
async def get_system_status(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Get system configuration status"""
    try:
        # Get user from database
        user_doc = await db.users.find_one({"email": current_user.email})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        user_settings = user_doc.get("settings", {})

        # Check various configurations
        status_info = {
            "deriv_api": {
                "configured": bool(user_doc.get("deriv_token")),
                "status": "connected" if user_doc.get("deriv_token") else "not_configured"
            },
            "openai_api": {
                "configured": bool(user_settings.get("openai_api_key") or settings.openai_api_key),
                "status": "configured" if user_settings.get("openai_api_key") or settings.openai_api_key else "not_configured"
            },
            "langchain_api": {
                "configured": bool(user_settings.get("langchain_api_key") or settings.langchain_api_key),
                "status": "configured" if user_settings.get("langchain_api_key") or settings.langchain_api_key else "not_configured"
            },
            "auto_trading": {
                "enabled": user_settings.get("auto_trading_enabled", False),
                "status": "enabled" if user_settings.get("auto_trading_enabled", False) else "disabled"
            },
            "risk_management": {
                "stop_loss": user_settings.get("auto_stop_loss_enabled", True),
                "take_profit": user_settings.get("auto_take_profit_enabled", True),
                "emergency_stop": user_settings.get("emergency_stop_enabled", True),
                "circuit_breaker": user_settings.get("circuit_breaker_enabled", True)
            }
        }

        return status_info

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting system status: {str(e)}"
        )


@router.post("/reset-to-defaults")
async def reset_settings_to_defaults(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Reset user settings to default values"""
    try:
        # Reset to default settings (keep deriv_token)
        default_settings = UserSettings().model_dump()

        # Remove fields that shouldn't be reset
        default_settings.pop("deriv_token", None)
        default_settings.pop("deriv_app_id", None)

        await db.users.update_one(
            {"email": current_user.email},
            {"$set": {"settings": default_settings}}
        )

        return {"message": "Settings reset to defaults successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting settings: {str(e)}"
        )


@router.get("/export")
async def export_user_settings(
    current_user: User = Depends(get_current_user),
    db = Depends(get_database),
):
    """Export user settings for backup"""
    try:
        user_doc = await db.users.find_one({"email": current_user.email})
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        # Get settings without sensitive data
        settings_export = user_doc.get("settings", {})

        # Remove sensitive keys
        sensitive_keys = ["openai_api_key", "langchain_api_key", "deriv_token"]
        for key in sensitive_keys:
            settings_export.pop(key, None)

        return {
            "user_id": str(user_doc["_id"]),
            "exported_at": "2024-01-01T00:00:00Z",  # You might want to use datetime.utcnow()
            "settings": settings_export
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting settings: {str(e)}"
        )
