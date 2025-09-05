// WebSocket Models

export interface WebSocketConnection {
  id: string;
  url: string;
  status:
    | 'connecting'
    | 'connected'
    | 'disconnected'
    | 'error'
    | 'reconnecting';
  lastMessage?: any;
  lastPing?: string;
  lastPong?: string;
  messageCount: number;
  errorCount: number;
  reconnectAttempts: number;
  maxReconnectAttempts: number;
  createdAt: string;
  updatedAt: string;
}

export interface WebSocketMessage {
  id: string;
  type: string;
  data: any;
  timestamp: string;
  connectionId: string;
}

export interface WebSocketState {
  connections: Record<string, WebSocketConnection>;
  messages: WebSocketMessage[];
  globalStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
  isEnabled: boolean;
  autoReconnect: boolean;
  reconnectInterval: number;
  maxReconnectAttempts: number;
  error: string | null;
  lastGlobalUpdate: string | null;
}

export interface CreateConnectionRequest {
  url: string;
  id?: string;
  autoReconnect?: boolean;
  maxReconnectAttempts?: number;
}

export interface SendMessageRequest {
  connectionId: string;
  type: string;
  data: any;
}
