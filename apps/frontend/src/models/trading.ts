// Trading Models

export interface TradingPosition {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  amount: number;
  price: number;
  status: 'open' | 'closed' | 'pending' | 'cancelled';
  profitLoss?: number;
  openTime: string;
  closeTime?: string;
  stopLoss?: number;
  takeProfit?: number;
  leverage?: number;
  margin?: number;
}

export interface MarketData {
  symbol: string;
  bid: number;
  ask: number;
  last: number;
  change: number;
  changePercent: number;
  volume: number;
  high: number;
  low: number;
  timestamp: string;
}

export interface TradingOrder {
  id: string;
  symbol: string;
  type: 'market' | 'limit' | 'stop' | 'stop_limit';
  side: 'buy' | 'sell';
  amount: number;
  price?: number;
  stopPrice?: number;
  status: 'pending' | 'filled' | 'cancelled' | 'rejected';
  filledAmount: number;
  remainingAmount: number;
  averagePrice?: number;
  createdAt: string;
  updatedAt: string;
}

export interface TradingState {
  positions: TradingPosition[];
  orders: TradingOrder[];
  marketData: Record<string, MarketData>;
  portfolio: {
    balance: number;
    equity: number;
    margin: number;
    freeMargin: number;
    marginLevel: number;
    totalPnL: number;
    dailyPnL: number;
  };
  isLoading: boolean;
  error: string | null;
  lastUpdate: string | null;
  selectedSymbol: string | null;
  tradingEnabled: boolean;
  riskLevel: 'low' | 'medium' | 'high';
}

export interface OpenPositionRequest {
  symbol: string;
  type: 'buy' | 'sell';
  amount: number;
  leverage?: number;
  stopLoss?: number;
  takeProfit?: number;
}

export interface ClosePositionRequest {
  positionId: string;
  amount?: number; // If not provided, close entire position
}

export interface PlaceOrderRequest {
  symbol: string;
  type: 'market' | 'limit' | 'stop' | 'stop_limit';
  side: 'buy' | 'sell';
  amount: number;
  price?: number;
  stopPrice?: number;
  timeInForce?: 'GTC' | 'IOC' | 'FOK';
}
