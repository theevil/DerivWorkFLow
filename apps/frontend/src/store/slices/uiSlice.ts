import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { UIState } from '../../models';

// Initial state
const initialState: UIState = {
  sidebar: {
    isOpen: true,
    isCollapsed: false,
    activeSection: null,
  },

  modals: {
    tradingModal: false,
    settingsModal: false,
    automationModal: false,
    confirmModal: false,
    errorModal: false,
  },

  theme: {
    mode: 'auto',
    primaryColor: '#3b82f6',
    accentColor: '#10b981',
    fontSize: 'medium',
    compactMode: false,
  },

  notifications: {
    enabled: true,
    position: 'top-right',
    duration: 5000,
    maxVisible: 5,
  },

  layout: {
    gridColumns: 3,
    showSidebar: true,
    showHeader: true,
    showFooter: true,
    sidebarWidth: 280,
    headerHeight: 64,
  },

  performance: {
    enableAnimations: true,
    enableTransitions: true,
    enableHoverEffects: true,
    reduceMotion: false,
    lowPowerMode: false,
  },

  errors: {
    showErrorBoundary: true,
    showErrorDetails: false,
    autoHideErrors: true,
    errorHideDelay: 5000,
  },

  loading: {
    globalLoading: false,
    pageLoading: false,
    componentLoading: {},
  },

  toasts: [],

  lastUpdate: null,
};

// UI slice
const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Sidebar actions
    toggleSidebar: state => {
      state.sidebar.isOpen = !state.sidebar.isOpen;
      state.lastUpdate = new Date().toISOString();
    },

    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebar.isOpen = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    toggleSidebarCollapsed: state => {
      state.sidebar.isCollapsed = !state.sidebar.isCollapsed;
      state.lastUpdate = new Date().toISOString();
    },

    setSidebarCollapsed: (state, action: PayloadAction<boolean>) => {
      state.sidebar.isCollapsed = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setActiveSection: (state, action: PayloadAction<string | null>) => {
      state.sidebar.activeSection = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    // Modal actions
    openModal: (state, action: PayloadAction<keyof UIState['modals']>) => {
      state.modals[action.payload] = true;
      state.lastUpdate = new Date().toISOString();
    },

    closeModal: (state, action: PayloadAction<keyof UIState['modals']>) => {
      state.modals[action.payload] = false;
      state.lastUpdate = new Date().toISOString();
    },

    closeAllModals: state => {
      Object.keys(state.modals).forEach(key => {
        state.modals[key as keyof UIState['modals']] = false;
      });
      state.lastUpdate = new Date().toISOString();
    },

    // Theme actions
    setThemeMode: (state, action: PayloadAction<'light' | 'dark' | 'auto'>) => {
      state.theme.mode = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setPrimaryColor: (state, action: PayloadAction<string>) => {
      state.theme.primaryColor = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setAccentColor: (state, action: PayloadAction<string>) => {
      state.theme.accentColor = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setFontSize: (
      state,
      action: PayloadAction<'small' | 'medium' | 'large'>
    ) => {
      state.theme.fontSize = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    toggleCompactMode: state => {
      state.theme.compactMode = !state.theme.compactMode;
      state.lastUpdate = new Date().toISOString();
    },

    // Notification actions
    setNotificationsEnabled: (state, action: PayloadAction<boolean>) => {
      state.notifications.enabled = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setNotificationPosition: (
      state,
      action: PayloadAction<
        'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
      >
    ) => {
      state.notifications.position = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setNotificationDuration: (state, action: PayloadAction<number>) => {
      state.notifications.duration = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setMaxVisibleNotifications: (state, action: PayloadAction<number>) => {
      state.notifications.maxVisible = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    // Layout actions
    setGridColumns: (state, action: PayloadAction<number>) => {
      state.layout.gridColumns = Math.max(1, Math.min(6, action.payload));
      state.lastUpdate = new Date().toISOString();
    },

    toggleSidebarVisibility: state => {
      state.layout.showSidebar = !state.layout.showSidebar;
      state.lastUpdate = new Date().toISOString();
    },

    toggleHeaderVisibility: state => {
      state.layout.showHeader = !state.layout.showHeader;
      state.lastUpdate = new Date().toISOString();
    },

    toggleFooterVisibility: state => {
      state.layout.showFooter = !state.layout.showFooter;
      state.lastUpdate = new Date().toISOString();
    },

    setSidebarWidth: (state, action: PayloadAction<number>) => {
      state.layout.sidebarWidth = Math.max(200, Math.min(400, action.payload));
      state.lastUpdate = new Date().toISOString();
    },

    setHeaderHeight: (state, action: PayloadAction<number>) => {
      state.layout.headerHeight = Math.max(48, Math.min(80, action.payload));
      state.lastUpdate = new Date().toISOString();
    },

    // Performance actions
    setAnimationsEnabled: (state, action: PayloadAction<boolean>) => {
      state.performance.enableAnimations = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setTransitionsEnabled: (state, action: PayloadAction<boolean>) => {
      state.performance.enableTransitions = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setHoverEffectsEnabled: (state, action: PayloadAction<boolean>) => {
      state.performance.enableHoverEffects = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setReduceMotion: (state, action: PayloadAction<boolean>) => {
      state.performance.reduceMotion = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setLowPowerMode: (state, action: PayloadAction<boolean>) => {
      state.performance.lowPowerMode = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    // Error handling actions
    setShowErrorBoundary: (state, action: PayloadAction<boolean>) => {
      state.errors.showErrorBoundary = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setShowErrorDetails: (state, action: PayloadAction<boolean>) => {
      state.errors.showErrorDetails = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setAutoHideErrors: (state, action: PayloadAction<boolean>) => {
      state.errors.autoHideErrors = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setErrorHideDelay: (state, action: PayloadAction<number>) => {
      state.errors.errorHideDelay = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    // Loading actions
    setGlobalLoading: (state, action: PayloadAction<boolean>) => {
      state.loading.globalLoading = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setPageLoading: (state, action: PayloadAction<boolean>) => {
      state.loading.pageLoading = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    setComponentLoading: (
      state,
      action: PayloadAction<{ componentId: string; loading: boolean }>
    ) => {
      const { componentId, loading } = action.payload;
      state.loading.componentLoading[componentId] = loading;
      state.lastUpdate = new Date().toISOString();
    },

    clearComponentLoading: (state, action: PayloadAction<string>) => {
      delete state.loading.componentLoading[action.payload];
      state.lastUpdate = new Date().toISOString();
    },

    // Toast actions
    addToast: (
      state,
      action: PayloadAction<
        Omit<UIState['toasts'][0], 'id' | 'timestamp' | 'isVisible'>
      >
    ) => {
      const toast = {
        ...action.payload,
        id: `toast_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        timestamp: new Date().toISOString(),
        isVisible: true,
      };

      state.toasts.push(toast);

      // Keep only maxVisible toasts
      if (state.toasts.length > state.notifications.maxVisible) {
        state.toasts = state.toasts.slice(-state.notifications.maxVisible);
      }

      state.lastUpdate = new Date().toISOString();
    },

    removeToast: (state, action: PayloadAction<string>) => {
      state.toasts = state.toasts.filter(toast => toast.id !== action.payload);
      state.lastUpdate = new Date().toISOString();
    },

    hideToast: (state, action: PayloadAction<string>) => {
      const toast = state.toasts.find(t => t.id === action.payload);
      if (toast) {
        toast.isVisible = false;
        state.lastUpdate = new Date().toISOString();
      }
    },

    clearToasts: state => {
      state.toasts = [];
      state.lastUpdate = new Date().toISOString();
    },

    // Reset actions
    resetUI: state => {
      state.sidebar = initialState.sidebar;
      state.modals = initialState.modals;
      state.theme = initialState.theme;
      state.notifications = initialState.notifications;
      state.layout = initialState.layout;
      state.performance = initialState.performance;
      state.errors = initialState.errors;
      state.loading = initialState.loading;
      state.toasts = [];
      state.lastUpdate = new Date().toISOString();
    },

    // Update last update
    updateLastUpdate: state => {
      state.lastUpdate = new Date().toISOString();
    },
  },
});

// Export actions
export const {
  // Sidebar
  toggleSidebar,
  setSidebarOpen,
  toggleSidebarCollapsed,
  setSidebarCollapsed,
  setActiveSection,

  // Modals
  openModal,
  closeModal,
  closeAllModals,

  // Theme
  setThemeMode,
  setPrimaryColor,
  setAccentColor,
  setFontSize,
  toggleCompactMode,

  // Notifications
  setNotificationsEnabled,
  setNotificationPosition,
  setNotificationDuration,
  setMaxVisibleNotifications,

  // Layout
  setGridColumns,
  toggleSidebarVisibility,
  toggleHeaderVisibility,
  toggleFooterVisibility,
  setSidebarWidth,
  setHeaderHeight,

  // Performance
  setAnimationsEnabled,
  setTransitionsEnabled,
  setHoverEffectsEnabled,
  setReduceMotion,
  setLowPowerMode,

  // Error handling
  setShowErrorBoundary,
  setShowErrorDetails,
  setAutoHideErrors,
  setErrorHideDelay,

  // Loading
  setGlobalLoading,
  setPageLoading,
  setComponentLoading,
  clearComponentLoading,

  // Toasts
  addToast,
  removeToast,
  hideToast,
  clearToasts,

  // Reset
  resetUI,
  updateLastUpdate,
} = uiSlice.actions;

// Export selectors
export const selectUI = (state: { ui: UIState }) => state.ui;
export const selectSidebar = (state: { ui: UIState }) => state.ui.sidebar;
export const selectModals = (state: { ui: UIState }) => state.ui.modals;
export const selectTheme = (state: { ui: UIState }) => state.ui.theme;
export const selectNotifications = (state: { ui: UIState }) =>
  state.ui.notifications;
export const selectLayout = (state: { ui: UIState }) => state.ui.layout;
export const selectPerformance = (state: { ui: UIState }) =>
  state.ui.performance;
export const selectErrors = (state: { ui: UIState }) => state.ui.errors;
export const selectLoading = (state: { ui: UIState }) => state.ui.loading;
export const selectToasts = (state: { ui: UIState }) => state.ui.toasts;
export const selectLastUpdate = (state: { ui: UIState }) => state.ui.lastUpdate;

// Helper selectors
export const selectIsSidebarOpen = (state: { ui: UIState }) =>
  state.ui.sidebar.isOpen;
export const selectIsSidebarCollapsed = (state: { ui: UIState }) =>
  state.ui.sidebar.isCollapsed;
export const selectActiveSection = (state: { ui: UIState }) =>
  state.ui.sidebar.activeSection;
export const selectIsModalOpen = (
  state: { ui: UIState },
  modalName: keyof UIState['modals']
) => state.ui.modals[modalName];
export const selectThemeMode = (state: { ui: UIState }) => state.ui.theme.mode;
export const selectIsDarkMode = (state: { ui: UIState }) =>
  state.ui.theme.mode === 'dark' ||
  (state.ui.theme.mode === 'auto' &&
    window.matchMedia('(prefers-color-scheme: dark)').matches);
export const selectIsGlobalLoading = (state: { ui: UIState }) =>
  state.ui.loading.globalLoading;
export const selectIsPageLoading = (state: { ui: UIState }) =>
  state.ui.loading.pageLoading;
export const selectIsComponentLoading = (
  state: { ui: UIState },
  componentId: string
) => state.ui.loading.componentLoading[componentId] || false;
export const selectVisibleToasts = (state: { ui: UIState }) =>
  state.ui.toasts.filter(toast => toast.isVisible);

// Export reducer
export default uiSlice.reducer;
