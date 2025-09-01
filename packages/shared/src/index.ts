// API Response Types
export type ApiHealth = { status: 'ok' };
export type ApiRoot = { message: string; env: string };

// Auth Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest extends LoginRequest {
  name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  deriv_token?: string;
  created_at: string;
  updated_at: string;
}

// Trading Types
export interface TradingParameters {
  profit_top: number;
  profit_loss: number;
  stop_loss: number;
  take_profit: number;
  max_daily_loss: number;
  position_size: number;
}

export interface DerivCredentials {
  app_id: string;
  api_token: string;
}

export interface TradePosition {
  id: string;
  user_id: string;
  symbol: string;
  contract_type: string;
  amount: number;
  duration: number;
  duration_unit: string;
  contract_id?: string;
  entry_spot?: number;
  exit_spot?: number;
  current_spot?: number;
  profit_loss?: number;
  status: string;
  entry_time?: string;
  exit_time?: string;
  created_at: string;
  updated_at: string;
}

export interface TradingParametersRequest {
  profit_top: number;
  profit_loss: number;
  stop_loss: number;
  take_profit: number;
  max_daily_loss: number;
  position_size: number;
}

export interface TradingSignal {
  id: string;
  user_id: string;
  symbol: string;
  signal_type: string;
  confidence: number;
  recommended_amount: number;
  recommended_duration: number;
  reasoning: string;
  created_at: string;
  executed: boolean;
  trade_id?: string;
}

export interface TradingStats {
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  total_profit: number;
  avg_profit: number;
  max_profit: number;
  max_loss: number;
  win_rate: number;
}