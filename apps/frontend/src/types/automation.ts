/**
 * TypeScript types for automation features
 */

export interface AutoTradingConfig {
  enabled: boolean;
  max_concurrent_positions: number;
  market_scan_interval: number;
  position_monitor_interval: number;
  auto_stop_loss: boolean;
  auto_take_profit: boolean;
}

export interface WorkerStatus {
  active: boolean;
  symbols_monitored?: number;
  last_scan?: string;
  cache_status?: Record<string, boolean>;
  redis_connected: boolean;
  monitoring_intervals?: {
    market_scan: number;
    position_monitor: number;
  };
}

export interface ExecutorStatus {
  active_executions: number;
  total_executions: number;
  redis_connected: boolean;
  auto_trading_enabled: boolean;
  max_concurrent_positions: number;
}

export interface SystemStatus {
  market_monitor: WorkerStatus;
  trading_executor: ExecutorStatus;
  celery_active_tasks: number;
  redis_connected: boolean;
}

export interface TaskStatus {
  task_id: string;
  status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | 'RETRY' | 'REVOKED';
  result?: any;
  timestamp: string;
}

export interface ActiveTask {
  id: string;
  name: string;
  args: any[];
  kwargs: Record<string, any>;
  time_start?: string;
  eta?: string;
  worker: string;
}

export interface QueueStats {
  length: number;
  queue_key: string;
}

export interface Alert {
  id: string;
  type: 'emergency_stop' | 'risk_warning' | 'position_closed' | 'system_error';
  reason: string;
  timestamp: string;
  acknowledged: boolean;
  positions_closed?: string[];
}

export interface AutomationPerformance {
  period_days: number;
  start_date: string;
  end_date: string;
  trading_stats: {
    total_trades: number;
    profitable_trades: number;
    total_profit: number;
    avg_profit: number;
    max_profit: number;
    min_profit: number;
    win_rate: number;
  };
  user_id: string;
}

export interface EmergencyStopRequest {
  reason: string;
  close_positions: boolean;
}

export interface AutomationSettings {
  auto_trading_enabled: boolean;
  config: AutoTradingConfig;
  last_updated?: string;
}

// Chart data types
export interface PerformanceChartData {
  date: string;
  profit: number;
  trades: number;
  win_rate: number;
}

export interface TaskQueueData {
  queue: string;
  length: number;
  processing_rate: number;
}

// Real-time updates
export interface AutomationUpdate {
  type:
    | 'signal_generated'
    | 'trade_executed'
    | 'position_closed'
    | 'alert_created';
  data: any;
  timestamp: string;
}

// API Response types
export interface AutomationConfigResponse {
  enabled: boolean;
  config: AutoTradingConfig;
  last_updated?: string;
}

export interface EmergencyStopResponse {
  message: string;
  task_id: string;
  user_id: string;
  reason: string;
  close_positions: boolean;
}

export interface TriggerTaskResponse {
  message: string;
  task_id: string;
  status: 'scheduled' | 'started' | 'failed';
}

export interface HealthCheckResponse {
  health_check: {
    status: 'healthy' | 'unhealthy';
    timestamp: string;
    worker_id: string;
  };
  task_id: string;
  system_status: 'healthy' | 'unhealthy';
}

// Store state types
export interface AutomationState {
  // Configuration
  config: AutomationSettings | null;
  isConfigLoading: boolean;

  // System status
  systemStatus: SystemStatus | null;
  isStatusLoading: boolean;
  lastStatusUpdate: string | null;

  // Tasks
  activeTasks: Record<string, ActiveTask[]>;
  taskHistory: TaskStatus[];
  isTasksLoading: boolean;

  // Alerts
  alerts: Alert[];
  unacknowledgedCount: number;
  isAlertsLoading: boolean;

  // Performance
  performance: AutomationPerformance | null;
  performanceHistory: PerformanceChartData[];
  isPerformanceLoading: boolean;

  // Queue stats
  queueStats: Record<string, QueueStats>;
  isQueueStatsLoading: boolean;

  // Real-time updates
  isConnected: boolean;
  lastUpdate: string | null;
}

// WebSocket message types
export interface AutomationWebSocketMessage {
  type: 'automation_update';
  data: AutomationUpdate;
}

// Component props types
export interface AutomationDashboardProps {
  className?: string;
}

export interface WorkerStatusCardProps {
  title: string;
  status: WorkerStatus | ExecutorStatus;
  isLoading?: boolean;
}

export interface AutoTradingConfigModalProps {
  opened: boolean;
  onClose: () => void;
  currentConfig?: AutomationSettings;
  onSave: (config: AutoTradingConfig) => Promise<void>;
}

export interface AlertsListProps {
  alerts: Alert[];
  onAcknowledge: (alertId: string) => Promise<void>;
  isLoading?: boolean;
}

export interface PerformanceChartProps {
  data: PerformanceChartData[];
  height?: number;
  showTooltip?: boolean;
}

export interface EmergencyStopButtonProps {
  onEmergencyStop: (request: EmergencyStopRequest) => Promise<void>;
  isLoading?: boolean;
  disabled?: boolean;
}

// Form types
export interface AutoTradingConfigForm {
  enabled: boolean;
  max_concurrent_positions: number;
  market_scan_interval: number;
  position_monitor_interval: number;
  auto_stop_loss: boolean;
  auto_take_profit: boolean;
}

export interface EmergencyStopForm {
  reason: string;
  close_positions: boolean;
}
