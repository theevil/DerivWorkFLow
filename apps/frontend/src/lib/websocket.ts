import { config } from '../config/env';

export interface WebSocketMessage {
  type: string;
  data?: any;
  message?: string;
  status?: string;
  timestamp?: number;
}

export interface TickData {
  symbol: string;
  tick: number;
  epoch: number;
  ask: number;
  bid: number;
  quote: number;
}

export interface PortfolioData {
  portfolio: {
    contracts: Array<{
      contract_id: string;
      symbol: string;
      contract_type: string;
      buy_price: number;
      current_spot?: number;
      profit_loss?: number;
      status: string;
    }>;
  };
}

export type WebSocketEventHandler = (message: WebSocketMessage) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private token: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private eventHandlers: Map<string, WebSocketEventHandler[]> = new Map();
  private isConnecting = false;

  constructor(token?: string) {
    this.token = token;
  }

  setToken(token: string) {
    this.token = token;
  }

  connect(): Promise<boolean> {
    return new Promise((resolve, reject) => {
      if (!this.token) {
        reject(new Error('No authentication token provided'));
        return;
      }

      if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
        resolve(false);
        return;
      }

      this.isConnecting = true;

      const wsUrl = `${config.wsUrl}/ws/${this.token}`.replace('http', 'ws');

      try {
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          console.log('WebSocket connected');
          this.emit('connection', { type: 'connection', status: 'connected' });
          resolve(true);
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          this.isConnecting = false;
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.emit('disconnection', {
            type: 'disconnection',
            status: 'disconnected',
            code: event.code,
            reason: event.reason
          });

          // Auto-reconnect unless it was a manual close
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          this.isConnecting = false;
          console.error('WebSocket error:', error);
          this.emit('error', {
            type: 'error',
            message: 'WebSocket connection error'
          });
          reject(error);
        };

        // Connection timeout
        setTimeout(() => {
          if (this.isConnecting) {
            this.isConnecting = false;
            this.ws?.close();
            reject(new Error('Connection timeout'));
          }
        }, config.wsReconnectInterval);

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  disconnect() {
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
    this.reconnectAttempts = this.maxReconnectAttempts; // Prevent auto-reconnect
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);

      setTimeout(() => {
        if (this.reconnectAttempts <= this.maxReconnectAttempts) {
          this.connect().catch(console.error);
        }
      }, this.reconnectInterval * this.reconnectAttempts);
    }
  }

  private handleMessage(message: WebSocketMessage) {
    console.log('WebSocket message received:', message);
    this.emit(message.type, message);
  }

  send(message: any): boolean {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
        return true;
      } catch (error) {
        console.error('Failed to send WebSocket message:', error);
        return false;
      }
    }
    console.warn('WebSocket is not connected');
    return false;
  }

  // Event handling
  on(event: string, handler: WebSocketEventHandler) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, []);
    }
    this.eventHandlers.get(event)!.push(handler);
  }

  off(event: string, handler: WebSocketEventHandler) {
    if (this.eventHandlers.has(event)) {
      const handlers = this.eventHandlers.get(event)!;
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  private emit(event: string, message: WebSocketMessage) {
    if (this.eventHandlers.has(event)) {
      this.eventHandlers.get(event)!.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error('Error in WebSocket event handler:', error);
        }
      });
    }
  }

  // Trading specific methods
  subscribeToTicks(symbol: string): boolean {
    return this.send({
      type: 'subscribe_ticks',
      symbol: symbol
    });
  }

  unsubscribeFromTicks(symbol: string): boolean {
    return this.send({
      type: 'unsubscribe_ticks',
      symbol: symbol
    });
  }

  buyContract(contractData: {
    contract_type: 'CALL' | 'PUT';
    symbol: string;
    amount: number;
    duration: number;
    duration_unit?: string;
    barrier?: number;
  }): boolean {
    return this.send({
      type: 'buy_contract',
      ...contractData
    });
  }

  sellContract(contractId: string, price?: number): boolean {
    return this.send({
      type: 'sell_contract',
      contract_id: contractId,
      price: price
    });
  }

  getPortfolio(): boolean {
    return this.send({
      type: 'get_portfolio'
    });
  }

  ping(): boolean {
    return this.send({
      type: 'ping',
      timestamp: Date.now()
    });
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  getReadyState(): number | null {
    return this.ws?.readyState ?? null;
  }
}

// Create singleton instance
let webSocketClient: WebSocketClient | null = null;

export const getWebSocketClient = (token?: string): WebSocketClient => {
  if (!webSocketClient) {
    webSocketClient = new WebSocketClient(token);
  } else if (token) {
    webSocketClient.setToken(token);
  }
  return webSocketClient;
};

export const disconnectWebSocket = () => {
  if (webSocketClient) {
    webSocketClient.disconnect();
    webSocketClient = null;
  }
};
