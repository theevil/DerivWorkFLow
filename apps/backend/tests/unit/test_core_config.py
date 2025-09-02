"""
Unit tests for app.core.config module.
"""

import os
from unittest.mock import patch

import pytest

from app.core.config import Settings, settings


class TestSettings:
    """Test the Settings class."""

    def test_default_values(self):
        """Test that default values are correctly set."""
        test_settings = Settings()

        assert test_settings.app_name == "Deriv Workflow API"
        assert test_settings.api_v1_prefix == "/api/v1"
        assert test_settings.algorithm == "HS256"
        assert test_settings.access_token_expire_minutes == 1440  # 24 hours
        assert test_settings.deriv_app_id == "1089"
        assert test_settings.log_level == "INFO"
        assert test_settings.rate_limit_requests == 100
        assert test_settings.rate_limit_window == 60
        assert test_settings.ai_confidence_threshold == 0.6
        assert test_settings.ai_analysis_interval == 30
        assert test_settings.max_positions_per_user == 10

    def test_cors_origins(self):
        """Test CORS origins configuration."""
        test_settings = Settings()

        expected_origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]

        assert test_settings.backend_cors_origins == expected_origins

    @patch.dict(os.environ, {
        "ENVIRONMENT": "production",
        "DEBUG": "true",
        "SECRET_KEY": "prod-secret-key",  # pragma: allowlist secret
        "MONGODB_URI": "mongodb://prod-db:27017",
        "MONGODB_DB": "deriv_prod",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "120",
        "DERIV_APP_ID": "12345",
        "LOG_LEVEL": "ERROR",
        "RATE_LIMIT_REQUESTS": "200",
        "RATE_LIMIT_WINDOW": "30",
        "AI_CONFIDENCE_THRESHOLD": "0.8",
        "AI_ANALYSIS_INTERVAL": "60",
        "MAX_POSITIONS_PER_USER": "20"
    })
    def test_environment_variables_override(self):
        """Test that environment variables override default values."""
        test_settings = Settings()

        assert test_settings.environment == "production"
        assert test_settings.debug is True
        assert test_settings.secret_key == "prod-secret-key"
        assert test_settings.mongodb_uri == "mongodb://prod-db:27017"
        assert test_settings.mongodb_db == "deriv_prod"
        assert test_settings.access_token_expire_minutes == 120
        assert test_settings.deriv_app_id == "12345"
        assert test_settings.log_level == "ERROR"
        assert test_settings.rate_limit_requests == 200
        assert test_settings.rate_limit_window == 30
        assert test_settings.ai_confidence_threshold == 0.8
        assert test_settings.ai_analysis_interval == 60
        assert test_settings.max_positions_per_user == 20

    @patch.dict(os.environ, {"DEBUG": "false"})
    def test_debug_false_conversion(self):
        """Test that DEBUG=false is converted to False boolean."""
        test_settings = Settings()
        assert test_settings.debug is False

    @patch.dict(os.environ, {"DEBUG": "true"})
    def test_debug_true_conversion(self):
        """Test that DEBUG=true is converted to True boolean."""
        test_settings = Settings()
        assert test_settings.debug is True

    @patch.dict(os.environ, {"DEBUG": "invalid"})
    def test_debug_invalid_value(self):
        """Test that invalid DEBUG values raise validation error."""
        with pytest.raises(Exception):  # Pydantic will raise ValidationError
            Settings()

    def test_settings_singleton(self):
        """Test that the settings instance is properly configured."""
        assert settings is not None
        assert isinstance(settings, Settings)
        assert hasattr(settings, "app_name")
        assert hasattr(settings, "mongodb_uri")
        assert hasattr(settings, "secret_key")

    def test_case_sensitive_config(self):
        """Test that config is case insensitive as specified."""
        # This test verifies the Config class setting
        test_settings = Settings()
        assert test_settings.Config.case_sensitive is False

    def test_env_file_config(self):
        """Test that env_file is properly configured."""
        test_settings = Settings()
        assert test_settings.Config.env_file == ".env"
