"""
Unit tests for app.core.database module.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.core.config import settings
from app.core.database import (
    Database,
    close_mongo_connection,
    connect_to_mongo,
    db,
    get_database,
)


class TestDatabase:
    """Test the Database class."""

    def test_database_initialization(self):
        """Test that Database class initializes properly."""
        test_db = Database()
        assert test_db.client is None

    def test_get_db_with_client(self):
        """Test get_db returns correct database when client is set."""
        test_db = Database()
        mock_client = AsyncMock()
        test_db.client = mock_client

        test_db.get_db()
        mock_client.__getitem__.assert_called_once_with(settings.mongodb_db)

    def test_get_db_without_client(self):
        """Test get_db when client is None."""
        test_db = Database()
        test_db.client = None

        with pytest.raises(TypeError):
            test_db.get_db()


class TestDatabaseFunctions:
    """Test database utility functions."""

    @pytest.mark.asyncio
    async def test_get_database(self):
        """Test get_database function."""
        with patch.object(db, 'get_db') as mock_get_db:
            mock_get_db.return_value = "test_database"

            result = await get_database()
            assert result == "test_database"
            mock_get_db.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_to_mongo(self):
        """Test connect_to_mongo function."""
        original_client = db.client

        try:
            with patch('app.core.database.AsyncIOMotorClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value = mock_client

                await connect_to_mongo()

                mock_client_class.assert_called_once_with(settings.mongodb_uri)
                assert db.client == mock_client
        finally:
            db.client = original_client

    @pytest.mark.asyncio
    async def test_close_mongo_connection_with_client(self):
        """Test close_mongo_connection when client exists."""
        mock_client = AsyncMock()
        db.client = mock_client

        await close_mongo_connection()

        mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_mongo_connection_without_client(self):
        """Test close_mongo_connection when client is None."""
        original_client = db.client
        db.client = None

        try:
            # Should not raise an exception
            await close_mongo_connection()
        finally:
            db.client = original_client


class TestDatabaseSingleton:
    """Test the database singleton instance."""

    def test_db_instance_exists(self):
        """Test that db instance is properly created."""
        assert db is not None
        assert isinstance(db, Database)

    def test_db_instance_is_singleton(self):
        """Test that db is a singleton instance."""
        from app.core.database import db as db2
        assert db is db2

    def test_db_initial_state(self):
        """Test initial state of db instance."""
        # Note: This test might fail if other tests have modified the db instance
        # In a real scenario, you might want to reset the db state in setUp/tearDown
        assert hasattr(db, 'client')


class TestDatabaseIntegration:
    """Integration tests for database functionality."""

    @pytest.mark.asyncio
    async def test_full_connection_cycle(self):
        """Test complete connect/disconnect cycle."""
        original_client = db.client

        try:
            # Start with no client
            db.client = None

            # Connect
            with patch('app.core.database.AsyncIOMotorClient') as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value = mock_client

                await connect_to_mongo()
                assert db.client == mock_client

                # Test get_database works
                with patch.object(db, 'get_db') as mock_get_db:
                    mock_get_db.return_value = "test_db"
                    result = await get_database()
                    assert result == "test_db"

                # Disconnect
                await close_mongo_connection()
                mock_client.close.assert_called_once()

        finally:
            db.client = original_client

    @pytest.mark.asyncio
    async def test_database_configuration(self):
        """Test that database uses correct configuration."""
        with patch('app.core.database.AsyncIOMotorClient') as mock_client_class:
            await connect_to_mongo()

            # Verify connection string is from settings
            mock_client_class.assert_called_once_with(settings.mongodb_uri)

    def test_database_name_from_settings(self):
        """Test that database name comes from settings."""
        mock_client = AsyncMock()
        db.client = mock_client

        db.get_db()

        mock_client.__getitem__.assert_called_once_with(settings.mongodb_db)
