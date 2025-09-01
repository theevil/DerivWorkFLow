// Deriv API Types
export interface DerivTicksRequest {
  ticks: string;  // Symbol
  subscribe?: 1;
}

export interface DerivTicksResponse {
  echo_req: DerivTicksRequest;
  msg_type: 'tick';
  tick: {
    ask: number;
    bid: number;
    epoch: number;
    id: string;
    pip_size: number;
    quote: number;
    symbol: string;
  };
}

export interface DerivBuyRequest {
  buy: string;  // Contract ID
  price: number;
  parameters: {
    amount: number;
    basis: 'stake';
    contract_type: string;
    currency: string;
    duration: number;
    duration_unit: string;
    symbol: string;
  };
}

export interface DerivBuyResponse {
  buy: {
    buy_price: number;
    contract_id: number;
    longcode: string;
    start_time: number;
    transaction_id: number;
  };
  echo_req: DerivBuyRequest;
  msg_type: 'buy';
}

export interface DerivContractUpdateResponse {
  msg_type: 'proposal_open_contract';
  proposal_open_contract: {
    contract_id: number;
    currency: string;
    date_start: number;
    date_expiry: number;
    entry_spot: number;
    current_spot: number;
    profit: number;
    profit_percentage: number;
    status: string;
    underlying: string;
  };
}

export interface DerivAuthRequest {
  authorize: string;  // API Token
}

export interface DerivAuthResponse {
  msg_type: 'authorize';
  authorize: {
    balance: number;
    currency: string;
    email: string;
    loginid: string;
  };
}
