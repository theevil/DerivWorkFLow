/**
 * Zustand store for automation system state management
 */

import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { api } from '../lib/api';
import type {
  AutomationState,
  SystemStatus,
  AutoTradingConfig,
  AutomationSettings,
  Alert,
  AutomationPerformance,
  PerformanceChartData,
  EmergencyStopRequest,
  TaskStatus,
  ActiveTask,
} from '../types/automation';

interface AutomationActions {
  // Configuration actions
  loadConfig: () => Promise<void>;
  updateConfig: (config: AutoTradingConfig) => Promise<void>;
  
  // System status actions
  loadSystemStatus: () => Promise<void>;
  refreshSystemStatus: () => Promise<void>;
  
  // Task management actions
  loadActiveTasks: () => Promise<void>;
  triggerMarketScan: () => Promise<string>;
  triggerPositionMonitor: () => Promise<string>;
  triggerModelRetrain: () => Promise<string>;
  getTaskStatus: (taskId: string) => Promise<TaskStatus>;
  
  // Alert actions
  loadAlerts: () => Promise<void>;
  acknowledgeAlert: (alertId: string) => Promise<void>;
  
  // Performance actions
  loadPerformance: (days?: number) => Promise<void>;
  
  // Emergency actions
  triggerEmergencyStop: (request: EmergencyStopRequest) => Promise<void>;
  
  // Health check
  runHealthCheck: () => Promise<void>;
  
  // Real-time updates
  setConnected: (connected: boolean) => void;
  updateLastUpdate: () => void;
  
  // Reset actions
  reset: () => void;
}

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

export const useAutomationStore = create<AutomationState & AutomationActions>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      ...initialState,

      // Configuration actions
      loadConfig: async () => {
        set({ isConfigLoading: true });
        try {
          const response = await api.getAutoTradingConfig();
          set({
            config: {
              auto_trading_enabled: response.enabled,
              config: response.config,
              last_updated: response.last_updated,
            },
            isConfigLoading: false,
          });
        } catch (error) {
          console.error('Failed to load automation config:', error);
          set({ isConfigLoading: false });
          throw error;
        }
      },

      updateConfig: async (config: AutoTradingConfig) => {
        set({ isConfigLoading: true });
        try {
          await api.configureAutoTrading(config);
          
          // Reload config to get updated values
          await get().loadConfig();
          
          // Refresh system status to reflect changes
          await get().refreshSystemStatus();
        } catch (error) {
          console.error('Failed to update automation config:', error);
          set({ isConfigLoading: false });
          throw error;
        }
      },

      // System status actions
      loadSystemStatus: async () => {
        set({ isStatusLoading: true });
        try {
          const status = await api.getAutomationStatus();
          set({
            systemStatus: status,
            isStatusLoading: false,
            lastStatusUpdate: new Date().toISOString(),
          });
        } catch (error) {
          console.error('Failed to load system status:', error);
          set({ isStatusLoading: false });
          throw error;
        }
      },

      refreshSystemStatus: async () => {
        // Refresh without loading state for background updates
        try {
          const status = await api.getAutomationStatus();
          set({
            systemStatus: status,
            lastStatusUpdate: new Date().toISOString(),
          });
        } catch (error) {
          console.error('Failed to refresh system status:', error);
        }
      },

      // Task management actions
      loadActiveTasks: async () => {
        set({ isTasksLoading: true });
        try {
          const response = await api.getActiveTasks();
          set({
            activeTasks: response.active_tasks,
            isTasksLoading: false,
          });
        } catch (error) {
          console.error('Failed to load active tasks:', error);
          set({ isTasksLoading: false });
          throw error;
        }
      },

      triggerMarketScan: async () => {
        try {
          const response = await api.triggerMarketScan();
          
          // Add to task history
          const newTask: TaskStatus = {
            task_id: response.task_id,
            status: 'STARTED',
            timestamp: new Date().toISOString(),
          };
          
          set(state => ({
            taskHistory: [newTask, ...state.taskHistory.slice(0, 49)], // Keep last 50
          }));
          
          return response.task_id;
        } catch (error) {
          console.error('Failed to trigger market scan:', error);
          throw error;
        }
      },

      triggerPositionMonitor: async () => {
        try {
          const response = await api.triggerPositionMonitor();
          
          const newTask: TaskStatus = {
            task_id: response.task_id,
            status: 'STARTED',
            timestamp: new Date().toISOString(),
          };
          
          set(state => ({
            taskHistory: [newTask, ...state.taskHistory.slice(0, 49)],
          }));
          
          return response.task_id;
        } catch (error) {
          console.error('Failed to trigger position monitor:', error);
          throw error;
        }
      },

      triggerModelRetrain: async () => {
        try {
          const response = await api.triggerModelRetrain();
          
          const newTask: TaskStatus = {
            task_id: response.task_id,
            status: 'STARTED',
            timestamp: new Date().toISOString(),
          };
          
          set(state => ({
            taskHistory: [newTask, ...state.taskHistory.slice(0, 49)],
          }));
          
          return response.task_id;
        } catch (error) {
          console.error('Failed to trigger model retrain:', error);
          throw error;
        }
      },

      getTaskStatus: async (taskId: string) => {
        try {
          const taskStatus = await api.getTaskStatus(taskId);
          
          // Update task in history
          set(state => ({
            taskHistory: state.taskHistory.map(task =>
              task.task_id === taskId ? taskStatus : task
            ),
          }));
          
          return taskStatus;
        } catch (error) {
          console.error('Failed to get task status:', error);
          throw error;
        }
      },

      // Alert actions
      loadAlerts: async () => {
        set({ isAlertsLoading: true });
        try {
          const response = await api.getUserAlerts();
          set({
            alerts: response.alerts,
            unacknowledgedCount: response.unacknowledged_count,
            isAlertsLoading: false,
          });
        } catch (error) {
          console.error('Failed to load alerts:', error);
          set({ isAlertsLoading: false });
          throw error;
        }
      },

      acknowledgeAlert: async (alertId: string) => {
        try {
          await api.acknowledgeAlert(alertId);
          
          // Update local state
          set(state => ({
            alerts: state.alerts.map(alert =>
              alert.id === alertId ? { ...alert, acknowledged: true } : alert
            ),
            unacknowledgedCount: Math.max(0, state.unacknowledgedCount - 1),
          }));
        } catch (error) {
          console.error('Failed to acknowledge alert:', error);
          throw error;
        }
      },

      // Performance actions
      loadPerformance: async (days = 7) => {
        set({ isPerformanceLoading: true });
        try {
          const performance = await api.getAutomationPerformance(days);
          
          // Generate chart data from performance stats
          const chartData: PerformanceChartData[] = [];
          const endDate = new Date();
          
          for (let i = days - 1; i >= 0; i--) {
            const date = new Date(endDate);
            date.setDate(date.getDate() - i);
            
            // In a real implementation, this would come from detailed daily data
            // For now, we'll simulate it based on the overall performance
            chartData.push({
              date: date.toISOString().split('T')[0],
              profit: performance.trading_stats.total_profit / days + (Math.random() - 0.5) * 20,
              trades: Math.round(performance.trading_stats.total_trades / days + Math.random() * 3),
              win_rate: performance.trading_stats.win_rate + (Math.random() - 0.5) * 0.2,
            });
          }
          
          set({
            performance,
            performanceHistory: chartData,
            isPerformanceLoading: false,
          });
        } catch (error) {
          console.error('Failed to load performance:', error);
          set({ isPerformanceLoading: false });
          throw error;
        }
      },

      // Emergency actions
      triggerEmergencyStop: async (request: EmergencyStopRequest) => {
        try {
          const response = await api.triggerEmergencyStop(request);
          
          // Add to task history
          const newTask: TaskStatus = {
            task_id: response.task_id,
            status: 'STARTED',
            timestamp: new Date().toISOString(),
          };
          
          set(state => ({
            taskHistory: [newTask, ...state.taskHistory.slice(0, 49)],
          }));
          
          // Refresh system status
          await get().refreshSystemStatus();
          
          // Reload alerts to see the emergency alert
          await get().loadAlerts();
        } catch (error) {
          console.error('Failed to trigger emergency stop:', error);
          throw error;
        }
      },

      // Health check
      runHealthCheck: async () => {
        try {
          const response = await api.runHealthCheck();
          
          // Update system status based on health check
          set(state => ({
            systemStatus: state.systemStatus ? {
              ...state.systemStatus,
              redis_connected: response.system_status === 'healthy',
            } : null,
            lastStatusUpdate: new Date().toISOString(),
          }));
        } catch (error) {
          console.error('Failed to run health check:', error);
          throw error;
        }
      },

      // Real-time updates
      setConnected: (connected: boolean) => {
        set({ isConnected: connected });
      },

      updateLastUpdate: () => {
        set({ lastUpdate: new Date().toISOString() });
      },

      // Reset actions
      reset: () => {
        set(initialState);
      },
    })),
    {
      name: 'automation-store',
    }
  )
);

// Utility functions for working with the store
export const automationActions = {
  // Auto-refresh system status every 30 seconds
  startAutoRefresh: () => {
    const store = useAutomationStore.getState();
    
    const interval = setInterval(() => {
      store.refreshSystemStatus();
    }, 30000);
    
    return () => clearInterval(interval);
  },
  
  // Check for alerts periodically
  startAlertPolling: () => {
    const store = useAutomationStore.getState();
    
    const interval = setInterval(() => {
      store.loadAlerts();
    }, 60000); // Check every minute
    
    return () => clearInterval(interval);
  },
  
  // Initialize automation store
  initialize: async () => {
    const store = useAutomationStore.getState();
    
    try {
      // Load initial data in parallel
      await Promise.all([
        store.loadConfig(),
        store.loadSystemStatus(),
        store.loadAlerts(),
        store.loadPerformance(),
      ]);
      
      // Start auto-refresh
      automationActions.startAutoRefresh();
      automationActions.startAlertPolling();
    } catch (error) {
      console.error('Failed to initialize automation store:', error);
    }
  },
};

// Selectors for computed values
export const automationSelectors = {
  isSystemHealthy: (state: AutomationState) => {
    if (!state.systemStatus) return false;
    
    return (
      state.systemStatus.redis_connected &&
      state.systemStatus.market_monitor.active &&
      state.systemStatus.trading_executor.redis_connected
    );
  },
  
  isAutoTradingEnabled: (state: AutomationState) => {
    return state.config?.auto_trading_enabled ?? false;
  },
  
  hasUnacknowledgedAlerts: (state: AutomationState) => {
    return state.unacknowledgedCount > 0;
  },
  
  getActiveTaskCount: (state: AutomationState) => {
    return Object.values(state.activeTasks).reduce(
      (total, tasks) => total + tasks.length,
      0
    );
  },
  
  getRecentTasksCount: (state: AutomationState) => {
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
    return state.taskHistory.filter(
      task => new Date(task.timestamp) > oneHourAgo
    ).length;
  },
  
  isLoading: (state: AutomationState) => {
    return (
      state.isConfigLoading ||
      state.isStatusLoading ||
      state.isTasksLoading ||
      state.isAlertsLoading ||
      state.isPerformanceLoading
    );
  },
};
