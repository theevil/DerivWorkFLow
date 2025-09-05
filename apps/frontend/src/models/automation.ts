// Automation Models

export interface AutomationStrategy {
  id: string;
  name: string;
  description: string;
  type:
    | 'trend_following'
    | 'mean_reversion'
    | 'breakout'
    | 'scalping'
    | 'custom';
  status: 'active' | 'paused' | 'stopped' | 'error' | 'running';
  symbol: string;
  parameters: Record<string, any>;
  riskSettings: {
    maxPositionSize: number;
    stopLoss: number;
    takeProfit: number;
    maxDailyLoss: number;
    maxDrawdown: number;
  };
  performance: {
    totalTrades: number;
    winningTrades: number;
    losingTrades: number;
    winRate: number;
    totalPnL: number;
    averageWin: number;
    averageLoss: number;
    maxDrawdown: number;
    sharpeRatio: number;
  };
  schedule: {
    enabled: boolean;
    startTime: string;
    endTime: string;
    timezone: string;
    daysOfWeek: number[];
  };
  createdAt: string;
  updatedAt: string;
  lastExecution?: string;
  nextExecution?: string;
  startedAt?: string;
  stoppedAt?: string;
}

export interface AutomationWorker {
  id: string;
  strategyId: string;
  status: 'running' | 'stopped' | 'error' | 'starting' | 'stopping';
  pid?: number;
  memoryUsage: number;
  cpuUsage: number;
  uptime: number;
  lastHeartbeat: string;
  error?: string;
  logs: Array<{
    timestamp: string;
    level: 'info' | 'warn' | 'error' | 'debug';
    message: string;
    data?: any;
  }>;
}

export interface AutomationRule {
  id: string;
  strategyId: string;
  name: string;
  type: 'entry' | 'exit' | 'risk' | 'timing';
  conditions: Array<{
    field: string;
    operator:
      | 'equals'
      | 'not_equals'
      | 'greater_than'
      | 'less_than'
      | 'contains'
      | 'regex';
    value: any;
    logicalOperator?: 'AND' | 'OR';
  }>;
  actions: Array<{
    type:
      | 'buy'
      | 'sell'
      | 'close'
      | 'modify_position'
      | 'send_alert'
      | 'execute_function';
    parameters: Record<string, any>;
  }>;
  priority: number;
  enabled: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface AutomationState {
  strategies: AutomationStrategy[];
  workers: AutomationWorker[];
  rules: AutomationRule[];
  globalRisk: {
    maxDrawdown: number;
    maxDailyLoss: number;
    maxPositionSize: number;
    stopLossEnabled: boolean;
    takeProfitEnabled: boolean;
  };
  performance: {
    totalPnL: number;
    winRate: number;
    totalTrades: number;
    averageReturn: number;
    sharpeRatio: number;
  };
  status: 'idle' | 'loading' | 'error';
  error: string | null;
  lastUpdate: string | null;
}

export interface CreateStrategyRequest {
  name: string;
  description: string;
  type: AutomationStrategy['type'];
  symbol: string;
  parameters: Record<string, any>;
  riskSettings: AutomationStrategy['riskSettings'];
  schedule?: AutomationStrategy['schedule'];
}

export interface UpdateStrategyRequest {
  name?: string;
  description?: string;
  type?: AutomationStrategy['type'];
  symbol?: string;
  parameters?: Record<string, any>;
  riskSettings?: Partial<AutomationStrategy['riskSettings']>;
  schedule?: AutomationStrategy['schedule'];
}

export interface StartStrategyRequest {
  strategyId: string;
  parameters?: Record<string, any>;
}

export interface StopStrategyRequest {
  strategyId: string;
  force?: boolean;
}
