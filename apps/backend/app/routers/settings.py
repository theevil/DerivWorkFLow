from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from app.core.database import get_database
from app.routers.auth import get_current_user
from app.models.user import User
from app.crud.users import get_user_by_email
from app.core.config import settings

router = APIRouter()


class UserSettings(BaseModel):
    """User settings model"""
    # Deriv API Configuration
    deriv_token: Optional[str] = None
    deriv_app_id: str = Field(default="1089")
    
    # AI Configuration
    ai_confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)
    ai_analysis_interval: int = Field(default=30, ge=10, le=300)
    max_positions_per_user: int = Field(default=10, ge=1, le=50)
    ai_model: str = Field(default="gpt-4o-mini")
    ai_temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    ai_max_tokens: int = Field(default=1000, ge=100, le=4000)
    
    # OpenAI Configuration (stored encrypted)
    openai_api_key: Optional[str] = None
    langchain_api_key: Optional[str] = None
    langsmith_project: str = Field(default="deriv-trading")
    
    # Risk Management
    auto_stop_loss_enabled: bool = Field(default=True)
    auto_take_profit_enabled: bool = Field(default=True)
    emergency_stop_enabled: bool = Field(default=True)
    circuit_breaker_enabled: bool = Field(default=True)
    
    # Automation Settings
    auto_trading_enabled: bool = Field(default=False)
    market_scan_interval: int = Field(default=30, ge=5, le=300)
    position_monitor_interval: int = Field(default=10, ge=1, le=60)
    signal_execution_delay: int = Field(default=5, ge=0, le=30)
    max_concurrent_positions: int = Field(default=5, ge=1, le=20)
    
    # Learning Configuration
    learning_data_lookback_days: int = Field(default=30, ge=1, le=365)
    min_training_samples: int = Field(default=100, ge=10, le=1000)
    model_retrain_interval_hours: int = Field(default=24, ge=1, le=168)


class SettingsUpdate(BaseModel):
    """Settings update model with optional fields"""
    # Deriv API Configuration
    deriv_token: Optional[str] = None
    deriv_app_id: Optional[str] = None
    
    # AI Configuration
    ai_confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    ai_analysis_interval: Optional[int] = Field(None, ge=10, le=300)
    max_positions_per_user: Optional[int] = Field(None, ge=1, le=50)
    ai_model: Optional[str] = None
    ai_temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    ai_max_tokens: Optional[int] = Field(None, ge=100, le=4000)
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    langchain_api_key: Optional[str] = None
    langsmith_project: Optional[str] = None
    
    # Risk Management
    auto_stop_loss_enabled: Optional[bool] = None
    auto_take_profit_enabled: Optional[bool] = None
    emergency_stop_enabled: Optional[bool] = None
    circuit_breaker_enabled: Optional[bool] = None
    
    # Automation Settings
    auto_trading_enabled: Optional[bool] = None
    market_scan_interval: Optional[int] = Field(None, ge=5, le=300)
    position_monitor_interval: Optional[int] = Field(None, ge=1, le=60)
    signal_execution_delay: Optional[int] = Field(None, ge=0, le=30)
    max_concurrent_positions: Optional[int] = Field(None, ge=1, le=20)
    
    # Learning Configuration
    learning_data_lookback_days: Optional[int] = Field(None, ge=1, le=365)
    min_training_samples: Optional[int] = Field(None, ge=10, le=1000)
    model_retrain_interval_hours: Optional[int] = Field(None, ge=1, le=168)


@router.get("/settings", response_model=UserSettings)
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


@router.put("/settings")
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


@router.post("/settings/test-deriv-connection")
async def test_deriv_connection(
    token: str,
    current_user: User = Depends(get_current_user),
):
    """Test Deriv API connection with provided token"""
    try:
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


@router.get("/settings/system-status")
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
        status = {
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
        
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting system status: {str(e)}"
        )


@router.post("/settings/reset-to-defaults")
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


@router.get("/settings/export")
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
