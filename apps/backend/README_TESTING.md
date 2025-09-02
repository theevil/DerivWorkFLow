# Backend Testing Guide

This document provides comprehensive information about testing the Deriv Workflow backend application.

## Test Structure

The test suite is organized into the following categories:

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_core_config.py     # Configuration testing
│   ├── test_core_security.py   # Security utilities testing
│   ├── test_core_database.py   # Database connection testing
│   ├── test_core_ai_analysis.py # AI analysis engine testing
│   ├── test_core_deriv.py      # Deriv WebSocket testing
│   ├── test_models_user.py     # User model validation testing
│   ├── test_models_trading.py  # Trading model validation testing
│   ├── test_crud_users.py      # User CRUD operations testing
│   ├── test_crud_trading.py    # Trading CRUD operations testing
│   ├── test_routers_health.py  # Health endpoint testing
│   └── test_routers_auth.py    # Authentication routes testing
└── integration/                # Integration tests
    ├── __init__.py
    ├── test_api_integration.py  # End-to-end API testing
    └── test_database_integration.py # Database workflow testing
```

## Testing Framework

We use **pytest** as our primary testing framework with the following key dependencies:

- `pytest` - Core testing framework
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking utilities
- `pytest-cov` - Coverage reporting
- `pytest-env` - Environment variable management
- `httpx` - HTTP client for API testing
- `mongomock-motor` - MongoDB mocking
- `factory-boy` - Test data generation
- `faker` - Fake data generation

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pipenv run test

# Run with verbose output
pipenv run pytest tests/ -v

# Run specific test file
pipenv run pytest tests/unit/test_core_security.py -v

# Run specific test function
pipenv run pytest tests/unit/test_core_security.py::TestPasswordHashing::test_get_password_hash -v
```

### Test Categories

Run tests by category using markers:

```bash
# Run only unit tests
pipenv run pytest -m unit

# Run only integration tests
pipenv run pytest -m integration

# Run only authentication tests
pipenv run pytest -m auth

# Run only trading functionality tests
pipenv run pytest -m trading

# Run only database tests
pipenv run pytest -m database
```

### Coverage Testing

```bash
# Run tests with coverage
pipenv run test-cov

# Generate HTML coverage report
pipenv run pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html
```

### Continuous Testing

```bash
# Run tests and re-run on file changes
pipenv run test-watch
```

## Test Configuration

### Environment Variables

Tests use the following environment variables (configured in `pytest.ini`):

```ini
ENVIRONMENT = testing
MONGODB_URI = mongodb://localhost:27017
MONGODB_DB = deriv_test
SECRET_KEY = test-secret-key-for-testing-only
DERIV_APP_ID = 1089
DEBUG = false
```

### Fixtures

Key fixtures available in `conftest.py`:

- `mock_db` - Mock database instance
- `client` - Synchronous test client
- `async_client` - Asynchronous test client
- `test_user` - Sample user for testing
- `authenticated_user` - User with JWT token
- `test_trading_params` - Sample trading parameters
- `test_trade_position` - Sample trade position
- `mock_deriv_websocket` - Mock Deriv WebSocket

## Unit Test Categories

### Core Module Tests

**Configuration Testing** (`test_core_config.py`)
- Environment variable handling
- Default value validation
- Setting overrides
- Type conversion

**Security Testing** (`test_core_security.py`)
- Password hashing and verification
- JWT token creation and validation
- Authentication flows
- Security utilities

**Database Testing** (`test_core_database.py`)
- Connection management
- Database initialization
- Connection pooling
- Error handling

**AI Analysis Testing** (`test_core_ai_analysis.py`)
- Technical indicator calculations
- Market analysis algorithms
- Trading signal generation
- Confidence scoring

**Deriv WebSocket Testing** (`test_core_deriv.py`)
- WebSocket connection management
- Message handling
- API communication
- Connection pooling

### Model Tests

**User Model Testing** (`test_models_user.py`)
- Data validation
- Model serialization
- Field constraints
- Model interoperability

**Trading Model Testing** (`test_models_trading.py`)
- Trading parameter validation
- Position model validation
- Market analysis models
- Signal generation models

### CRUD Tests

**User CRUD Testing** (`test_crud_users.py`)
- User creation and retrieval
- Authentication workflows
- User updates
- Error handling

**Trading CRUD Testing** (`test_crud_trading.py`)
- Trading parameter management
- Position lifecycle
- Market analysis storage
- Signal management
- Trading statistics

### Router Tests

**Health Router Testing** (`test_routers_health.py`)
- Health endpoint functionality
- Response format validation
- Performance testing
- Error scenarios

**Authentication Router Testing** (`test_routers_auth.py`)
- Login/logout flows
- User registration
- Token validation
- Protected endpoint access

## Integration Tests

### API Integration Testing

**Complete Workflows** (`test_api_integration.py`)
- End-to-end user registration and login
- Trading parameter management
- Position creation and management
- Error handling across endpoints
- CORS and middleware testing

**Concurrent Operations**
- Multiple simultaneous requests
- Database transaction handling
- Resource management

### Database Integration Testing

**Data Persistence** (`test_database_integration.py`)
- User data lifecycle
- Trading data relationships
- Data isolation between users
- Performance with multiple records

**Transaction Management**
- Atomic operations
- Rollback scenarios
- Concurrent access patterns

## Best Practices

### Writing Tests

1. **Follow AAA Pattern** (Arrange, Act, Assert)
   ```python
   def test_user_creation():
       # Arrange
       user_data = {"email": "test@example.com", "name": "Test"}

       # Act
       result = create_user(user_data)

       # Assert
       assert result.email == "test@example.com"
   ```

2. **Use Descriptive Test Names**
   ```python
   def test_user_authentication_with_valid_credentials():
       # Test implementation
   ```

3. **Mock External Dependencies**
   ```python
   @patch('app.core.deriv.websockets.connect')
   async def test_websocket_connection(mock_connect):
       mock_connect.return_value = mock_websocket
       # Test implementation
   ```

4. **Test Edge Cases**
   - Invalid inputs
   - Boundary conditions
   - Error scenarios
   - Performance limits

### Test Data Management

1. **Use Factories for Complex Objects**
   ```python
   def create_test_user(**kwargs):
       defaults = {
           "email": "test@example.com",
           "name": "Test User",
           "password": "password123"
       }
       defaults.update(kwargs)
       return UserCreate(**defaults)
   ```

2. **Clean Up After Tests**
   ```python
   @pytest.fixture(autouse=True)
   async def cleanup_db(mock_db):
       yield
       # Clean up collections
       collections = await mock_db.list_collection_names()
       for collection_name in collections:
           await mock_db[collection_name].delete_many({})
   ```

### Performance Testing

1. **Set Reasonable Timeouts**
   ```python
   @pytest.mark.timeout(5)
   def test_api_response_time():
       # Test should complete within 5 seconds
   ```

2. **Test Concurrent Operations**
   ```python
   @pytest.mark.asyncio
   async def test_concurrent_requests():
       tasks = [make_request() for _ in range(10)]
       results = await asyncio.gather(*tasks)
       # Verify all succeeded
   ```

## Debugging Tests

### Running Individual Tests
```bash
# Run single test with full output
pipenv run pytest tests/unit/test_core_security.py::test_password_hashing -v -s

# Run with debugger
pipenv run pytest tests/unit/test_core_security.py::test_password_hashing --pdb
```

### Test Output and Logging
```bash
# Show print statements
pipenv run pytest -s

# Show log output
pipenv run pytest --log-cli-level=DEBUG
```

### Common Issues

1. **Async Test Issues**
   - Ensure `@pytest.mark.asyncio` decorator is used
   - Use `AsyncMock` for async functions
   - Properly await async operations

2. **Database Connection Issues**
   - Verify mock database setup
   - Check for proper cleanup between tests
   - Ensure unique test data

3. **Import Issues**
   - Check Python path configuration
   - Verify all dependencies are installed
   - Check for circular imports

## Continuous Integration

### GitHub Actions Integration
```yaml
name: Backend Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install pipenv
          pipenv install --dev
      - name: Run tests
        run: pipenv run test-cov
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests before commit
pipenv run test
```

## Coverage Goals

Maintain the following coverage targets:

- **Overall Coverage**: > 90%
- **Core Modules**: > 95%
- **CRUD Operations**: > 90%
- **API Routes**: > 85%
- **Models**: > 95%

## Performance Benchmarks

Target performance metrics:

- **Unit Tests**: < 10ms per test
- **Integration Tests**: < 100ms per test
- **Full Test Suite**: < 2 minutes
- **Coverage Report**: < 30 seconds

## Troubleshooting

### Common Test Failures

1. **Database Connection Timeouts**
   - Check MongoDB mock setup
   - Verify connection cleanup

2. **Authentication Failures**
   - Verify JWT secret configuration
   - Check token expiration settings

3. **Async Operation Issues**
   - Ensure proper await usage
   - Check event loop configuration

4. **Import Errors**
   - Verify PYTHONPATH configuration
   - Check for missing dependencies

### Getting Help

1. Review test logs and error messages
2. Check fixture setup in `conftest.py`
3. Verify environment configuration
4. Run tests with debug flags
5. Consult pytest documentation

For additional support, refer to the main project documentation or create an issue in the project repository.
