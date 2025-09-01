"""
Pytest configuration and fixtures for the entire test suite.
"""

import asyncio
import pytest
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.core.config import settings
from app.core.database import db
from app.core.security import create_access_token, get_password_hash
from app.models.user import UserInDB
from app.models.trading import TradingParametersInDB, TradePositionInDB


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def mock_db():
    """Mock database for testing."""
    # Use mongomock for testing
    client = AsyncMongoMockClient()
    db.client = client
    
    yield db.get_db()
    
    # Clean up
    await client.close()


@pytest.fixture(scope="function")
def client() -> Generator:
    """Test client for synchronous API calls."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator:
    """Async test client for API calls."""
    async with AsyncClient(base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def test_user(mock_db):
    """Create a test user in the database."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "hashed_password": get_password_hash("testpass123"),
        "deriv_token": None
    }
    
    user_doc = UserInDB(**user_data)
    result = await mock_db.users.insert_one(user_doc.model_dump(by_alias=True))
    user_data["_id"] = result.inserted_id
    
    return UserInDB(**user_data)


@pytest.fixture(scope="function")
async def authenticated_user(test_user):
    """Create an authenticated user with JWT token."""
    access_token = create_access_token(subject=str(test_user.id))
    return {
        "user": test_user,
        "token": access_token,
        "headers": {"Authorization": f"Bearer {access_token}"}
    }


@pytest.fixture(scope="function")
async def test_trading_params(mock_db, test_user):
    """Create test trading parameters."""
    params_data = {
        "user_id": test_user.id,
        "profit_top": 10.0,
        "profit_loss": 5.0,
        "stop_loss": 15.0,
        "take_profit": 8.0,
        "max_daily_loss": 100.0,
        "position_size": 10.0
    }
    
    params_doc = TradingParametersInDB(**params_data)
    result = await mock_db.trading_parameters.insert_one(params_doc.model_dump(by_alias=True))
    params_data["_id"] = result.inserted_id
    
    return TradingParametersInDB(**params_data)


@pytest.fixture(scope="function")
async def test_trade_position(mock_db, test_user):
    """Create a test trade position."""
    position_data = {
        "user_id": test_user.id,
        "symbol": "R_10",
        "contract_type": "CALL",
        "amount": 10.0,
        "duration": 5,
        "duration_unit": "m",
        "status": "pending"
    }
    
    position_doc = TradePositionInDB(**position_data)
    result = await mock_db.trade_positions.insert_one(position_doc.model_dump(by_alias=True))
    position_data["_id"] = result.inserted_id
    
    return TradePositionInDB(**position_data)


@pytest.fixture(autouse=True, scope="function")
async def cleanup_db(mock_db):
    """Clean up database after each test."""
    yield
    # Clean up all collections
    try:
        collections = await mock_db.list_collection_names()
        for collection_name in collections:
            await mock_db[collection_name].delete_many({})
    except Exception:
        # In case mock_db is not available or test doesn't use it
        pass


class MockDerivWebSocket:
    """Mock WebSocket for Deriv API testing."""
    
    def __init__(self):
        self.sent_messages = []
        self.responses = {}
    
    async def send(self, message):
        self.sent_messages.append(message)
    
    async def recv(self):
        # Return mock responses based on sent messages
        if self.sent_messages:
            last_message = self.sent_messages[-1]
            if "authorize" in last_message:
                return '{"authorize": {"loginid": "test123", "balance": 1000}}'
            elif "buy" in last_message:
                return '{"buy": {"contract_id": "12345", "longcode": "Test contract"}}'
            elif "proposal" in last_message:
                return '{"proposal": {"id": "test_proposal", "ask_price": 10.5}}'
        return '{"ping": "pong"}'
    
    async def close(self):
        pass


@pytest.fixture
def mock_deriv_websocket():
    """Mock Deriv WebSocket for testing."""
    return MockDerivWebSocket()


@pytest.fixture(scope="function")
def integration_client():
    """Test client with database dependency override for integration tests."""
    from app.core.database import get_database
    from unittest.mock import AsyncMock
    
    def override_get_database():
        return AsyncMock()
    
    # Override the database dependency
    app.dependency_overrides[get_database] = override_get_database
    
    with TestClient(app) as c:
        yield c
    
    # Clean up dependency override
    app.dependency_overrides.clear()
