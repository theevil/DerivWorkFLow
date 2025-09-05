import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { http } from '../../lib/http-client';
import { AutomationState } from '../../types/automation';

// Initial state
const initialState: AutomationState = {
  // Configuration
  config: null,
  isConfigLoading: false,

  // System status
  systemStatus: null,
  isStatusLoading: false,
  lastStatusUpdate: null,

  // Tasks
  activeTasks: {},
  taskHistory: [],
  isTasksLoading: false,

  // Alerts
  alerts: [],
  unacknowledgedCount: 0,
  isAlertsLoading: false,

  // Performance
  performance: null,
  performanceHistory: [],
  isPerformanceLoading: false,

  // Queue stats
  queueStats: {},
  isQueueStatsLoading: false,

  // Real-time updates
  isConnected: false,
  lastUpdate: null,
};

// Async thunks

// New automation actions
export const loadConfig = createAsyncThunk(
  'automation/loadConfig',
  async (_, { rejectWithValue }) => {
    try {
      const response = await http.get('/automation/config');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to load config'
      );
    }
  }
);

export const loadSystemStatus = createAsyncThunk(
  'automation/loadSystemStatus',
  async (_, { rejectWithValue }) => {
    try {
      const response = await http.get('/automation/status');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to load system status'
      );
    }
  }
);

export const loadAlerts = createAsyncThunk(
  'automation/loadAlerts',
  async (_, { rejectWithValue }) => {
    try {
      const response = await http.get('/automation/alerts');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to load alerts'
      );
    }
  }
);

export const triggerMarketScan = createAsyncThunk(
  'automation/triggerMarketScan',
  async (_, { rejectWithValue }) => {
    try {
      const response = await http.post('/automation/trigger/market-scan');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to trigger market scan'
      );
    }
  }
);

export const triggerPositionMonitor = createAsyncThunk(
  'automation/triggerPositionMonitor',
  async (_, { rejectWithValue }) => {
    try {
      const response = await http.post('/automation/trigger/position-monitor');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to trigger position monitor'
      );
    }
  }
);

export const triggerModelRetrain = createAsyncThunk(
  'automation/triggerModelRetrain',
  async (_, { rejectWithValue }) => {
    try {
      const response = await http.post('/automation/trigger/model-retrain');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to trigger model retrain'
      );
    }
  }
);

export const runHealthCheck = createAsyncThunk(
  'automation/runHealthCheck',
  async (_, { rejectWithValue }) => {
    try {
      const response = await http.post('/automation/health-check');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to run health check'
      );
    }
  }
);

export const triggerEmergencyStop = createAsyncThunk(
  'automation/triggerEmergencyStop',
  async (request: any, { rejectWithValue }) => {
    try {
      const response = await http.post('/automation/emergency-stop', request);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to trigger emergency stop'
      );
    }
  }
);

export const acknowledgeAlert = createAsyncThunk(
  'automation/acknowledgeAlert',
  async (alertId: string, { rejectWithValue }) => {
    try {
      const response = await http.post(
        `/automation/alerts/${alertId}/acknowledge`
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to acknowledge alert'
      );
    }
  }
);

export const updateConfig = createAsyncThunk(
  'automation/updateConfig',
  async (config: any, { rejectWithValue }) => {
    try {
      const response = await http.put('/automation/config', config);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to update config'
      );
    }
  }
);

// Automation slice
const automationSlice = createSlice({
  name: 'automation',
  initialState,
  reducers: {
    // Update last update
    updateLastUpdate: state => {
      state.lastUpdate = new Date().toISOString();
    },

    // Set connected status
    setConnected: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload;
      state.lastUpdate = new Date().toISOString();
    },
  },
  extraReducers: builder => {
    // Load config
    builder
      .addCase(loadConfig.pending, state => {
        state.isConfigLoading = true;
      })
      .addCase(loadConfig.fulfilled, (state, action) => {
        state.config = action.payload;
        state.isConfigLoading = false;
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(loadConfig.rejected, (state, action) => {
        state.isConfigLoading = false;
        state.lastUpdate = new Date().toISOString();
      });

    // Load system status
    builder
      .addCase(loadSystemStatus.pending, state => {
        state.isStatusLoading = true;
      })
      .addCase(loadSystemStatus.fulfilled, (state, action) => {
        state.systemStatus = action.payload;
        state.isStatusLoading = false;
        state.lastStatusUpdate = new Date().toISOString();
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(loadSystemStatus.rejected, (state, action) => {
        state.isStatusLoading = false;
        state.lastUpdate = new Date().toISOString();
      });

    // Load alerts
    builder
      .addCase(loadAlerts.pending, state => {
        state.isAlertsLoading = true;
      })
      .addCase(loadAlerts.fulfilled, (state, action) => {
        state.alerts = action.payload.alerts || [];
        state.unacknowledgedCount = action.payload.unacknowledged_count || 0;
        state.isAlertsLoading = false;
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(loadAlerts.rejected, (state, action) => {
        state.isAlertsLoading = false;
        state.lastUpdate = new Date().toISOString();
      });

    // Trigger market scan
    builder.addCase(triggerMarketScan.fulfilled, (state, action) => {
      state.lastUpdate = new Date().toISOString();
    });

    // Trigger position monitor
    builder.addCase(triggerPositionMonitor.fulfilled, (state, action) => {
      state.lastUpdate = new Date().toISOString();
    });

    // Trigger model retrain
    builder.addCase(triggerModelRetrain.fulfilled, (state, action) => {
      state.lastUpdate = new Date().toISOString();
    });

    // Run health check
    builder.addCase(runHealthCheck.fulfilled, (state, action) => {
      state.lastUpdate = new Date().toISOString();
    });

    // Trigger emergency stop
    builder.addCase(triggerEmergencyStop.fulfilled, (state, action) => {
      state.lastUpdate = new Date().toISOString();
    });

    // Acknowledge alert
    builder.addCase(acknowledgeAlert.fulfilled, (state, action) => {
      const alertId = action.meta.arg;
      state.alerts = state.alerts.map(alert =>
        alert.id === alertId ? { ...alert, acknowledged: true } : alert
      );
      state.unacknowledgedCount = Math.max(0, state.unacknowledgedCount - 1);
      state.lastUpdate = new Date().toISOString();
    });

    // Update config
    builder
      .addCase(updateConfig.pending, state => {
        state.isConfigLoading = true;
      })
      .addCase(updateConfig.fulfilled, (state, action) => {
        state.config = action.payload;
        state.isConfigLoading = false;
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(updateConfig.rejected, (state, action) => {
        state.isConfigLoading = false;
        state.lastUpdate = new Date().toISOString();
      });
  },
});

// Export actions
export const { updateLastUpdate, setConnected } = automationSlice.actions;

// Export selectors
export const selectAutomation = (state: { automation: AutomationState }) =>
  state.automation;
export const selectConfig = (state: { automation: AutomationState }) =>
  state.automation.config;
export const selectSystemStatus = (state: { automation: AutomationState }) =>
  state.automation.systemStatus;
export const selectActiveTasks = (state: { automation: AutomationState }) =>
  state.automation.activeTasks;
export const selectTaskHistory = (state: { automation: AutomationState }) =>
  state.automation.taskHistory;
export const selectAlerts = (state: { automation: AutomationState }) =>
  state.automation.alerts;
export const selectUnacknowledgedCount = (state: {
  automation: AutomationState;
}) => state.automation.unacknowledgedCount;
export const selectPerformance = (state: { automation: AutomationState }) =>
  state.automation.performance;
export const selectPerformanceHistory = (state: {
  automation: AutomationState;
}) => state.automation.performanceHistory;
export const selectQueueStats = (state: { automation: AutomationState }) =>
  state.automation.queueStats;
export const selectIsConnected = (state: { automation: AutomationState }) =>
  state.automation.isConnected;
export const selectLastUpdate = (state: { automation: AutomationState }) =>
  state.automation.lastUpdate;

// Helper selectors
export const selectIsLoading = (state: { automation: AutomationState }) =>
  state.automation.isConfigLoading ||
  state.automation.isStatusLoading ||
  state.automation.isTasksLoading ||
  state.automation.isAlertsLoading ||
  state.automation.isPerformanceLoading;

export const selectHasError = (state: { automation: AutomationState }) =>
  state.automation.alerts.some(alert => !alert.acknowledged);

export const selectIsAutoTradingEnabled = (state: {
  automation: AutomationState;
}) => state.automation.config?.auto_trading_enabled ?? false;

// Export reducer
export default automationSlice.reducer;
