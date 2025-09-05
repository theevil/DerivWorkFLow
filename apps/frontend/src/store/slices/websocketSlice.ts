import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import {
  WebSocketConnection,
  WebSocketMessage,
  WebSocketState,
  CreateConnectionRequest,
  SendMessageRequest,
} from '../../models';

// Initial state
const initialState: WebSocketState = {
  connections: {},
  messages: [],
  globalStatus: 'disconnected',
  isEnabled: true,
  autoReconnect: true,
  reconnectInterval: 5000,
  maxReconnectAttempts: 5,
  error: null,
  lastGlobalUpdate: null,
};

// Async thunks
export const createConnection = createAsyncThunk(
  'websocket/createConnection',
  async (request: CreateConnectionRequest, { rejectWithValue }) => {
    try {
      // This would typically be handled by a WebSocket service
      // For now, we'll simulate the connection creation
      const connection: WebSocketConnection = {
        id:
          request.id ||
          `ws_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        url: request.url,
        status: 'connecting',
        messageCount: 0,
        errorCount: 0,
        reconnectAttempts: 0,
        maxReconnectAttempts: request.maxReconnectAttempts || 5,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      return connection;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to create connection');
    }
  }
);

export const closeConnection = createAsyncThunk(
  'websocket/closeConnection',
  async (connectionId: string, { rejectWithValue }) => {
    try {
      // This would typically be handled by a WebSocket service
      return connectionId;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to close connection');
    }
  }
);

export const sendMessage = createAsyncThunk(
  'websocket/sendMessage',
  async (request: SendMessageRequest, { rejectWithValue }) => {
    try {
      // This would typically be handled by a WebSocket service
      const message: WebSocketMessage = {
        id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        type: request.type,
        data: request.data,
        timestamp: new Date().toISOString(),
        connectionId: request.connectionId,
      };

      return message;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to send message');
    }
  }
);

// WebSocket slice
const websocketSlice = createSlice({
  name: 'websocket',
  initialState,
  reducers: {
    // Clear error
    clearError: state => {
      state.error = null;
    },

    // Set global status
    setGlobalStatus: (
      state,
      action: PayloadAction<WebSocketState['globalStatus']>
    ) => {
      state.globalStatus = action.payload;
      state.lastGlobalUpdate = new Date().toISOString();
    },

    // Set enabled state
    setEnabled: (state, action: PayloadAction<boolean>) => {
      state.isEnabled = action.payload;
    },

    // Set auto reconnect
    setAutoReconnect: (state, action: PayloadAction<boolean>) => {
      state.autoReconnect = action.payload;
    },

    // Set reconnect interval
    setReconnectInterval: (state, action: PayloadAction<number>) => {
      state.reconnectInterval = action.payload;
    },

    // Set max reconnect attempts
    setMaxReconnectAttempts: (state, action: PayloadAction<number>) => {
      state.maxReconnectAttempts = action.payload;
    },

    // Update connection status
    updateConnectionStatus: (
      state,
      action: PayloadAction<{
        id: string;
        status: WebSocketConnection['status'];
      }>
    ) => {
      const { id, status } = action.payload;
      if (state.connections[id]) {
        state.connections[id].status = status;
        state.connections[id].updatedAt = new Date().toISOString();
      }
    },

    // Update connection ping/pong
    updateConnectionPingPong: (
      state,
      action: PayloadAction<{
        id: string;
        type: 'ping' | 'pong';
        timestamp: string;
      }>
    ) => {
      const { id, type, timestamp } = action.payload;
      if (state.connections[id]) {
        if (type === 'ping') {
          state.connections[id].lastPing = timestamp;
        } else {
          state.connections[id].lastPong = timestamp;
        }
        state.connections[id].updatedAt = new Date().toISOString();
      }
    },

    // Increment message count
    incrementMessageCount: (state, action: PayloadAction<string>) => {
      const connectionId = action.payload;
      if (state.connections[connectionId]) {
        state.connections[connectionId].messageCount++;
        state.connections[connectionId].updatedAt = new Date().toISOString();
      }
    },

    // Increment error count
    incrementErrorCount: (state, action: PayloadAction<string>) => {
      const connectionId = action.payload;
      if (state.connections[connectionId]) {
        state.connections[connectionId].errorCount++;
        state.connections[connectionId].updatedAt = new Date().toISOString();
      }
    },

    // Increment reconnect attempts
    incrementReconnectAttempts: (state, action: PayloadAction<string>) => {
      const connectionId = action.payload;
      if (state.connections[connectionId]) {
        state.connections[connectionId].reconnectAttempts++;
        state.connections[connectionId].updatedAt = new Date().toISOString();
      }
    },

    // Reset reconnect attempts
    resetReconnectAttempts: (state, action: PayloadAction<string>) => {
      const connectionId = action.payload;
      if (state.connections[connectionId]) {
        state.connections[connectionId].reconnectAttempts = 0;
        state.connections[connectionId].updatedAt = new Date().toISOString();
      }
    },

    // Add message
    addMessage: (state, action: PayloadAction<WebSocketMessage>) => {
      state.messages.push(action.payload);
      // Keep only last 1000 messages to prevent memory issues
      if (state.messages.length > 1000) {
        state.messages = state.messages.slice(-1000);
      }
    },

    // Clear messages
    clearMessages: state => {
      state.messages = [];
    },

    // Clear messages for connection
    clearConnectionMessages: (state, action: PayloadAction<string>) => {
      const connectionId = action.payload;
      state.messages = state.messages.filter(
        msg => msg.connectionId !== connectionId
      );
    },

    // Set error
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
    },

    // Reset WebSocket state
    resetWebSocket: state => {
      state.connections = {};
      state.messages = [];
      state.globalStatus = 'disconnected';
      state.error = null;
      state.lastGlobalUpdate = null;
    },
  },
  extraReducers: builder => {
    // Create connection
    builder
      .addCase(createConnection.pending, state => {
        state.error = null;
      })
      .addCase(createConnection.fulfilled, (state, action) => {
        const connection = action.payload;
        state.connections[connection.id] = connection;
        state.lastGlobalUpdate = new Date().toISOString();

        // Update global status if this is the first connection
        if (Object.keys(state.connections).length === 1) {
          state.globalStatus = 'connecting';
        }
      })
      .addCase(createConnection.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // Close connection
    builder
      .addCase(closeConnection.pending, state => {
        state.error = null;
      })
      .addCase(closeConnection.fulfilled, (state, action) => {
        const connectionId = action.payload;
        delete state.connections[connectionId];
        state.lastGlobalUpdate = new Date().toISOString();

        // Update global status if no connections remain
        if (Object.keys(state.connections).length === 0) {
          state.globalStatus = 'disconnected';
        }
      })
      .addCase(closeConnection.rejected, (state, action) => {
        state.error = action.payload as string;
      });

    // Send message
    builder
      .addCase(sendMessage.pending, state => {
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        const message = action.payload;
        state.messages.push(message);
        state.lastGlobalUpdate = new Date().toISOString();

        // Keep only last 1000 messages
        if (state.messages.length > 1000) {
          state.messages = state.messages.slice(-1000);
        }
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});

// Export actions
export const {
  clearError,
  setGlobalStatus,
  setEnabled,
  setAutoReconnect,
  setReconnectInterval,
  setMaxReconnectAttempts,
  updateConnectionStatus,
  updateConnectionPingPong,
  incrementMessageCount,
  incrementErrorCount,
  incrementReconnectAttempts,
  resetReconnectAttempts,
  addMessage,
  clearMessages,
  clearConnectionMessages,
  setError,
  resetWebSocket,
} = websocketSlice.actions;

// Export selectors
export const selectWebSocket = (state: { websocket: WebSocketState }) =>
  state.websocket;
export const selectConnections = (state: { websocket: WebSocketState }) =>
  state.websocket.connections;
export const selectMessages = (state: { websocket: WebSocketState }) =>
  state.websocket.messages;
export const selectGlobalStatus = (state: { websocket: WebSocketState }) =>
  state.websocket.globalStatus;
export const selectIsEnabled = (state: { websocket: WebSocketState }) =>
  state.websocket.isEnabled;
export const selectAutoReconnect = (state: { websocket: WebSocketState }) =>
  state.websocket.autoReconnect;
export const selectReconnectInterval = (state: { websocket: WebSocketState }) =>
  state.websocket.reconnectInterval;
export const selectMaxReconnectAttempts = (state: {
  websocket: WebSocketState;
}) => state.websocket.maxReconnectAttempts;
export const selectError = (state: { websocket: WebSocketState }) =>
  state.websocket.error;
export const selectLastGlobalUpdate = (state: { websocket: WebSocketState }) =>
  state.websocket.lastGlobalUpdate;

// Helper selectors
export const selectConnectionById = (
  state: { websocket: WebSocketState },
  connectionId: string
) => state.websocket.connections[connectionId];

export const selectMessagesByConnection = (
  state: { websocket: WebSocketState },
  connectionId: string
) => state.websocket.messages.filter(msg => msg.connectionId === connectionId);

export const selectActiveConnections = (state: { websocket: WebSocketState }) =>
  Object.values(state.websocket.connections).filter(
    conn => conn.status === 'connected' || conn.status === 'connecting'
  );

export const selectConnectionCount = (state: { websocket: WebSocketState }) =>
  Object.keys(state.websocket.connections).length;

// Export reducer
export default websocketSlice.reducer;
