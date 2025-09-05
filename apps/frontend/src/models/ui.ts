// UI Models

export interface UIState {
  // Sidebar state
  sidebar: {
    isOpen: boolean;
    isCollapsed: boolean;
    activeSection: string | null;
  };

  // Modal states
  modals: {
    tradingModal: boolean;
    settingsModal: boolean;
    automationModal: boolean;
    confirmModal: boolean;
    errorModal: boolean;
  };

  // Theme and appearance
  theme: {
    mode: 'light' | 'dark' | 'auto';
    primaryColor: string;
    accentColor: string;
    fontSize: 'small' | 'medium' | 'large';
    compactMode: boolean;
  };

  // Notifications
  notifications: {
    enabled: boolean;
    position: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
    duration: number;
    maxVisible: number;
  };

  // Layout preferences
  layout: {
    gridColumns: number;
    showSidebar: boolean;
    showHeader: boolean;
    showFooter: boolean;
    sidebarWidth: number;
    headerHeight: number;
  };

  // Performance settings
  performance: {
    enableAnimations: boolean;
    enableTransitions: boolean;
    enableHoverEffects: boolean;
    reduceMotion: boolean;
    lowPowerMode: boolean;
  };

  // Error handling
  errors: {
    showErrorBoundary: boolean;
    showErrorDetails: boolean;
    autoHideErrors: boolean;
    errorHideDelay: number;
  };

  // Loading states
  loading: {
    globalLoading: boolean;
    pageLoading: boolean;
    componentLoading: Record<string, boolean>;
  };

  // Toast messages
  toasts: Array<{
    id: string;
    type: 'success' | 'error' | 'warning' | 'info';
    title: string;
    message: string;
    duration: number;
    timestamp: string;
    isVisible: boolean;
  }>;

  // Last update
  lastUpdate: string | null;
}
