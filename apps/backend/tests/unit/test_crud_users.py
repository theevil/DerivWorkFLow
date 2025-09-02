"""
Unit tests for app.crud.users module.
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from bson import ObjectId

from app.crud.users import (
    authenticate_user,
    create_user,
    get_user,
    get_user_by_email,
    update_user,
)
from app.models.user import UserCreate, UserInDB, UserUpdate


class TestGetUser:
    """Test the get_user function."""

    @pytest.mark.asyncio
    async def test_get_user_exists(self):
        """Test getting an existing user."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        user_data = {
            "_id": ObjectId(user_id),
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": "$2b$12$hash",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        mock_db.users.find_one.return_value = user_data

        result = await get_user(mock_db, user_id)

        assert result is not None
        assert isinstance(result, UserInDB)
        assert result.email == "test@example.com"
        assert result.name == "Test User"
        mock_db.users.find_one.assert_called_once_with({"_id": ObjectId(user_id)})

    @pytest.mark.asyncio
    async def test_get_user_not_exists(self):
        """Test getting a non-existent user."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"

        mock_db.users.find_one.return_value = None

        result = await get_user(mock_db, user_id)

        assert result is None
        mock_db.users.find_one.assert_called_once_with({"_id": ObjectId(user_id)})

    @pytest.mark.asyncio
    async def test_get_user_invalid_id(self):
        """Test getting user with invalid ObjectId."""
        mock_db = AsyncMock()
        invalid_id = "invalid_id"

        with pytest.raises(Exception):  # ObjectId will raise an exception
            await get_user(mock_db, invalid_id)


class TestGetUserByEmail:
    """Test the get_user_by_email function."""

    @pytest.mark.asyncio
    async def test_get_user_by_email_exists(self):
        """Test getting an existing user by email."""
        mock_db = AsyncMock()
        email = "test@example.com"
        user_data = {
            "_id": ObjectId(),
            "email": email,
            "name": "Test User",
            "hashed_password": "$2b$12$hash",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        mock_db.users.find_one.return_value = user_data

        result = await get_user_by_email(mock_db, email)

        assert result is not None
        assert isinstance(result, UserInDB)
        assert result.email == email
        mock_db.users.find_one.assert_called_once_with({"email": email})

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_exists(self):
        """Test getting a non-existent user by email."""
        mock_db = AsyncMock()
        email = "nonexistent@example.com"

        mock_db.users.find_one.return_value = None

        result = await get_user_by_email(mock_db, email)

        assert result is None
        mock_db.users.find_one.assert_called_once_with({"email": email})

    @pytest.mark.asyncio
    async def test_get_user_by_email_case_sensitivity(self):
        """Test that email lookup is case sensitive."""
        mock_db = AsyncMock()
        email = "Test@Example.Com"

        mock_db.users.find_one.return_value = None

        await get_user_by_email(mock_db, email)

        # Should search for exact case
        mock_db.users.find_one.assert_called_once_with({"email": "Test@Example.Com"})


class TestCreateUser:
    """Test the create_user function."""

    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Test successful user creation."""
        mock_db = AsyncMock()
        user_create = UserCreate(
            email="test@example.com",
            name="Test User",
            password="plainpassword"  # pragma: allowlist secret
        )

        inserted_id = ObjectId()
        mock_db.users.insert_one.return_value.inserted_id = inserted_id

        with patch('app.crud.users.get_password_hash') as mock_hash:
            mock_hash.return_value = "$2b$12$hashed_password"

            result = await create_user(mock_db, user_create)

        assert result is not None
        assert isinstance(result, UserInDB)
        assert result.email == "test@example.com"
        assert result.name == "Test User"
        assert result.hashed_password == "$2b$12$hashed_password"
        assert result.deriv_token is None
        assert result.id == inserted_id
        assert isinstance(result.created_at, datetime)
        assert isinstance(result.updated_at, datetime)

        # Verify password was hashed
        mock_hash.assert_called_once_with("plainpassword")

        # Verify database insert was called
        mock_db.users.insert_one.assert_called_once()
        call_args = mock_db.users.insert_one.call_args[0][0]
        assert call_args["email"] == "test@example.com"
        assert call_args["name"] == "Test User"
        assert call_args["hashed_password"] == "$2b$12$hashed_password"
        assert call_args["deriv_token"] is None

    @pytest.mark.asyncio
    async def test_create_user_timestamps(self):
        """Test that timestamps are set during user creation."""
        mock_db = AsyncMock()
        user_create = UserCreate(
            email="test@example.com",
            name="Test User",
            password="plainpassword"  # pragma: allowlist secret
        )

        mock_db.users.insert_one.return_value.inserted_id = ObjectId()

        with patch('app.crud.users.get_password_hash', return_value="$2b$12$hash"):
            with patch('app.crud.users.datetime') as mock_datetime:
                mock_now = datetime(2023, 1, 1, 12, 0, 0)
                mock_datetime.utcnow.return_value = mock_now

                result = await create_user(mock_db, user_create)

        assert result.created_at == mock_now
        assert result.updated_at == mock_now

    @pytest.mark.asyncio
    async def test_create_user_database_error(self):
        """Test user creation with database error."""
        mock_db = AsyncMock()
        user_create = UserCreate(
            email="test@example.com",
            name="Test User",
            password="plainpassword"  # pragma: allowlist secret
        )

        mock_db.users.insert_one.side_effect = Exception("Database error")

        with patch('app.crud.users.get_password_hash', return_value="$2b$12$hash"):
            with pytest.raises(Exception, match="Database error"):
                await create_user(mock_db, user_create)


class TestUpdateUser:
    """Test the update_user function."""

    @pytest.mark.asyncio
    async def test_update_user_success(self):
        """Test successful user update."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        user_update = UserUpdate(
            name="Updated Name",
            deriv_token="new_token"
        )

        updated_user_data = {
            "_id": ObjectId(user_id),
            "email": "test@example.com",
            "name": "Updated Name",
            "hashed_password": "$2b$12$hash",
            "deriv_token": "new_token",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime.utcnow()
        }

        mock_db.users.find_one_and_update.return_value = updated_user_data

        result = await update_user(mock_db, user_id, user_update)

        assert result is not None
        assert isinstance(result, UserInDB)
        assert result.name == "Updated Name"
        assert result.deriv_token == "new_token"

        # Verify update was called correctly
        mock_db.users.find_one_and_update.assert_called_once()
        call_args = mock_db.users.find_one_and_update.call_args

        assert call_args[0][0] == {"_id": ObjectId(user_id)}
        update_data = call_args[0][1]["$set"]
        assert update_data["name"] == "Updated Name"
        assert update_data["deriv_token"] == "new_token"
        assert "updated_at" in update_data
        assert call_args[1]["return_document"] is True

    @pytest.mark.asyncio
    async def test_update_user_password(self):
        """Test updating user password."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        user_update = UserUpdate(password="newpassword")  # pragma: allowlist secret

        updated_user_data = {
            "_id": ObjectId(user_id),
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": "$2b$12$new_hash",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime.utcnow()
        }

        mock_db.users.find_one_and_update.return_value = updated_user_data

        with patch('app.crud.users.get_password_hash') as mock_hash:
            mock_hash.return_value = "$2b$12$new_hash"

            result = await update_user(mock_db, user_id, user_update)

        assert result is not None
        assert result.hashed_password == "$2b$12$new_hash"

        # Verify password was hashed
        mock_hash.assert_called_once_with("newpassword")

        # Verify update data doesn't contain plain password
        call_args = mock_db.users.find_one_and_update.call_args
        update_data = call_args[0][1]["$set"]
        assert "password" not in update_data
        assert update_data["hashed_password"] == "$2b$12$new_hash"

    @pytest.mark.asyncio
    async def test_update_user_exclude_unset(self):
        """Test that only set fields are updated."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        user_update = UserUpdate(name="Updated Name")  # Only name is set

        updated_user_data = {
            "_id": ObjectId(user_id),
            "email": "test@example.com",
            "name": "Updated Name",
            "hashed_password": "$2b$12$hash",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime.utcnow()
        }

        mock_db.users.find_one_and_update.return_value = updated_user_data

        await update_user(mock_db, user_id, user_update)

        # Verify only name and updated_at are in update data
        call_args = mock_db.users.find_one_and_update.call_args
        update_data = call_args[0][1]["$set"]
        assert "name" in update_data
        assert "updated_at" in update_data
        assert "email" not in update_data
        assert "password" not in update_data
        assert "deriv_token" not in update_data

    @pytest.mark.asyncio
    async def test_update_user_not_found(self):
        """Test updating non-existent user."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        user_update = UserUpdate(name="Updated Name")

        mock_db.users.find_one_and_update.return_value = None

        result = await update_user(mock_db, user_id, user_update)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_user_empty_update(self):
        """Test updating user with no changes."""
        mock_db = AsyncMock()
        user_id = "507f1f77bcf86cd799439011"
        user_update = UserUpdate()  # No fields set

        updated_user_data = {
            "_id": ObjectId(user_id),
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": "$2b$12$hash",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime.utcnow()
        }

        mock_db.users.find_one_and_update.return_value = updated_user_data

        result = await update_user(mock_db, user_id, user_update)

        assert result is not None

        # Should still update the updated_at timestamp
        call_args = mock_db.users.find_one_and_update.call_args
        update_data = call_args[0][1]["$set"]
        assert "updated_at" in update_data
        assert len(update_data) == 1  # Only updated_at


class TestAuthenticateUser:
    """Test the authenticate_user function."""

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self):
        """Test successful user authentication."""
        mock_db = AsyncMock()
        email = "test@example.com"
        password = "correctpassword"  # pragma: allowlist secret

        user_data = {
            "_id": ObjectId(),
            "email": email,
            "name": "Test User",
            "hashed_password": "$2b$12$hashed_password",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        with patch('app.crud.users.get_user_by_email') as mock_get_user:
            with patch('app.crud.users.verify_password') as mock_verify:
                mock_get_user.return_value = UserInDB(**user_data)
                mock_verify.return_value = True

                result = await authenticate_user(mock_db, email, password)

        assert result is not None
        assert isinstance(result, UserInDB)
        assert result.email == email

        mock_get_user.assert_called_once_with(mock_db, email)
        mock_verify.assert_called_once_with(password, "$2b$12$hashed_password")

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self):
        """Test authentication with non-existent user."""
        mock_db = AsyncMock()
        email = "nonexistent@example.com"
        password = "password"  # pragma: allowlist secret

        with patch('app.crud.users.get_user_by_email') as mock_get_user:
            mock_get_user.return_value = None

            result = await authenticate_user(mock_db, email, password)

        assert result is None
        mock_get_user.assert_called_once_with(mock_db, email)

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password."""
        mock_db = AsyncMock()
        email = "test@example.com"
        password = "wrongpassword"  # pragma: allowlist secret

        user_data = {
            "_id": ObjectId(),
            "email": email,
            "name": "Test User",
            "hashed_password": "$2b$12$hashed_password",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        with patch('app.crud.users.get_user_by_email') as mock_get_user:
            with patch('app.crud.users.verify_password') as mock_verify:
                mock_get_user.return_value = UserInDB(**user_data)
                mock_verify.return_value = False  # Wrong password

                result = await authenticate_user(mock_db, email, password)

        assert result is None

        mock_get_user.assert_called_once_with(mock_db, email)
        mock_verify.assert_called_once_with(password, "$2b$12$hashed_password")

    @pytest.mark.asyncio
    async def test_authenticate_user_empty_password(self):
        """Test authentication with empty password."""
        mock_db = AsyncMock()
        email = "test@example.com"
        password = ""

        user_data = {
            "_id": ObjectId(),
            "email": email,
            "name": "Test User",
            "hashed_password": "$2b$12$hashed_password",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        with patch('app.crud.users.get_user_by_email') as mock_get_user:
            with patch('app.crud.users.verify_password') as mock_verify:
                mock_get_user.return_value = UserInDB(**user_data)
                mock_verify.return_value = False  # Empty password fails

                result = await authenticate_user(mock_db, email, password)

        assert result is None


class TestUserCRUDIntegration:
    """Integration tests for user CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_and_get_user_cycle(self):
        """Test creating a user and then retrieving it."""
        mock_db = AsyncMock()
        user_create = UserCreate(
            email="test@example.com",
            name="Test User",
            password="testpassword"  # pragma: allowlist secret
        )

        # Mock creation
        inserted_id = ObjectId()
        mock_db.users.insert_one.return_value.inserted_id = inserted_id

        with patch('app.crud.users.get_password_hash', return_value="$2b$12$hash"):
            created_user = await create_user(mock_db, user_create)

        # Mock retrieval
        user_data = {
            "_id": inserted_id,
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": "$2b$12$hash",
            "deriv_token": None,
            "created_at": created_user.created_at,
            "updated_at": created_user.updated_at
        }
        mock_db.users.find_one.return_value = user_data

        retrieved_user = await get_user(mock_db, str(inserted_id))

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email
        assert retrieved_user.name == created_user.name

    @pytest.mark.asyncio
    async def test_create_authenticate_cycle(self):
        """Test creating a user and then authenticating."""
        mock_db = AsyncMock()
        email = "test@example.com"
        password = "testpassword"  # pragma: allowlist secret
        hashed_password = "$2b$12$hashed_password"

        user_create = UserCreate(
            email=email,
            name="Test User",
            password=password
        )

        # Mock creation
        mock_db.users.insert_one.return_value.inserted_id = ObjectId()

        with patch('app.crud.users.get_password_hash', return_value=hashed_password):
            created_user = await create_user(mock_db, user_create)

        # Mock authentication
        with patch('app.crud.users.get_user_by_email') as mock_get_user:
            with patch('app.crud.users.verify_password') as mock_verify:
                mock_get_user.return_value = created_user
                mock_verify.return_value = True

                authenticated_user = await authenticate_user(mock_db, email, password)

        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        assert authenticated_user.email == email
