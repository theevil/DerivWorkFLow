import { config } from '../config/env';

export interface WebSocketMessage {
  type: string;
  data?: any;
  message?: string;
  status?: string;
  timestamp?: number;
  code?: number;
}

type TimeoutType = ReturnType<typeof setTimeout>;

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
  private messageBuffer: any[] = [];
  private worker: Worker | null = null;
  private readonly BUFFER_FLUSH_INTERVAL = 100; // ms
  private readonly MESSAGE_BATCH_SIZE = 10;
  private flushTimeout: TimeoutType | null = null;
  private lastHeartbeat: number = Date.now();
  private heartbeatInterval: TimeoutType | null = null;

  private readonly WS_CONFIG = {
    RECONNECT_MAX_ATTEMPTS: 5,
    RECONNECT_BASE_DELAY: 1000,
    MESSAGE_BATCH_SIZE: 10,
    MESSAGE_BATCH_INTERVAL: 100,
    HEARTBEAT_INTERVAL: 15000,
    CONNECTION_TIMEOUT: 30000
  };

  constructor(token?: string) {
    this.token = token || null;
    this.initializeWorker();
  }

  setToken(token: string) {
    this.token = token;
  }

  private initializeWorker() {
    if (typeof Worker !== 'undefined') {
      this.worker = new Worker(new URL('./websocket.worker.ts', import.meta.url));
      this.worker.onmessage = this.handleWorkerMessage.bind(this);
    }
  }

  private handleWorkerMessage(event: MessageEvent) {
    const { type, data } = event.data;
    this.notifyHandlers(type, data);
  }

  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'heartbeat' }));
        this.lastHeartbeat = Date.now();
      }
    }, this.WS_CONFIG.HEARTBEAT_INTERVAL);
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private bufferMessage(message: any) {
    this.messageBuffer.push(message);

    if (this.messageBuffer.length >= this.MESSAGE_BATCH_SIZE) {
      this.flushMessageBuffer();
    } else if (!this.flushTimeout) {
      this.flushTimeout = setTimeout(() => this.flushMessageBuffer(), this.BUFFER_FLUSH_INTERVAL);
    }
  }

  private flushMessageBuffer() {
    if (this.messageBuffer.length === 0) return;

    if (this.worker) {
      this.worker.postMessage({
        type: 'PROCESS_BATCH',
        data: this.messageBuffer
      });
    } else {
      // Fallback if worker is not available
      this.messageBuffer.forEach(msg => this.notifyHandlers(msg.type, msg));
    }

    this.messageBuffer = [];
    if (this.flushTimeout) {
      clearTimeout(this.flushTimeout);
      this.flushTimeout = null;
    }
  }

  async connect() {
    if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
      return;
    }

    this.isConnecting = true;

    try {
      // Reset any existing connection
      if (this.ws) {
        this.ws.close();
        this.ws = null;
      }

      const wsUrl = `${config.wsUrl}?token=${this.token}`;
      this.ws = new WebSocket(wsUrl);

      // Set up connection timeout
      const connectionTimeout = setTimeout(() => {
        if (this.ws?.readyState !== WebSocket.OPEN) {
          console.error('WebSocket connection timeout');
          this.ws?.close();
          this.handleError(new Error('Connection timeout'));
        }
      }, this.WS_CONFIG.CONNECTION_TIMEOUT);

      // Set up event handlers
      this.ws.onopen = () => {
        clearTimeout(connectionTimeout);
        this.handleOpen();
      };
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);

      this.startHeartbeat();

    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.handleError(error);
    } finally {
      this.isConnecting = false;
    }
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

  private notifyHandlers(type: string, data: any) {
    const handlers = this.eventHandlers.get(type) || [];
    handlers.forEach(handler => handler({ type, data }));
  }

  private handleOpen() {
    console.log('WebSocket connected');
    this.reconnectAttempts = 0;
    this.notifyHandlers('connection', { status: 'connected' });
  }

  private handleClose(event: CloseEvent) {
    this.stopHeartbeat();
    this.notifyHandlers('connection', {
      status: 'disconnected',
      code: event.code,
      reason: event.reason
    });

    if (this.reconnectAttempts < this.WS_CONFIG.RECONNECT_MAX_ATTEMPTS) {
      const delay = Math.min(
        this.WS_CONFIG.RECONNECT_BASE_DELAY * Math.pow(2, this.reconnectAttempts),
        30000
      );
      this.reconnectAttempts++;
      setTimeout(() => this.connect(), delay);
    }
  }

  private handleError(error: any) {
    console.error('WebSocket error:', error);
    this.notifyHandlers('error', { error });
  }

  private handleMessage(event: MessageEvent) {
    try {
      const message = JSON.parse(event.data);

      // Manejar heartbeat
      if (message.type === 'heartbeat') {
        this.lastHeartbeat = Date.now();
        return;
      }

      // Buffering de mensajes
      this.bufferMessage(message);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
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
