"""
Unit tests for app.routers.auth module.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from fastapi import FastAPI
from bson import ObjectId

from app.routers.auth import (
    router,
    get_current_user,
    get_current_user_from_token,
    oauth2_scheme
)
from app.models.user import User, UserCreate, UserInDB


class TestAuthDependencies:
    """Test authentication dependencies."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Test getting current user with valid token."""
        mock_db = AsyncMock()
        valid_token = "valid_token"
        
        user_data = UserInDB(
            _id=ObjectId(),
            email="test@example.com",
            name="Test User",
            hashed_password="$2b$12$hash",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        with patch('app.routers.auth.jwt.decode') as mock_decode:
            with patch('app.routers.auth.get_user_by_email') as mock_get_user:
                mock_decode.return_value = {"sub": "test@example.com"}
                mock_get_user.return_value = user_data
                
                result = await get_current_user(valid_token, mock_db)
                
                assert isinstance(result, User)
                assert result.email == "test@example.com"
                assert result.name == "Test User"
                assert not hasattr(result, 'hashed_password')  # Should not expose password
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        mock_db = AsyncMock()
        invalid_token = "invalid_token"
        
        with patch('app.routers.auth.jwt.decode') as mock_decode:
            from jose import JWTError
            mock_decode.side_effect = JWTError("Invalid token")
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(invalid_token, mock_db)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Could not validate credentials"
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_subject(self):
        """Test getting current user when token has no subject."""
        mock_db = AsyncMock()
        token = "token_without_sub"
        
        with patch('app.routers.auth.jwt.decode') as mock_decode:
            mock_decode.return_value = {}  # No 'sub' field
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token, mock_db)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self):
        """Test getting current user when user doesn't exist."""
        mock_db = AsyncMock()
        token = "valid_token"
        
        with patch('app.routers.auth.jwt.decode') as mock_decode:
            with patch('app.routers.auth.get_user_by_email') as mock_get_user:
                mock_decode.return_value = {"sub": "nonexistent@example.com"}
                mock_get_user.return_value = None
                
                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(token, mock_db)
                
                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_current_user_from_token_valid(self):
        """Test getting current user from token (WebSocket use)."""
        token = "valid_token"
        
        user_data = UserInDB(
            _id=ObjectId(),
            email="test@example.com",
            name="Test User",
            hashed_password="$2b$12$hash",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        with patch('app.routers.auth.jwt.decode') as mock_decode:
            with patch('app.routers.auth.get_database') as mock_get_db:
                with patch('app.routers.auth.get_user_by_email') as mock_get_user:
                    mock_decode.return_value = {"sub": "test@example.com"}
                    mock_get_db.return_value = AsyncMock()
                    mock_get_user.return_value = user_data
                    
                    result = await get_current_user_from_token(token)
                    
                    assert isinstance(result, User)
                    assert result.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_current_user_from_token_invalid(self):
        """Test getting current user from invalid token."""
        invalid_token = "invalid_token"
        
        with patch('app.routers.auth.jwt.decode') as mock_decode:
            from jose import JWTError
            mock_decode.side_effect = JWTError("Invalid token")
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_from_token(invalid_token)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthRoutes:
    """Test authentication routes."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)
    
    def test_login_success(self):
        """Test successful login."""
        user_data = UserInDB(
            _id=ObjectId(),
            email="test@example.com",
            name="Test User",
            hashed_password="$2b$12$hash",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        with patch('app.routers.auth.get_database') as mock_get_db:
            with patch('app.routers.auth.authenticate_user') as mock_auth:
                with patch('app.routers.auth.create_access_token') as mock_create_token:
                    mock_get_db.return_value = AsyncMock()
                    mock_auth.return_value = user_data
                    mock_create_token.return_value = "access_token_123"
                    
                    response = self.client.post(
                        "/token",
                        data={"username": "test@example.com", "password": "password123"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    assert "access_token" in data
                    assert data["access_token"] == "access_token_123"
                    assert data["token_type"] == "bearer"
                    assert "user" in data
                    assert data["user"]["email"] == "test@example.com"
                    assert data["user"]["name"] == "Test User"
                    assert "hashed_password" not in data["user"]
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        with patch('app.routers.auth.get_database') as mock_get_db:
            with patch('app.routers.auth.authenticate_user') as mock_auth:
                mock_get_db.return_value = AsyncMock()
                mock_auth.return_value = None  # Authentication failed
                
                response = self.client.post(
                    "/token",
                    data={"username": "test@example.com", "password": "wrongpassword"}
                )
                
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
                data = response.json()
                assert data["detail"] == "Incorrect email or password"
    
    def test_login_missing_credentials(self):
        """Test login with missing credentials."""
        # Missing password
        response = self.client.post(
            "/token",
            data={"username": "test@example.com"}
        )
        assert response.status_code == 422  # Validation error
        
        # Missing username
        response = self.client.post(
            "/token",
            data={"password": "password123"}
        )
        assert response.status_code == 422  # Validation error
    
    def test_login_empty_credentials(self):
        """Test login with empty credentials."""
        # Mock dependency injection for database 
        from app.core.database import get_database
        
        def override_get_database():
            return AsyncMock()
        
        self.app.dependency_overrides[get_database] = override_get_database
        
        try:
            with patch('app.routers.auth.authenticate_user') as mock_auth:
                mock_auth.return_value = None
                
                response = self.client.post(
                    "/token",
                    data={"username": "", "password": ""}
                )
                
                assert response.status_code == status.HTTP_401_UNAUTHORIZED
        finally:
            # Clean up dependency override
            self.app.dependency_overrides.clear()
    
    def test_register_success(self):
        """Test successful user registration."""
        user_create_data = {
            "email": "newuser@example.com",
            "name": "New User",
            "password": "password123"
        }
        
        created_user = UserInDB(
            _id=ObjectId(),
            email="newuser@example.com",
            name="New User",
            hashed_password="$2b$12$hash",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        with patch('app.routers.auth.get_database') as mock_get_db:
            with patch('app.routers.auth.get_user_by_email') as mock_get_user:
                with patch('app.routers.auth.create_user') as mock_create_user:
                    mock_get_db.return_value = AsyncMock()
                    mock_get_user.return_value = None  # User doesn't exist
                    mock_create_user.return_value = created_user
                    
                    response = self.client.post("/register", json=user_create_data)
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    assert data["email"] == "newuser@example.com"
                    assert data["name"] == "New User"
                    assert "id" in data
                    assert "created_at" in data
                    assert "updated_at" in data
                    assert "hashed_password" not in data
    
    def test_register_email_already_exists(self):
        """Test registration with existing email."""
        user_create_data = {
            "email": "existing@example.com",
            "name": "Existing User",
            "password": "password123"
        }
        
        existing_user = UserInDB(
            _id=ObjectId(),
            email="existing@example.com",
            name="Existing User",
            hashed_password="$2b$12$hash",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        with patch('app.routers.auth.get_database') as mock_get_db:
            with patch('app.routers.auth.get_user_by_email') as mock_get_user:
                mock_get_db.return_value = AsyncMock()
                mock_get_user.return_value = existing_user  # User already exists
                
                response = self.client.post("/register", json=user_create_data)
                
                assert response.status_code == status.HTTP_400_BAD_REQUEST
                data = response.json()
                assert data["detail"] == "Email already registered"
    
    def test_register_invalid_email(self):
        """Test registration with invalid email."""
        user_create_data = {
            "email": "invalid-email",
            "name": "User",
            "password": "password123"
        }
        
        response = self.client.post("/register", json=user_create_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    def test_register_missing_fields(self):
        """Test registration with missing required fields."""
        # Missing email
        response = self.client.post("/register", json={
            "name": "User",
            "password": "password123"
        })
        assert response.status_code == 422
        
        # Missing name
        response = self.client.post("/register", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 422
        
        # Missing password
        response = self.client.post("/register", json={
            "email": "test@example.com",
            "name": "User"
        })
        assert response.status_code == 422
    
    def test_register_empty_fields(self):
        """Test registration with empty fields."""
        user_create_data = {
            "email": "",
            "name": "",
            "password": ""
        }
        
        response = self.client.post("/register", json=user_create_data)
        
        assert response.status_code == 422  # Validation error


class TestAuthRouterIntegration:
    """Integration tests for auth router."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)
    
    def test_register_then_login_flow(self):
        """Test complete registration and login flow."""
        user_data = {
            "email": "testuser@example.com",
            "name": "Test User",
            "password": "password123"
        }
        
        created_user = UserInDB(
            _id=ObjectId(),
            email="testuser@example.com",
            name="Test User",
            hashed_password="$2b$12$hash",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        with patch('app.routers.auth.get_database') as mock_get_db:
            with patch('app.routers.auth.get_user_by_email') as mock_get_user:
                with patch('app.routers.auth.create_user') as mock_create_user:
                    with patch('app.routers.auth.authenticate_user') as mock_auth:
                        with patch('app.routers.auth.create_access_token') as mock_create_token:
                            mock_get_db.return_value = AsyncMock()
                            
                            # Registration
                            mock_get_user.return_value = None  # User doesn't exist
                            mock_create_user.return_value = created_user
                            
                            register_response = self.client.post("/register", json=user_data)
                            assert register_response.status_code == 200
                            
                            # Login
                            mock_auth.return_value = created_user
                            mock_create_token.return_value = "access_token_123"
                            
                            login_response = self.client.post(
                                "/token",
                                data={"username": "testuser@example.com", "password": "password123"}
                            )
                            
                            assert login_response.status_code == 200
                            login_data = login_response.json()
                            
                            assert "access_token" in login_data
                            assert login_data["user"]["email"] == "testuser@example.com"
    
    def test_protected_route_with_valid_token(self):
        """Test accessing a protected route with valid token."""
        # First, create a simple protected route for testing
        from fastapi import Depends
        
        @self.app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id, "email": current_user.email}
        
        user_data = UserInDB(
            _id=ObjectId(),
            email="test@example.com",
            name="Test User",
            hashed_password="$2b$12$hash",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        with patch('app.routers.auth.jwt.decode') as mock_decode:
            with patch('app.routers.auth.get_user_by_email') as mock_get_user:
                with patch('app.routers.auth.get_database') as mock_get_db:
                    mock_decode.return_value = {"sub": "test@example.com"}
                    mock_get_user.return_value = user_data
                    mock_get_db.return_value = AsyncMock()
                    
                    response = self.client.get(
                        "/protected",
                        headers={"Authorization": "Bearer valid_token"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["email"] == "test@example.com"
    
    def test_protected_route_without_token(self):
        """Test accessing a protected route without token."""
        from fastapi import Depends
        
        @self.app.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user_id": current_user.id}
        
        response = self.client.get("/protected")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestOAuth2Scheme:
    """Test OAuth2 scheme configuration."""
    
    def test_oauth2_scheme_token_url(self):
        """Test that OAuth2 scheme has correct token URL."""
        assert oauth2_scheme.model.flows.password.tokenUrl == "token"
    
    def test_oauth2_scheme_type(self):
        """Test OAuth2 scheme type."""
        from fastapi.security import OAuth2PasswordBearer
        assert isinstance(oauth2_scheme, OAuth2PasswordBearer)
