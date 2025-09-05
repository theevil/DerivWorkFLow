"""
AI Configuration Manager for DerivWorkFlow

This module manages AI provider selection and configuration across the platform.
It allows users to dynamically switch between different AI providers and ensures
consistency across all AI operations.
"""

from typing import Optional, Dict, Any
from enum import Enum
from loguru import logger

from app.core.database import get_database
from app.crud.users import get_user_settings, update_user_settings


class AIProvider(str, Enum):
    """Available AI providers"""
    LOCAL = "local"
    OPENAI = "openai"
    HYBRID = "hybrid"


class AIConfigManager:
    """
    Centralized AI configuration manager that handles provider selection
    and ensures consistency across all AI operations
    """

    def __init__(self):
        self._provider_configs = {
            AIProvider.LOCAL: {
                "name": "Local AI",
                "description": "Local models running on your machine",
                "recommended": True,
                "cost": "Free",
                "latency": "Low",
                "privacy": "High"
            },
            AIProvider.OPENAI: {
                "name": "OpenAI",
                "description": "Cloud-based AI models via OpenAI API",
                "recommended": False,
                "cost": "Per token",
                "latency": "Medium",
                "privacy": "Medium"
            },
            AIProvider.HYBRID: {
                "name": "Hybrid",
                "description": "Combines local and cloud AI for optimal performance",
                "recommended": False,
                "cost": "Mixed",
                "latency": "Low-Medium",
                "privacy": "High"
            }
        }

    async def get_user_ai_config(self, user_id: str) -> dict[str, Any]:
        """
        Get AI configuration for a specific user
        """
        try:
            db = await get_database()
            user_settings = await get_user_settings(user_id, db)

            if not user_settings:
                # Return default configuration
                return self._get_default_config()

            return {
                "provider": user_settings.get("ai_provider", AIProvider.LOCAL),
                "confidence_threshold": user_settings.get("ai_confidence_threshold", 0.6),
                "analysis_interval": user_settings.get("ai_analysis_interval", 30),
                "temperature": user_settings.get("ai_temperature", 0.1),
                "max_tokens": user_settings.get("ai_max_tokens", 1000),
                "local_ai_enabled": user_settings.get("local_ai_enabled", True),
                "local_ai_model": user_settings.get("local_ai_model", "phi-3-mini"),
                "openai_api_key": user_settings.get("openai_api_key"),
                "langchain_api_key": user_settings.get("langchain_api_key"),
                "langsmith_project": user_settings.get("langsmith_project", "deriv-trading")
            }
        except Exception as e:
            logger.error(f"Error getting user AI config: {e}")
            return self._get_default_config()

    async def update_user_ai_config(self, user_id: str, config: dict[str, Any]) -> bool:
        """
        Update AI configuration for a specific user
        """
        try:
            db = await get_database()

            # Validate provider
            if "ai_provider" in config:
                if config["ai_provider"] not in [p.value for p in AIProvider]:
                    raise ValueError(f"Invalid AI provider: {config['ai_provider']}")

            # Update settings
            success = await update_user_settings(user_id, config, db)

            if success:
                logger.info(f"Updated AI config for user {user_id}: {config}")
                return True
            else:
                logger.error(f"Failed to update AI config for user {user_id}")
                return False

        except Exception as e:
            logger.error(f"Error updating user AI config: {e}")
            return False

    def get_available_providers(self) -> dict[str, dict[str, Any]]:
        """
        Get information about all available AI providers
        """
        return self._provider_configs

    def get_provider_info(self, provider: str) -> Optional[dict[str, Any]]:
        """
        Get information about a specific AI provider
        """
        return self._provider_configs.get(provider)

    def is_provider_available(self, provider: str) -> bool:
        """
        Check if a specific AI provider is available
        """
        return provider in self._provider_configs

    def _get_default_config(self) -> dict[str, Any]:
        """
        Get default AI configuration
        """
        return {
            "provider": AIProvider.LOCAL,
            "confidence_threshold": 0.6,
            "analysis_interval": 30,
            "temperature": 0.1,
            "max_tokens": 1000,
            "local_ai_enabled": True,
            "local_ai_model": "phi-3-mini",
            "openai_api_key": None,
            "langchain_api_key": None,
            "langsmith_project": "deriv-trading"
        }

    async def validate_provider_config(self, provider: str, config: dict[str, Any]) -> dict[str, Any]:
        """
        Validate configuration for a specific provider
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }

        if provider == AIProvider.LOCAL:
            # Validate local AI configuration
            if not config.get("local_ai_enabled", False):
                validation_result["errors"].append("Local AI must be enabled for local provider")
                validation_result["valid"] = False

            if not config.get("local_ai_model"):
                validation_result["errors"].append("Local AI model must be specified")
                validation_result["valid"] = False

        elif provider == AIProvider.OPENAI:
            # Validate OpenAI configuration
            if not config.get("openai_api_key"):
                validation_result["errors"].append("OpenAI API key is required")
                validation_result["valid"] = False

            if not config.get("ai_model"):
                validation_result["warnings"].append("AI model not specified, using default")

        elif provider == AIProvider.HYBRID:
            # Validate hybrid configuration
            if not config.get("local_ai_enabled", False):
                validation_result["warnings"].append("Local AI should be enabled for hybrid mode")

            if not config.get("openai_api_key"):
                validation_result["warnings"].append("OpenAI API key recommended for hybrid mode")

        return validation_result


# Global instance
ai_config_manager = AIConfigManager()
