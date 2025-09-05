// Settings Models

export interface TradingSettings {
  defaultLeverage: number;
  defaultPositionSize: number;
  enableStopLoss: boolean;
  enableTakeProfit: boolean;
  defaultStopLoss: number;
  defaultTakeProfit: number;
  maxOpenPositions: number;
  allowHedging: boolean;
  confirmTrades: boolean;
  autoClosePositions: boolean;
}

export interface NotificationSettings {
  email: {
    enabled: boolean;
    address: string;
    tradeConfirmations: boolean;
    dailyReports: boolean;
    alerts: boolean;
    marketing: boolean;
  };
  push: {
    enabled: boolean;
    tradeConfirmations: boolean;
    priceAlerts: boolean;
    newsUpdates: boolean;
    systemMaintenance: boolean;
  };
  inApp: {
    enabled: boolean;
    sound: boolean;
    toastDuration: number;
    maxVisible: number;
  };
}

export interface SecuritySettings {
  twoFactorAuth: boolean;
  sessionTimeout: number;
  maxLoginAttempts: number;
  lockoutDuration: number;
  requirePasswordChange: boolean;
  passwordExpiryDays: number;
  ipWhitelist: string[];
  deviceWhitelist: string[];
}

export interface PerformanceSettings {
  enableCaching: boolean;
  cacheExpiry: number;
  enableCompression: boolean;
  enableMinification: boolean;
  lazyLoading: boolean;
  virtualScrolling: boolean;
  debounceDelay: number;
  throttleDelay: number;
}

export interface AppearanceSettings {
  theme: 'light' | 'dark' | 'auto';
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  fontSize: 'small' | 'medium' | 'large';
  fontFamily: string;
  borderRadius: 'none' | 'small' | 'medium' | 'large';
  shadows: 'none' | 'small' | 'medium' | 'large';
  animations: 'none' | 'reduced' | 'normal';
  compactMode: boolean;
}

export interface APISettings {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
  enableCaching: boolean;
  cacheExpiry: number;
  rateLimit: {
    enabled: boolean;
    maxRequests: number;
    windowMs: number;
  };
}

export interface SettingsState {
  trading: TradingSettings;
  notifications: NotificationSettings;
  security: SecuritySettings;
  performance: PerformanceSettings;
  appearance: AppearanceSettings;
  api: APISettings;
  lastUpdate: string | null;
  isDirty: boolean;
  error: string | null;
}

export interface UpdateSettingsRequest {
  trading?: Partial<TradingSettings>;
  notifications?: Partial<NotificationSettings>;
  security?: Partial<SecuritySettings>;
  performance?: Partial<PerformanceSettings>;
  appearance?: Partial<AppearanceSettings>;
  api?: Partial<APISettings>;
}
