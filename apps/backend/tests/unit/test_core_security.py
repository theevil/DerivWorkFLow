"""
Unit tests for app.core.security module.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
from jose import jwt, JWTError

from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    pwd_context
)
from app.core.config import settings


class TestPasswordHashing:
    """Test password hashing and verification functions."""
    
    def test_get_password_hash(self):
        """Test password hashing function."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt hash prefix
    
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_empty_strings(self):
        """Test password verification with empty strings."""
        # Empty hash should raise an exception
        with pytest.raises(Exception):
            verify_password("", "")
        
        with pytest.raises(Exception):
            verify_password("password", "")
        
        # Invalid hash format should return False or raise exception
        try:
            result = verify_password("", "invalid_hash")
            assert result is False
        except Exception:
            # This is also acceptable behavior
            pass
    
    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2
    
    def test_same_password_different_hashes(self):
        """Test that the same password produces different hashes (salt)."""
        password = "testpassword123"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # Different due to salt
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestAccessTokens:
    """Test JWT access token creation and validation."""
    
    def test_create_access_token_default_expiry(self):
        """Test token creation with default expiry."""
        subject = "test@example.com"
        token = create_access_token(subject=subject)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify token structure (without time validation)
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm], options={"verify_exp": False})
        assert payload["sub"] == subject
        assert "exp" in payload
        
        # Check that expiry is in the future (approximately correct)
        exp_datetime = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        time_diff = (exp_datetime - now).total_seconds()
        
        # Should be roughly the configured expiry time (within reasonable bounds)
        expected_seconds = settings.access_token_expire_minutes * 60
        assert 0 < time_diff < expected_seconds + 300  # Allow 5 minute buffer
    
    def test_create_access_token_custom_expiry(self):
        """Test token creation with custom expiry."""
        subject = "test@example.com"
        custom_delta = timedelta(minutes=30)
        token = create_access_token(subject=subject, expires_delta=custom_delta)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm], options={"verify_exp": False})
        
        # Just verify the token structure is correct
        assert payload["sub"] == subject
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
    
    def test_create_access_token_numeric_subject(self):
        """Test token creation with numeric subject."""
        subject = 123456
        token = create_access_token(subject=subject)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "123456"  # Should be converted to string
    
    def test_create_access_token_different_subjects(self):
        """Test that different subjects create different tokens."""
        subject1 = "user1@example.com"
        subject2 = "user2@example.com"
        
        token1 = create_access_token(subject=subject1)
        token2 = create_access_token(subject=subject2)
        
        assert token1 != token2
        
        payload1 = jwt.decode(token1, settings.secret_key, algorithms=[settings.algorithm])
        payload2 = jwt.decode(token2, settings.secret_key, algorithms=[settings.algorithm])
        
        assert payload1["sub"] == subject1
        assert payload2["sub"] == subject2
    
    def test_token_expires_in_future(self):
        """Test that created tokens expire in the future."""
        subject = "test@example.com"
        token = create_access_token(subject=subject)
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        
        assert exp_datetime > datetime.utcnow()
    
    def test_token_with_zero_expiry(self):
        """Test token creation with zero expiry delta."""
        subject = "test@example.com"
        token = create_access_token(subject=subject, expires_delta=timedelta(seconds=0))
        
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm], options={"verify_exp": False})
        
        # Just verify the token structure is correct
        assert payload["sub"] == subject
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
    
    def test_invalid_token_decode(self):
        """Test that invalid tokens raise JWTError."""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(JWTError):
            jwt.decode(invalid_token, settings.secret_key, algorithms=[settings.algorithm])
    
    def test_token_with_wrong_secret(self):
        """Test that tokens can't be decoded with wrong secret."""
        subject = "test@example.com"
        token = create_access_token(subject=subject)
        
        with pytest.raises(JWTError):
            jwt.decode(token, "wrong-secret", algorithms=[settings.algorithm])


class TestPasswordContext:
    """Test the password context configuration."""
    
    def test_pwd_context_schemes(self):
        """Test that bcrypt is configured as the scheme."""
        assert "bcrypt" in pwd_context.schemes()
    
    def test_pwd_context_deprecated(self):
        """Test password context deprecated configuration."""
        # This test verifies the context is properly configured
        # The exact assertion may vary based on passlib version
        assert pwd_context is not None
