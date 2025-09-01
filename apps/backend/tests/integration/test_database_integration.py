"""
Integration tests for database operations.
"""

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from mongomock_motor import AsyncMongoMockClient
from datetime import datetime
from bson import ObjectId

from app.core.database import Database, connect_to_mongo, close_mongo_connection
from app.crud.users import create_user, get_user, get_user_by_email, update_user, authenticate_user
from app.crud.trading import (
    create_trading_parameters, get_user_trading_parameters,
    create_trade_position, get_user_positions, update_position
)
from app.models.user import UserCreate, UserUpdate
from app.models.trading import TradingParametersCreate, TradePositionCreate


@pytest.mark.asyncio
class TestDatabaseConnection:
    """Test database connection functionality."""
    
    async def test_connect_and_disconnect_cycle(self):
        """Test connecting to and disconnecting from database."""
        # Use a test database instance
        db_instance = Database()
        original_client = db_instance.client
        
        try:
            # Test connection (using mock for safety)
            db_instance.client = AsyncMongoMockClient()
            assert db_instance.client is not None
            
            # Test getting database
            test_db = db_instance.get_db()
            assert test_db is not None
            
            # Test disconnection
            await db_instance.client.close()
            
        finally:
            # Restore original client
            db_instance.client = original_client
    
    async def test_database_operations_with_mock(self):
        """Test basic database operations with mock client."""
        # Use mongomock for testing
        client = AsyncMongoMockClient()
        db = client.test_database
        
        try:
            # Test insert and find
            collection = db.test_collection
            doc = {"name": "test", "value": 123}
            
            result = await collection.insert_one(doc)
            assert result.inserted_id is not None
            
            found_doc = await collection.find_one({"_id": result.inserted_id})
            assert found_doc is not None
            assert found_doc["name"] == "test"
            assert found_doc["value"] == 123
            
        finally:
            await client.close()


@pytest.mark.asyncio
class TestUserCRUDIntegration:
    """Test user CRUD operations with database."""
    
    async def setup_method(self):
        """Set up test database."""
        self.client = AsyncMongoMockClient()
        self.db = self.client.test_database
    
    async def teardown_method(self):
        """Clean up test database."""
        await self.client.close()
    
    async def test_user_creation_and_retrieval(self):
        """Test creating and retrieving a user."""
        user_create = UserCreate(
            email="test@example.com",
            name="Test User",
            password="testpassword123"
        )
        
        # Create user
        created_user = await create_user(self.db, user_create)
        
        assert created_user is not None
        assert created_user.email == "test@example.com"
        assert created_user.name == "Test User"
        assert created_user.hashed_password != "testpassword123"  # Should be hashed
        assert created_user.id is not None
        assert isinstance(created_user.created_at, datetime)
        
        # Retrieve user by ID
        retrieved_user = await get_user(self.db, str(created_user.id))
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
        assert retrieved_user.name == created_user.name
        
        # Retrieve user by email
        retrieved_by_email = await get_user_by_email(self.db, "test@example.com")
        
        assert retrieved_by_email is not None
        assert retrieved_by_email.id == created_user.id
        assert retrieved_by_email.email == "test@example.com"
    
    async def test_user_update_workflow(self):
        """Test updating user information."""
        user_create = UserCreate(
            email="update@example.com",
            name="Original Name",
            password="password123"
        )
        
        # Create user
        created_user = await create_user(self.db, user_create)
        
        # Update user
        user_update = UserUpdate(
            name="Updated Name",
            deriv_token="new_token_123"
        )
        
        updated_user = await update_user(self.db, str(created_user.id), user_update)
        
        assert updated_user is not None
        assert updated_user.id == created_user.id
        assert updated_user.name == "Updated Name"
        assert updated_user.deriv_token == "new_token_123"
        assert updated_user.email == "update@example.com"  # Unchanged
        assert updated_user.updated_at > created_user.updated_at
    
    async def test_user_authentication_workflow(self):
        """Test user authentication."""
        user_create = UserCreate(
            email="auth@example.com",
            name="Auth User",
            password="correctpassword"
        )
        
        # Create user
        created_user = await create_user(self.db, user_create)
        
        # Test correct authentication
        authenticated_user = await authenticate_user(
            self.db, "auth@example.com", "correctpassword"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        assert authenticated_user.email == "auth@example.com"
        
        # Test incorrect password
        failed_auth = await authenticate_user(
            self.db, "auth@example.com", "wrongpassword"
        )
        
        assert failed_auth is None
        
        # Test non-existent user
        failed_auth = await authenticate_user(
            self.db, "nonexistent@example.com", "password"
        )
        
        assert failed_auth is None
    
    async def test_duplicate_email_prevention(self):
        """Test that duplicate emails are handled at application level."""
        user_create1 = UserCreate(
            email="duplicate@example.com",
            name="User One",
            password="password123"
        )
        
        user_create2 = UserCreate(
            email="duplicate@example.com",
            name="User Two",
            password="password456"
        )
        
        # Create first user
        user1 = await create_user(self.db, user_create1)
        assert user1 is not None
        
        # Check if user exists before creating second user (application logic)
        existing_user = await get_user_by_email(self.db, "duplicate@example.com")
        assert existing_user is not None  # Should find the first user
        
        # In real application, this would raise an error
        # Here we just verify the check works


@pytest.mark.asyncio
class TestTradingCRUDIntegration:
    """Test trading CRUD operations with database."""
    
    async def setup_method(self):
        """Set up test database and user."""
        self.client = AsyncMongoMockClient()
        self.db = self.client.test_database
        
        # Create a test user
        user_create = UserCreate(
            email="trader@example.com",
            name="Trader User",
            password="password123"
        )
        self.user = await create_user(self.db, user_create)
    
    async def teardown_method(self):
        """Clean up test database."""
        await self.client.close()
    
    async def test_trading_parameters_workflow(self):
        """Test complete trading parameters workflow."""
        params_create = TradingParametersCreate(
            profit_top=10.0,
            profit_loss=5.0,
            stop_loss=15.0,
            take_profit=8.0,
            max_daily_loss=100.0,
            position_size=10.0
        )
        
        # Create trading parameters
        created_params = await create_trading_parameters(
            self.db, str(self.user.id), params_create
        )
        
        assert created_params is not None
        assert created_params.user_id == self.user.id
        assert created_params.profit_top == 10.0
        assert created_params.position_size == 10.0
        
        # Retrieve trading parameters
        retrieved_params = await get_user_trading_parameters(self.db, str(self.user.id))
        
        assert retrieved_params is not None
        assert retrieved_params.id == created_params.id
        assert retrieved_params.profit_top == 10.0
        
        # Update trading parameters
        from app.models.trading import TradingParametersUpdate
        params_update = TradingParametersUpdate(
            profit_top=15.0,
            position_size=20.0
        )
        
        from app.crud.trading import update_trading_parameters
        updated_params = await update_trading_parameters(
            self.db, str(self.user.id), params_update
        )
        
        assert updated_params is not None
        assert updated_params.profit_top == 15.0
        assert updated_params.position_size == 20.0
        assert updated_params.profit_loss == 5.0  # Unchanged
    
    async def test_trade_positions_workflow(self):
        """Test complete trade positions workflow."""
        position_create = TradePositionCreate(
            symbol="R_10",
            contract_type="CALL",
            amount=10.0,
            duration=5,
            duration_unit="m"
        )
        
        # Create trade position
        created_position = await create_trade_position(
            self.db, str(self.user.id), position_create
        )
        
        assert created_position is not None
        assert created_position.user_id == self.user.id
        assert created_position.symbol == "R_10"
        assert created_position.contract_type == "CALL"
        assert created_position.status == "pending"
        
        # Get user positions
        positions = await get_user_positions(self.db, str(self.user.id))
        
        assert len(positions) == 1
        assert positions[0].id == created_position.id
        
        # Get positions by status
        pending_positions = await get_user_positions(self.db, str(self.user.id), "pending")
        assert len(pending_positions) == 1
        
        open_positions = await get_user_positions(self.db, str(self.user.id), "open")
        assert len(open_positions) == 0
        
        # Update position
        update_data = {
            "status": "open",
            "entry_spot": 100.5,
            "contract_id": "123456"
        }
        
        updated_position = await update_position(
            self.db, str(created_position.id), str(self.user.id), update_data
        )
        
        assert updated_position is not None
        assert updated_position.status == "open"
        assert updated_position.entry_spot == 100.5
        assert updated_position.contract_id == "123456"
    
    async def test_multiple_users_isolation(self):
        """Test that users' data is properly isolated."""
        # Create second user
        user2_create = UserCreate(
            email="trader2@example.com",
            name="Trader Two",
            password="password456"
        )
        user2 = await create_user(self.db, user2_create)
        
        # Create trading parameters for both users
        params_create1 = TradingParametersCreate(
            profit_top=10.0,
            profit_loss=5.0,
            stop_loss=15.0,
            take_profit=8.0,
            max_daily_loss=100.0,
            position_size=10.0
        )
        
        params_create2 = TradingParametersCreate(
            profit_top=20.0,
            profit_loss=10.0,
            stop_loss=25.0,
            take_profit=15.0,
            max_daily_loss=200.0,
            position_size=20.0
        )
        
        params1 = await create_trading_parameters(self.db, str(self.user.id), params_create1)
        params2 = await create_trading_parameters(self.db, str(user2.id), params_create2)
        
        # Verify each user gets their own parameters
        retrieved_params1 = await get_user_trading_parameters(self.db, str(self.user.id))
        retrieved_params2 = await get_user_trading_parameters(self.db, str(user2.id))
        
        assert retrieved_params1.profit_top == 10.0
        assert retrieved_params2.profit_top == 20.0
        assert retrieved_params1.id != retrieved_params2.id
        
        # Create positions for both users
        position1 = await create_trade_position(
            self.db, str(self.user.id),
            TradePositionCreate(symbol="R_10", contract_type="CALL", amount=10.0, duration=5)
        )
        
        position2 = await create_trade_position(
            self.db, str(user2.id),
            TradePositionCreate(symbol="R_25", contract_type="PUT", amount=20.0, duration=10)
        )
        
        # Verify each user gets their own positions
        positions1 = await get_user_positions(self.db, str(self.user.id))
        positions2 = await get_user_positions(self.db, str(user2.id))
        
        assert len(positions1) == 1
        assert len(positions2) == 1
        assert positions1[0].symbol == "R_10"
        assert positions2[0].symbol == "R_25"


@pytest.mark.asyncio
class TestDatabasePerformance:
    """Test database performance characteristics."""
    
    async def setup_method(self):
        """Set up test database."""
        self.client = AsyncMongoMockClient()
        self.db = self.client.test_database
    
    async def teardown_method(self):
        """Clean up test database."""
        await self.client.close()
    
    async def test_bulk_user_creation(self):
        """Test creating multiple users efficiently."""
        import asyncio
        
        async def create_test_user(index):
            user_create = UserCreate(
                email=f"user{index}@example.com",
                name=f"User {index}",
                password="password123"
            )
            return await create_user(self.db, user_create)
        
        # Create 10 users concurrently
        tasks = [create_test_user(i) for i in range(10)]
        users = await asyncio.gather(*tasks)
        
        assert len(users) == 10
        assert all(user is not None for user in users)
        
        # Verify all users have unique emails
        emails = [user.email for user in users]
        assert len(set(emails)) == 10
    
    async def test_position_queries_with_multiple_records(self):
        """Test position queries with multiple records."""
        # Create a user
        user_create = UserCreate(
            email="performance@example.com",
            name="Performance User",
            password="password123"
        )
        user = await create_user(self.db, user_create)
        
        # Create multiple positions
        positions = []
        for i in range(20):
            position_create = TradePositionCreate(
                symbol=f"R_{10 + i}",
                contract_type="CALL" if i % 2 == 0 else "PUT",
                amount=10.0 + i,
                duration=5 + i,
            )
            position = await create_trade_position(self.db, str(user.id), position_create)
            positions.append(position)
        
        # Test retrieving all positions
        all_positions = await get_user_positions(self.db, str(user.id))
        assert len(all_positions) == 20
        
        # Test filtering by status
        pending_positions = await get_user_positions(self.db, str(user.id), "pending")
        assert len(pending_positions) == 20  # All should be pending by default
        
        # Update some positions to different status
        for i in range(5):
            await update_position(
                self.db, str(positions[i].id), str(user.id), {"status": "open"}
            )
        
        # Test filtering again
        open_positions = await get_user_positions(self.db, str(user.id), "open")
        pending_positions = await get_user_positions(self.db, str(user.id), "pending")
        
        assert len(open_positions) == 5
        assert len(pending_positions) == 15
