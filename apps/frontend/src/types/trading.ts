// Trading Types for Frontend
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  name: string;
  password: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  deriv_token?: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface TradePosition {
  id: string;
  user_id: string;
  symbol: string;
  contract_type: 'CALL' | 'PUT';
  amount: number;
  entry_spot?: number;
  current_spot?: number;
  profit_loss?: number;
  status: 'open' | 'closed' | 'pending';
  created_at: string;
  updated_at: string;
}

export interface TradingStats {
  total_profit: number;
  total_trades: number;
  win_rate: number;
  avg_profit: number;
  max_profit: number;
  max_loss: number;
  active_positions: number;
}

export interface TradingParametersRequest {
  profit_top: number;
  profit_loss: number;
  stop_loss: number;
  take_profit: number;
  max_daily_loss: number;
  position_size: number;
}

export interface TradingParameters extends TradingParametersRequest {
  id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface CreateTradeRequest {
  symbol: string;
  contract_type: 'CALL' | 'PUT';
  amount: number;
  duration: number;
  duration_unit: 'S' | 'M' | 'H' | 'D';
  barrier?: number;
}

export interface MarketData {
  symbol: string;
  current_price: number;
  change_24h: number;
  change_percentage_24h: number;
  high_24h: number;
  low_24h: number;
  volume_24h: number;
  timestamp: string;
}

export interface AIAnalysis {
  symbol: string;
  recommendation: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reasoning: string;
  technical_indicators: {
    rsi?: number;
    macd?: number;
    moving_average?: number;
    bollinger_bands?: {
      upper: number;
      middle: number;
      lower: number;
    };
  };
  timestamp: string;
}
