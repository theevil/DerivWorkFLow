"""
Unit tests for automation system components
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import redis
import json

from app.workers.market_monitor import MarketMonitorWorker
from app.workers.trading_executor import TradingExecutorWorker
from app.workers.celery_app import celery_app
from app.workers.tasks import market_scan_scheduler, process_signal


class TestMarketMonitorWorker:
    """Test cases for MarketMonitorWorker"""
    
    @pytest.fixture
    def market_monitor(self):
        with patch('app.workers.market_monitor.redis.from_url'):
            monitor = MarketMonitorWorker()
            monitor.redis_client = MagicMock()
            return monitor
    
    def test_market_monitor_initialization(self, market_monitor):
        """Test market monitor initializes correctly"""
        assert market_monitor is not None
        assert market_monitor.enhanced_generator is not None
        assert market_monitor.market_analyzer is not None
        assert market_monitor.risk_manager is not None
        assert len(market_monitor.symbols) > 0
        assert "R_10" in market_monitor.symbols
    
    def test_generate_simulated_data(self, market_monitor):
        """Test simulated market data generation"""
        data = market_monitor._generate_simulated_data("R_10")
        
        assert data["symbol"] == "R_10"
        assert "current_price" in data
        assert "price_history" in data
        assert "volatility" in data
        assert "timestamp" in data
        assert len(data["price_history"]) == 50
        assert all(price > 0 for price in data["price_history"])
    
    @pytest.mark.asyncio
    async def test_fetch_market_data(self, market_monitor):
        """Test market data fetching"""
        # Mock Redis responses
        market_monitor.redis_client.get.return_value = None  # No cache
        
        market_data = await market_monitor._fetch_market_data()
        
        assert isinstance(market_data, dict)
        assert len(market_data) > 0
        
        # Check that all symbols are present
        for symbol in market_monitor.symbols:
            assert symbol in market_data
            assert "current_price" in market_data[symbol]
            assert "price_history" in market_data[symbol]
    
    @pytest.mark.asyncio
    async def test_analyze_symbol_opportunity(self, market_monitor):
        """Test symbol opportunity analysis"""
        # Create mock market data
        market_data = {
            "symbol": "R_10",
            "current_price": 1.05,
            "price_history": [1.0 + i * 0.001 for i in range(50)],
            "volatility": 0.15,
            "volume": 500
        }
        
        with patch.object(market_monitor.market_analyzer, 'analyze_market_advanced') as mock_analyze:
            # Mock analysis result
            mock_analysis = MagicMock()
            mock_analysis.confidence_score = 0.8
            mock_analysis.recommended_action = "buy_call"
            mock_analysis.risk_level = "medium"
            mock_analyze.return_value = mock_analysis
            
            opportunity = await market_monitor._analyze_symbol_opportunity("R_10", market_data)
            
            assert opportunity is not None
            assert opportunity["symbol"] == "R_10"
            assert opportunity["opportunity_score"] == 0.8
            assert opportunity["recommended_action"] == "buy_call"
            assert opportunity["analysis"] == mock_analysis
    
    @pytest.mark.asyncio
    async def test_analyze_symbol_opportunity_low_confidence(self, market_monitor):
        """Test opportunity analysis with low confidence"""
        market_data = {
            "symbol": "R_10",
            "current_price": 1.05,
            "price_history": [1.0] * 50,  # Flat price history
            "volatility": 0.15,
            "volume": 500
        }
        
        with patch.object(market_monitor.market_analyzer, 'analyze_market_advanced') as mock_analyze:
            # Mock low confidence analysis
            mock_analysis = MagicMock()
            mock_analysis.confidence_score = 0.3  # Low confidence
            mock_analysis.recommended_action = "hold"
            mock_analysis.risk_level = "high"
            mock_analyze.return_value = mock_analysis
            
            opportunity = await market_monitor._analyze_symbol_opportunity("R_10", market_data)
            
            assert opportunity is None  # Should not create opportunity for low confidence
    
    @pytest.mark.asyncio
    async def test_is_user_eligible_for_signal(self, market_monitor):
        """Test user eligibility check for signals"""
        user_id = "test_user"
        symbol = "R_10"
        positions = []  # No current positions
        
        # Mock trading parameters
        trading_params = MagicMock()
        trading_params.max_daily_loss = 100
        
        # Mock Redis for recent signals check
        market_monitor.redis_client.exists.return_value = False
        
        # Test eligible user
        eligible = await market_monitor._is_user_eligible_for_signal(
            user_id, symbol, positions, trading_params
        )
        
        assert eligible is True
    
    @pytest.mark.asyncio
    async def test_is_user_not_eligible_max_positions(self, market_monitor):
        """Test user not eligible due to max positions"""
        user_id = "test_user"
        symbol = "R_10"
        
        # Create mock positions (exceed limit)
        positions = []
        for i in range(10):  # More than max_concurrent_positions
            pos = MagicMock()
            pos.status = "open"
            pos.symbol = f"R_{i * 10}"
            positions.append(pos)
        
        trading_params = MagicMock()
        trading_params.max_daily_loss = 100
        
        eligible = await market_monitor._is_user_eligible_for_signal(
            user_id, symbol, positions, trading_params
        )
        
        assert eligible is False
    
    def test_get_market_status(self, market_monitor):
        """Test market status retrieval"""
        # Mock Redis ping
        market_monitor.redis_client.ping.return_value = True
        market_monitor.redis_client.exists.return_value = True
        
        status = market_monitor.get_market_status()
        
        assert status["active"] is True
        assert status["symbols_monitored"] == len(market_monitor.symbols)
        assert status["redis_connected"] is True
        assert "monitoring_intervals" in status


class TestTradingExecutorWorker:
    """Test cases for TradingExecutorWorker"""
    
    @pytest.fixture
    def trading_executor(self):
        with patch('app.workers.trading_executor.redis.from_url'):
            executor = TradingExecutorWorker()
            executor.redis_client = MagicMock()
            return executor
    
    @pytest.fixture
    def sample_signal_data(self):
        return {
            "user_id": "test_user",
            "symbol": "R_10",
            "signal_type": "BUY_CALL",
            "recommended_amount": 50,
            "recommended_duration": 5,
            "confidence": 0.8,
            "reasoning": "Test signal",
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def test_trading_executor_initialization(self, trading_executor):
        """Test trading executor initializes correctly"""
        assert trading_executor is not None
        assert trading_executor.risk_manager is not None
        assert trading_executor.execution_queue == "trading_queue"
        assert trading_executor.active_executions == {}
    
    @pytest.mark.asyncio
    async def test_validate_execution_success(self, trading_executor, sample_signal_data):
        """Test successful execution validation"""
        with patch('app.workers.trading_executor.get_database_sync') as mock_db, \
             patch('app.crud.users.get_user_by_id') as mock_get_user, \
             patch('app.crud.trading.get_user_trading_parameters') as mock_get_params, \
             patch('app.crud.trading.get_user_positions') as mock_get_positions:
            
            # Mock database and user data
            mock_db.return_value = MagicMock()
            
            mock_user = MagicMock()
            mock_user.deriv_token = "test_token"
            mock_get_user.return_value = mock_user
            
            mock_params = MagicMock()
            mock_params.max_daily_loss = 100
            mock_get_params.return_value = mock_params
            
            mock_get_positions.return_value = []  # No current positions
            
            result = await trading_executor._validate_execution(sample_signal_data)
            
            assert result["valid"] is True
            assert "user_data" in result
    
    @pytest.mark.asyncio
    async def test_validate_execution_no_user(self, trading_executor, sample_signal_data):
        """Test validation failure when user not found"""
        with patch('app.workers.trading_executor.get_database_sync') as mock_db, \
             patch('app.crud.users.get_user_by_id') as mock_get_user:
            
            mock_db.return_value = MagicMock()
            mock_get_user.return_value = None  # User not found
            
            result = await trading_executor._validate_execution(sample_signal_data)
            
            assert result["valid"] is False
            assert "User not found" in result["reason"]
    
    @pytest.mark.asyncio
    async def test_validate_execution_no_deriv_token(self, trading_executor, sample_signal_data):
        """Test validation failure when user has no Deriv token"""
        with patch('app.workers.trading_executor.get_database_sync') as mock_db, \
             patch('app.crud.users.get_user_by_id') as mock_get_user:
            
            mock_db.return_value = MagicMock()
            
            mock_user = MagicMock()
            mock_user.deriv_token = None  # No token
            mock_get_user.return_value = mock_user
            
            result = await trading_executor._validate_execution(sample_signal_data)
            
            assert result["valid"] is False
            assert "no Deriv API token" in result["reason"]
    
    @pytest.mark.asyncio
    async def test_final_risk_check_approved(self, trading_executor, sample_signal_data):
        """Test final risk check approval"""
        user_data = {
            "user": MagicMock(),
            "trading_params": MagicMock(),
            "positions": [],
            "daily_pnl": 0
        }
        
        with patch.object(trading_executor.risk_manager, 'assess_position_risk') as mock_risk:
            # Mock approved risk assessment
            mock_assessment = MagicMock()
            mock_assessment.recommended_action = "allow"
            mock_assessment.position_size_adjustment = 1.0
            mock_risk.return_value = mock_assessment
            
            result = await trading_executor._final_risk_check(sample_signal_data, user_data)
            
            assert result["approved"] is True
            assert result["adjusted_amount"] == sample_signal_data["recommended_amount"]
    
    @pytest.mark.asyncio
    async def test_final_risk_check_rejected(self, trading_executor, sample_signal_data):
        """Test final risk check rejection"""
        user_data = {
            "user": MagicMock(),
            "trading_params": MagicMock(),
            "positions": [],
            "daily_pnl": 0
        }
        
        with patch.object(trading_executor.risk_manager, 'assess_position_risk') as mock_risk:
            # Mock rejected risk assessment
            mock_assessment = MagicMock()
            mock_assessment.recommended_action = "halt_trading"
            mock_risk.return_value = mock_assessment
            
            result = await trading_executor._final_risk_check(sample_signal_data, user_data)
            
            assert result["approved"] is False
            assert "halt_trading" in result["reason"]
    
    @pytest.mark.asyncio
    async def test_execute_trade_success(self, trading_executor, sample_signal_data):
        """Test successful trade execution"""
        user_data = {
            "user": MagicMock(),
            "trading_params": MagicMock(),
            "positions": [],
            "daily_pnl": 0
        }
        user_data["user"].id = "test_user"
        user_data["user"].deriv_token = "test_token"
        
        with patch('app.workers.trading_executor.websocket_manager') as mock_ws_manager:
            # Mock successful WebSocket execution
            mock_ws = MagicMock()
            mock_ws.buy_contract.return_value = True
            mock_ws_manager.get_connection.return_value = mock_ws
            
            result = await trading_executor._execute_trade(sample_signal_data, user_data)
            
            assert result["success"] is True
            assert "contract_id" in result
            assert "entry_price" in result
    
    @pytest.mark.asyncio
    async def test_execute_trade_no_connection(self, trading_executor, sample_signal_data):
        """Test trade execution failure due to no WebSocket connection"""
        user_data = {
            "user": MagicMock(),
            "trading_params": MagicMock(),
            "positions": [],
            "daily_pnl": 0
        }
        user_data["user"].id = "test_user"
        
        with patch('app.workers.trading_executor.websocket_manager') as mock_ws_manager:
            # Mock no WebSocket connection
            mock_ws_manager.get_connection.return_value = None
            mock_ws_manager.create_connection.return_value = None
            
            result = await trading_executor._execute_trade(sample_signal_data, user_data)
            
            assert result["success"] is False
            assert "Could not establish Deriv connection" in result["error"]
    
    @pytest.mark.asyncio
    async def test_should_close_position_take_profit(self, trading_executor):
        """Test position should be closed due to take profit"""
        # Mock position
        position = MagicMock()
        position.user_id = "test_user"
        position.amount = 100
        position.entry_time = datetime.utcnow() - timedelta(minutes=2)
        position.duration = 10  # 10 minutes
        
        # Mock trading parameters
        with patch('app.workers.trading_executor.get_database_sync') as mock_db, \
             patch('app.crud.trading.get_user_trading_parameters') as mock_get_params:
            
            mock_db.return_value = MagicMock()
            
            mock_params = MagicMock()
            mock_params.take_profit = 20  # 20% take profit
            mock_params.stop_loss = 10   # 10% stop loss
            mock_get_params.return_value = mock_params
            
            # Test with profitable position (25% profit)
            current_pnl = 25  # 25% profit
            
            should_close, reason = await trading_executor._should_close_position(
                position, current_pnl, MagicMock()
            )
            
            assert should_close is True
            assert reason == "take_profit_reached"
    
    @pytest.mark.asyncio
    async def test_should_close_position_stop_loss(self, trading_executor):
        """Test position should be closed due to stop loss"""
        position = MagicMock()
        position.user_id = "test_user"
        position.amount = 100
        position.entry_time = datetime.utcnow() - timedelta(minutes=2)
        position.duration = 10
        
        with patch('app.workers.trading_executor.get_database_sync') as mock_db, \
             patch('app.crud.trading.get_user_trading_parameters') as mock_get_params:
            
            mock_db.return_value = MagicMock()
            
            mock_params = MagicMock()
            mock_params.take_profit = 20
            mock_params.stop_loss = 10  # 10% stop loss
            mock_get_params.return_value = mock_params
            
            # Test with losing position (-15% loss)
            current_pnl = -15
            
            should_close, reason = await trading_executor._should_close_position(
                position, current_pnl, MagicMock()
            )
            
            assert should_close is True
            assert reason == "stop_loss_triggered"
    
    @pytest.mark.asyncio
    async def test_should_close_position_duration_expired(self, trading_executor):
        """Test position should be closed due to duration expiry"""
        position = MagicMock()
        position.user_id = "test_user"
        position.amount = 100
        position.entry_time = datetime.utcnow() - timedelta(minutes=15)  # 15 minutes ago
        position.duration = 10  # 10 minute duration (expired)
        
        with patch('app.workers.trading_executor.get_database_sync') as mock_db, \
             patch('app.crud.trading.get_user_trading_parameters') as mock_get_params:
            
            mock_db.return_value = MagicMock()
            mock_params = MagicMock()
            mock_params.take_profit = 20
            mock_params.stop_loss = 10
            mock_get_params.return_value = mock_params
            
            current_pnl = 5  # Small profit
            
            should_close, reason = await trading_executor._should_close_position(
                position, current_pnl, MagicMock()
            )
            
            assert should_close is True
            assert reason == "duration_expired"
    
    def test_get_execution_status(self, trading_executor):
        """Test execution status retrieval"""
        # Mock some active executions
        trading_executor.active_executions = {
            "exec_1": {"status": "processing"},
            "exec_2": {"status": "completed"},
            "exec_3": {"status": "processing"}
        }
        
        # Mock Redis ping
        trading_executor.redis_client.ping.return_value = True
        
        status = trading_executor.get_execution_status()
        
        assert status["active_executions"] == 2  # Only processing ones
        assert status["total_executions"] == 3
        assert status["redis_connected"] is True


class TestCeleryTasks:
    """Test cases for Celery tasks"""
    
    @pytest.fixture
    def celery_app_test(self):
        """Create test Celery app"""
        celery_app.conf.task_always_eager = True
        celery_app.conf.task_eager_propagates = True
        return celery_app
    
    def test_health_check_task(self, celery_app_test):
        """Test health check task"""
        from app.workers.tasks import health_check
        
        result = health_check.delay()
        
        assert result.successful()
        task_result = result.get()
        assert task_result["status"] == "healthy"
        assert "timestamp" in task_result
    
    @patch('app.workers.tasks.market_monitor')
    def test_market_scan_scheduler_task(self, mock_monitor, celery_app_test):
        """Test market scan scheduler task"""
        from app.workers.tasks import market_scan_scheduler
        
        # Mock market monitor scan
        mock_monitor.scan_markets.return_value = {
            "symbols_scanned": 5,
            "signals_generated": 2,
            "timestamp": datetime.utcnow()
        }
        
        result = market_scan_scheduler.delay()
        
        assert result.successful()
        task_result = result.get()
        assert task_result["symbols_scanned"] == 5
        assert task_result["signals_generated"] == 2
    
    @patch('app.workers.tasks.trading_executor')
    def test_process_signal_task(self, mock_executor, celery_app_test):
        """Test process signal task"""
        from app.workers.tasks import process_signal
        
        signal_data = {
            "user_id": "test_user",
            "symbol": "R_10",
            "signal_type": "BUY_CALL",
            "recommended_amount": 50
        }
        
        # Mock successful execution
        mock_executor.execute_trade_signal.return_value = {
            "success": True,
            "trade_id": "12345"
        }
        
        result = process_signal.delay(signal_data)
        
        assert result.successful()
        task_result = result.get()
        assert task_result["success"] is True
        assert task_result["trade_id"] == "12345"


class TestCeleryIntegration:
    """Integration tests for Celery setup"""
    
    def test_celery_app_configuration(self):
        """Test Celery app is configured correctly"""
        assert celery_app.main == "deriv_workflow"
        assert celery_app.conf.task_serializer == "json"
        assert celery_app.conf.result_serializer == "json"
        assert celery_app.conf.timezone == "UTC"
    
    def test_celery_beat_schedule(self):
        """Test Celery beat schedule is configured"""
        beat_schedule = celery_app.conf.beat_schedule
        
        assert "market-scan" in beat_schedule
        assert "position-monitor" in beat_schedule
        assert "risk-monitor" in beat_schedule
        assert "model-retrain-check" in beat_schedule
        
        # Check task names
        assert beat_schedule["market-scan"]["task"] == "app.workers.tasks.market_scan_scheduler"
        assert beat_schedule["position-monitor"]["task"] == "app.workers.tasks.position_monitor_scheduler"
    
    def test_task_routes_configuration(self):
        """Test task routing is configured"""
        task_routes = celery_app.conf.task_routes
        
        assert "app.workers.tasks.market_scan" in task_routes
        assert task_routes["app.workers.tasks.market_scan"]["queue"] == "market_scan"
        
        assert "app.workers.tasks.execute_trade" in task_routes
        assert task_routes["app.workers.tasks.execute_trade"]["queue"] == "trading"


@pytest.mark.integration
class TestAutomationIntegration:
    """Integration tests for the complete automation system"""
    
    @pytest.mark.asyncio
    async def test_complete_signal_flow(self):
        """Test complete signal generation and execution flow"""
        # This would be a more complex integration test
        # that tests the entire flow from market scan to trade execution
        
        with patch('app.workers.market_monitor.redis.from_url'), \
             patch('app.workers.trading_executor.redis.from_url'), \
             patch('app.workers.market_monitor.get_database_sync'), \
             patch('app.workers.trading_executor.websocket_manager'):
            
            # Initialize components
            market_monitor = MarketMonitorWorker()
            trading_executor = TradingExecutorWorker()
            
            # Mock Redis
            market_monitor.redis_client = MagicMock()
            trading_executor.redis_client = MagicMock()
            
            # Test market scan
            scan_result = await market_monitor.scan_markets()
            assert "symbols_scanned" in scan_result
            
            # Test that components are initialized and functional
            assert market_monitor.get_market_status()["active"] is True
    
    def test_redis_connection_handling(self):
        """Test Redis connection handling"""
        # Test with mock Redis
        with patch('redis.from_url') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_redis.return_value = mock_client
            
            monitor = MarketMonitorWorker()
            status = monitor.get_market_status()
            
            assert status["redis_connected"] is True
    
    def test_error_handling_in_workers(self):
        """Test error handling in worker components"""
        with patch('app.workers.market_monitor.redis.from_url'):
            monitor = MarketMonitorWorker()
            monitor.redis_client = MagicMock()
            
            # Test that errors don't crash the worker
            monitor.redis_client.ping.side_effect = Exception("Redis error")
            
            try:
                status = monitor.get_market_status()
                # Should handle error gracefully
                assert "error" in status or status["active"] is False
            except Exception:
                pytest.fail("Worker should handle Redis errors gracefully")


# Mock async database functions for testing
@pytest.fixture(autouse=True)
def mock_async_db_functions():
    """Mock async database functions used in workers"""
    with patch('app.workers.tasks._get_active_positions_for_monitoring', return_value=[]), \
         patch('app.workers.tasks._get_users_with_active_positions', return_value=[]), \
         patch('app.workers.tasks._get_users_needing_retrain', return_value=[]), \
         patch('app.workers.tasks._get_all_trading_users', return_value=[]):
        yield


# Utility functions for testing
def create_mock_position(user_id="test_user", symbol="R_10", status="open", amount=50):
    """Create a mock trading position for testing"""
    position = MagicMock()
    position.id = "position_123"
    position.user_id = user_id
    position.symbol = symbol
    position.status = status
    position.amount = amount
    position.contract_type = "CALL"
    position.created_at = datetime.utcnow()
    position.entry_time = datetime.utcnow()
    position.duration = 10
    position.profit_loss = 0
    return position


def create_mock_user(user_id="test_user", has_deriv_token=True):
    """Create a mock user for testing"""
    user = MagicMock()
    user.id = user_id
    user.deriv_token = "test_token" if has_deriv_token else None
    return user
