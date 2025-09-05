import { configureStore, combineReducers } from '@reduxjs/toolkit';
import {
  persistStore,
  persistReducer,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
} from 'redux-persist';
import storage from 'redux-persist/lib/storage';
import { setupListeners } from '@reduxjs/toolkit/query';

// Import reducers
import authReducer from './slices/authSlice';
import tradingReducer from './slices/tradingSlice';
import websocketReducer from './slices/websocketSlice';
import uiReducer from './slices/uiSlice';
import automationReducer from './slices/automationSlice';
import settingsReducer from './slices/settingsSlice';

// Combine reducers
const rootReducer = combineReducers({
  auth: authReducer,
  trading: tradingReducer,
  websocket: websocketReducer,
  ui: uiReducer,
  automation: automationReducer,
  settings: settingsReducer,
});

// Persist configuration
const persistConfig = {
  key: 'root',
  storage,
  whitelist: ['auth', 'ui', 'settings'], // Only persist these reducers
  blacklist: ['trading', 'websocket', 'automation'], // Don't persist these
};

// Create persisted reducer
const persistedReducer = persistReducer(persistConfig, rootReducer);

// Configure store
export const store = configureStore({
  reducer: persistedReducer,
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
        ignoredPaths: ['websocket.connections', 'websocket.messages'],
      },
      immutableCheck: {
        ignoredPaths: ['websocket.connections', 'websocket.messages'],
      },
    }).concat([]),
  devTools: false,
});

// Setup listeners for RTK Query
setupListeners(store.dispatch);

// Export types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Export persistor
export const persistor = persistStore(store);

// Export store as default
export default store;

// Explicit exports for actions and selectors with aliasing to prevent conflicts
export {
  // Auth
  loginUser,
  registerUser,
  logoutUser,
  refreshUserToken,
  getCurrentUser,
  initializeAuth,
  selectAuth,
  selectUser,
  selectIsAuthenticated,
  selectIsLoading as selectAuthIsLoading,
  selectError as selectAuthError,
  selectToken,
  selectTokenExpiry,
} from './slices/authSlice';

export {
  // Trading
  fetchPositions,
  fetchOrders,
  fetchMarketData,
  fetchPortfolio,
  openPosition,
  closePosition,
  placeOrder,
  cancelOrder,
  selectTrading,
  selectPositions,
  selectOrders,
  selectMarketData,
  selectPortfolio,
  selectIsLoading as selectTradingIsLoading,
  selectError as selectTradingError,
  selectSelectedSymbol,
  selectTradingEnabled,
} from './slices/tradingSlice';

export {
  // Automation
  loadConfig,
  loadSystemStatus,
  loadAlerts,
  triggerMarketScan,
  triggerPositionMonitor,
  triggerModelRetrain,
  runHealthCheck,
  triggerEmergencyStop,
  acknowledgeAlert,
  updateConfig,
  setConnected,
  updateLastUpdate,
  selectAutomation,
  selectConfig,
  selectSystemStatus,
  selectActiveTasks,
  selectTaskHistory,
  selectAlerts,
  selectUnacknowledgedCount,
  selectPerformance as selectAutomationPerformance,
  selectPerformanceHistory,
  selectQueueStats,
  selectIsConnected,
  selectLastUpdate as selectAutomationLastUpdate,
  selectIsLoading as selectAutomationIsLoading,
  selectHasError as selectAutomationHasError,
  selectIsAutoTradingEnabled,
} from './slices/automationSlice';

export {
  // WebSocket
  createConnection,
  closeConnection,
  sendMessage,
  selectWebSocket,
  selectConnections,
  selectMessages,
  selectGlobalStatus,
  selectIsEnabled,
  selectAutoReconnect,
  selectReconnectInterval,
  selectMaxReconnectAttempts,
  selectError as selectWebSocketError,
  selectLastGlobalUpdate,
} from './slices/websocketSlice';

export {
  // Settings
  fetchSettings,
  updateSettings,
  resetSettings,
  exportSettings,
  importSettings,
  selectSettings,
  selectTradingSettings,
  selectNotificationSettings,
  selectSecuritySettings,
  selectPerformanceSettings,
  selectAppearanceSettings,
  selectAPISettings,
  selectError as selectSettingsError,
  selectLastUpdate as selectSettingsLastUpdate,
  selectIsDirty,
  selectHasChanges,
  selectIsDarkMode,
  selectIsCompactMode,
  selectIsTwoFactorEnabled,
  selectIsCachingEnabled,
  selectIsEmailEnabled,
  selectIsPushEnabled,
  selectIsInAppEnabled,
} from './slices/settingsSlice';

export {
  // UI
  toggleSidebar,
  setSidebarOpen,
  toggleSidebarCollapsed,
  setSidebarCollapsed,
  setActiveSection,
  openModal,
  closeModal,
  closeAllModals,
  setThemeMode,
  setPrimaryColor,
  setAccentColor,
  setFontSize,
  toggleCompactMode,
  setNotificationsEnabled,
  setNotificationPosition,
  setNotificationDuration,
  setMaxVisibleNotifications,
  setGridColumns,
  toggleSidebarVisibility,
  toggleHeaderVisibility,
  toggleFooterVisibility,
  setSidebarWidth,
  setHeaderHeight,
  setAnimationsEnabled,
  setTransitionsEnabled,
  setHoverEffectsEnabled,
  setReduceMotion,
  setLowPowerMode,
  setShowErrorBoundary,
  setShowErrorDetails,
  setAutoHideErrors,
  setErrorHideDelay,
  setGlobalLoading,
  setPageLoading,
  setComponentLoading,
  clearComponentLoading,
  addToast,
  removeToast,
  hideToast,
  clearToasts,
  resetUI,
  selectUI,
  selectSidebar,
  selectModals,
  selectTheme,
  selectNotifications,
  selectLayout,
  selectPerformance,
  selectErrors,
  selectLoading,
  selectToasts,
  selectLastUpdate as selectUILastUpdate,
  selectIsSidebarOpen,
  selectIsSidebarCollapsed,
  selectActiveSection,
  selectIsModalOpen,
  selectThemeMode,
  selectIsDarkMode as selectUIIsDarkMode,
  selectIsGlobalLoading,
  selectIsPageLoading,
  selectIsComponentLoading,
  selectVisibleToasts,
} from './slices/uiSlice';
