"""
Unit tests for app.models.user module.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from bson import ObjectId

from app.models.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserInDB,
    User
)


class TestUserBase:
    """Test the UserBase model."""
    
    def test_valid_user_base(self):
        """Test creating a valid UserBase instance."""
        user_data = {
            "email": "test@example.com",
            "name": "Test User"
        }
        
        user = UserBase(**user_data)
        
        assert user.email == "test@example.com"
        assert user.name == "Test User"
    
    def test_invalid_email(self):
        """Test UserBase with invalid email."""
        user_data = {
            "email": "invalid-email",
            "name": "Test User"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)
        
        assert "value is not a valid email address" in str(exc_info.value)
    
    def test_missing_email(self):
        """Test UserBase with missing email."""
        user_data = {
            "name": "Test User"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)
        
        assert "email" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    def test_missing_name(self):
        """Test UserBase with missing name."""
        user_data = {
            "email": "test@example.com"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserBase(**user_data)
        
        assert "name" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    def test_empty_name(self):
        """Test UserBase with empty name."""
        user_data = {
            "email": "test@example.com",
            "name": ""
        }
        
        # Empty string should be allowed but might not be practical
        user = UserBase(**user_data)
        assert user.name == ""
    
    def test_unicode_name(self):
        """Test UserBase with unicode characters in name."""
        user_data = {
            "email": "test@example.com",
            "name": "José María Azñar"
        }
        
        user = UserBase(**user_data)
        assert user.name == "José María Azñar"


class TestUserCreate:
    """Test the UserCreate model."""
    
    def test_valid_user_create(self):
        """Test creating a valid UserCreate instance."""
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "securepassword123"
        }
        
        user = UserCreate(**user_data)
        
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.password == "securepassword123"
    
    def test_missing_password(self):
        """Test UserCreate with missing password."""
        user_data = {
            "email": "test@example.com",
            "name": "Test User"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "password" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)
    
    def test_empty_password(self):
        """Test UserCreate with empty password."""
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": ""
        }
        
        # Empty password should be allowed at model level
        # Business logic should handle password validation
        user = UserCreate(**user_data)
        assert user.password == ""
    
    def test_inherits_from_user_base(self):
        """Test that UserCreate inherits UserBase properties."""
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "password123"
        }
        
        user = UserCreate(**user_data)
        
        # Should have UserBase properties
        assert hasattr(user, 'email')
        assert hasattr(user, 'name')
        # And UserCreate specific properties
        assert hasattr(user, 'password')


class TestUserUpdate:
    """Test the UserUpdate model."""
    
    def test_all_fields_provided(self):
        """Test UserUpdate with all fields provided."""
        user_data = {
            "email": "updated@example.com",
            "name": "Updated User",
            "password": "newpassword123",
            "deriv_token": "new_token_123"
        }
        
        user = UserUpdate(**user_data)
        
        assert user.email == "updated@example.com"
        assert user.name == "Updated User"
        assert user.password == "newpassword123"
        assert user.deriv_token == "new_token_123"
    
    def test_partial_update(self):
        """Test UserUpdate with only some fields."""
        user_data = {
            "name": "Updated User"
        }
        
        user = UserUpdate(**user_data)
        
        assert user.name == "Updated User"
        assert user.email is None
        assert user.password is None
        assert user.deriv_token is None
    
    def test_empty_update(self):
        """Test UserUpdate with no fields."""
        user = UserUpdate()
        
        assert user.email is None
        assert user.name is None
        assert user.password is None
        assert user.deriv_token is None
    
    def test_invalid_email_update(self):
        """Test UserUpdate with invalid email."""
        user_data = {
            "email": "invalid-email"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(**user_data)
        
        assert "value is not a valid email address" in str(exc_info.value)
    
    def test_deriv_token_update(self):
        """Test UserUpdate with deriv token."""
        user_data = {
            "deriv_token": "abc123_deriv_token"
        }
        
        user = UserUpdate(**user_data)
        assert user.deriv_token == "abc123_deriv_token"


class TestUserInDB:
    """Test the UserInDB model."""
    
    def test_valid_user_in_db(self):
        """Test creating a valid UserInDB instance."""
        object_id = ObjectId()
        user_data = {
            "_id": object_id,
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": "$2b$12$hashed_password_here",
            "deriv_token": "token_123"
        }
        
        user = UserInDB(**user_data)
        
        assert user.id == object_id
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.hashed_password == "$2b$12$hashed_password_here"
        assert user.deriv_token == "token_123"
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_default_timestamps(self):
        """Test that timestamps are set by default."""
        user_data = {
            "_id": ObjectId(),
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": "$2b$12$hashed_password_here"
        }
        
        user = UserInDB(**user_data)
        
        assert user.created_at is not None
        assert user.updated_at is not None
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_custom_timestamps(self):
        """Test UserInDB with custom timestamps."""
        custom_time = datetime(2023, 1, 1, 12, 0, 0)
        user_data = {
            "_id": ObjectId(),
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": "$2b$12$hashed_password_here",
            "created_at": custom_time,
            "updated_at": custom_time
        }
        
        user = UserInDB(**user_data)
        
        assert user.created_at == custom_time
        assert user.updated_at == custom_time
    
    def test_none_deriv_token(self):
        """Test UserInDB with None deriv_token."""
        user_data = {
            "_id": ObjectId(),
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": "$2b$12$hashed_password_here",
            "deriv_token": None
        }
        
        user = UserInDB(**user_data)
        assert user.deriv_token is None
    
    def test_missing_required_fields(self):
        """Test UserInDB with missing required fields."""
        user_data = {
            "_id": ObjectId(),
            "email": "test@example.com",
            "name": "Test User"
            # Missing hashed_password
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserInDB(**user_data)
        
        assert "hashed_password" in str(exc_info.value)
    
    def test_model_config(self):
        """Test that model configuration is correct."""
        config = UserInDB.model_config
        
        assert ObjectId in config["json_encoders"]
        assert config["populate_by_name"] is True
        assert config["arbitrary_types_allowed"] is True
    
    def test_alias_mapping(self):
        """Test that _id is properly aliased to id."""
        object_id = ObjectId()
        user_data = {
            "_id": object_id,
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": "$2b$12$hashed_password_here"
        }
        
        user = UserInDB(**user_data)
        assert user.id == object_id


class TestUser:
    """Test the User model (public response model)."""
    
    def test_valid_user(self):
        """Test creating a valid User instance."""
        user_data = {
            "id": "507f1f77bcf86cd799439011",
            "email": "test@example.com",
            "name": "Test User",
            "deriv_token": "token_123",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime(2023, 1, 1, 12, 0, 0)
        }
        
        user = User(**user_data)
        
        assert user.id == "507f1f77bcf86cd799439011"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.deriv_token == "token_123"
        assert user.created_at == datetime(2023, 1, 1, 12, 0, 0)
        assert user.updated_at == datetime(2023, 1, 1, 12, 0, 0)
    
    def test_no_hashed_password(self):
        """Test that User model doesn't expose hashed_password."""
        user_data = {
            "id": "507f1f77bcf86cd799439011",
            "email": "test@example.com",
            "name": "Test User",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime(2023, 1, 1, 12, 0, 0)
        }
        
        user = User(**user_data)
        
        # Should not have hashed_password field
        assert not hasattr(user, 'hashed_password')
    
    def test_string_id(self):
        """Test that User uses string ID instead of ObjectId."""
        user_data = {
            "id": "507f1f77bcf86cd799439011",
            "email": "test@example.com",
            "name": "Test User",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime(2023, 1, 1, 12, 0, 0)
        }
        
        user = User(**user_data)
        
        assert isinstance(user.id, str)
        assert user.id == "507f1f77bcf86cd799439011"
    
    def test_none_deriv_token(self):
        """Test User with None deriv_token."""
        user_data = {
            "id": "507f1f77bcf86cd799439011",
            "email": "test@example.com",
            "name": "Test User",
            "deriv_token": None,
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime(2023, 1, 1, 12, 0, 0)
        }
        
        user = User(**user_data)
        assert user.deriv_token is None
    
    def test_inherits_from_user_base(self):
        """Test that User inherits from UserBase."""
        user_data = {
            "id": "507f1f77bcf86cd799439011",
            "email": "test@example.com",
            "name": "Test User",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime(2023, 1, 1, 12, 0, 0)
        }
        
        user = User(**user_data)
        
        # Should have UserBase properties
        assert hasattr(user, 'email')
        assert hasattr(user, 'name')
        # And User specific properties
        assert hasattr(user, 'id')
        assert hasattr(user, 'created_at')
        assert hasattr(user, 'updated_at')
    
    def test_model_config(self):
        """Test that model configuration is correct."""
        config = User.model_config
        
        assert ObjectId in config["json_encoders"]


class TestUserModelInteroperability:
    """Test interoperability between user models."""
    
    def test_user_create_to_user_in_db(self):
        """Test converting UserCreate to UserInDB."""
        create_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "plainpassword"
        }
        
        user_create = UserCreate(**create_data)
        
        # Simulate what would happen in business logic
        user_in_db_data = {
            "_id": ObjectId(),
            "email": user_create.email,
            "name": user_create.name,
            "hashed_password": "$2b$12$hashed_version_of_password"
        }
        
        user_in_db = UserInDB(**user_in_db_data)
        
        assert user_in_db.email == user_create.email
        assert user_in_db.name == user_create.name
        assert user_in_db.hashed_password != create_data["password"]  # Should be hashed
    
    def test_user_in_db_to_user(self):
        """Test converting UserInDB to User."""
        object_id = ObjectId()
        user_in_db_data = {
            "_id": object_id,
            "email": "test@example.com",
            "name": "Test User",
            "hashed_password": "$2b$12$hashed_password_here",
            "deriv_token": "token_123",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime(2023, 1, 1, 12, 0, 0)
        }
        
        user_in_db = UserInDB(**user_in_db_data)
        
        # Convert to public User model
        user_data = {
            "id": str(user_in_db.id),
            "email": user_in_db.email,
            "name": user_in_db.name,
            "deriv_token": user_in_db.deriv_token,
            "created_at": user_in_db.created_at,
            "updated_at": user_in_db.updated_at
        }
        
        user = User(**user_data)
        
        assert user.id == str(object_id)
        assert user.email == user_in_db.email
        assert user.name == user_in_db.name
        assert user.deriv_token == user_in_db.deriv_token
        assert not hasattr(user, 'hashed_password')  # Should not expose password
    
    def test_user_update_partial_application(self):
        """Test applying UserUpdate to existing UserInDB."""
        # Existing user
        existing_user = UserInDB(
            _id=ObjectId(),
            email="old@example.com",
            name="Old Name",
            hashed_password="$2b$12$old_hash"
        )
        
        # Update data
        update_data = UserUpdate(
            name="New Name",
            deriv_token="new_token_123"
        )
        
        # Simulate update application
        updated_fields = update_data.model_dump(exclude_unset=True)
        
        for field, value in updated_fields.items():
            if value is not None:
                setattr(existing_user, field, value)
        
        assert existing_user.name == "New Name"
        assert existing_user.deriv_token == "new_token_123"
        assert existing_user.email == "old@example.com"  # Unchanged
        assert existing_user.hashed_password == "$2b$12$old_hash"  # Unchanged
