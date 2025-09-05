import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { http } from '../../lib/http-client';
import {
  TradingSettings,
  NotificationSettings,
  SecuritySettings,
  PerformanceSettings,
  AppearanceSettings,
  APISettings,
  SettingsState,
  UpdateSettingsRequest,
} from '../../models';

// Initial state
const initialState: SettingsState = {
  trading: {
    defaultLeverage: 1,
    defaultPositionSize: 0.01,
    enableStopLoss: true,
    enableTakeProfit: true,
    defaultStopLoss: 0.02,
    defaultTakeProfit: 0.04,
    maxOpenPositions: 5,
    allowHedging: false,
    confirmTrades: true,
    autoClosePositions: false,
  },

  notifications: {
    email: {
      enabled: true,
      address: '',
      tradeConfirmations: true,
      dailyReports: true,
      alerts: true,
      marketing: false,
    },
    push: {
      enabled: true,
      tradeConfirmations: true,
      priceAlerts: true,
      newsUpdates: false,
      systemMaintenance: true,
    },
    inApp: {
      enabled: true,
      sound: true,
      toastDuration: 5000,
      maxVisible: 5,
    },
  },

  security: {
    twoFactorAuth: false,
    sessionTimeout: 3600,
    maxLoginAttempts: 5,
    lockoutDuration: 900,
    requirePasswordChange: false,
    passwordExpiryDays: 90,
    ipWhitelist: [],
    deviceWhitelist: [],
  },

  performance: {
    enableCaching: true,
    cacheExpiry: 300,
    enableCompression: true,
    enableMinification: true,
    lazyLoading: true,
    virtualScrolling: false,
    debounceDelay: 300,
    throttleDelay: 100,
  },

  appearance: {
    theme: 'auto',
    primaryColor: '#3b82f6',
    secondaryColor: '#10b981',
    accentColor: '#f59e0b',
    fontSize: 'medium',
    fontFamily: 'Inter',
    borderRadius: 'medium',
    shadows: 'medium',
    animations: 'normal',
    compactMode: false,
  },

  api: {
    baseUrl: 'http://localhost:8000',
    timeout: 30000,
    retryAttempts: 3,
    retryDelay: 1000,
    enableCaching: true,
    cacheExpiry: 300,
    rateLimit: {
      enabled: true,
      maxRequests: 100,
      windowMs: 60000,
    },
  },

  lastUpdate: null,
  isDirty: false,
  error: null,
};

// Async thunks
export const fetchSettings = createAsyncThunk(
  'settings/fetchSettings',
  async (_, { rejectWithValue }) => {
    try {
      const response = await http.get('/settings');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to fetch settings'
      );
    }
  }
);

export const updateSettings = createAsyncThunk(
  'settings/updateSettings',
  async (settingsData: UpdateSettingsRequest, { rejectWithValue }) => {
    try {
      const response = await http.put('/settings', settingsData);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to update settings'
      );
    }
  }
);

export const resetSettings = createAsyncThunk(
  'settings/resetSettings',
  async (_, { rejectWithValue }) => {
    try {
      const response = await http.post('/settings/reset');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to reset settings'
      );
    }
  }
);

export const exportSettings = createAsyncThunk(
  'settings/exportSettings',
  async (_, { rejectWithValue }) => {
    try {
      const response = await http.get('/settings/export');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to export settings'
      );
    }
  }
);

export const importSettings = createAsyncThunk(
  'settings/importSettings',
  async (settingsFile: File, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      formData.append('settings', settingsFile);

      const response = await http.post('/settings/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.message || 'Failed to import settings'
      );
    }
  }
);

// Settings slice
const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    // Trading settings
    updateTradingSettings: (
      state,
      action: PayloadAction<Partial<TradingSettings>>
    ) => {
      state.trading = { ...state.trading, ...action.payload };
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setDefaultLeverage: (state, action: PayloadAction<number>) => {
      state.trading.defaultLeverage = Math.max(
        1,
        Math.min(100, action.payload)
      );
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setDefaultPositionSize: (state, action: PayloadAction<number>) => {
      state.trading.defaultPositionSize = Math.max(
        0.001,
        Math.min(1, action.payload)
      );
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setDefaultStopLoss: (state, action: PayloadAction<number>) => {
      state.trading.defaultStopLoss = Math.max(
        0.001,
        Math.min(0.5, action.payload)
      );
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setDefaultTakeProfit: (state, action: PayloadAction<number>) => {
      state.trading.defaultTakeProfit = Math.max(
        0.001,
        Math.min(1, action.payload)
      );
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setMaxOpenPositions: (state, action: PayloadAction<number>) => {
      state.trading.maxOpenPositions = Math.max(
        1,
        Math.min(50, action.payload)
      );
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    // Notification settings
    updateNotificationSettings: (
      state,
      action: PayloadAction<Partial<NotificationSettings>>
    ) => {
      state.notifications = { ...state.notifications, ...action.payload };
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setEmailEnabled: (state, action: PayloadAction<boolean>) => {
      state.notifications.email.enabled = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setEmailAddress: (state, action: PayloadAction<string>) => {
      state.notifications.email.address = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setPushEnabled: (state, action: PayloadAction<boolean>) => {
      state.notifications.push.enabled = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setInAppEnabled: (state, action: PayloadAction<boolean>) => {
      state.notifications.inApp.enabled = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    // Security settings
    updateSecuritySettings: (
      state,
      action: PayloadAction<Partial<SecuritySettings>>
    ) => {
      state.security = { ...state.security, ...action.payload };
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setTwoFactorAuth: (state, action: PayloadAction<boolean>) => {
      state.security.twoFactorAuth = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setSessionTimeout: (state, action: PayloadAction<number>) => {
      state.security.sessionTimeout = Math.max(
        300,
        Math.min(86400, action.payload)
      );
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setMaxLoginAttempts: (state, action: PayloadAction<number>) => {
      state.security.maxLoginAttempts = Math.max(
        3,
        Math.min(10, action.payload)
      );
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    // Performance settings
    updatePerformanceSettings: (
      state,
      action: PayloadAction<Partial<PerformanceSettings>>
    ) => {
      state.performance = { ...state.performance, ...action.payload };
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setCachingEnabled: (state, action: PayloadAction<boolean>) => {
      state.performance.enableCaching = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setCacheExpiry: (state, action: PayloadAction<number>) => {
      state.performance.cacheExpiry = Math.max(
        60,
        Math.min(3600, action.payload)
      );
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setDebounceDelay: (state, action: PayloadAction<number>) => {
      state.performance.debounceDelay = Math.max(
        100,
        Math.min(1000, action.payload)
      );
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    // Appearance settings
    updateAppearanceSettings: (
      state,
      action: PayloadAction<Partial<AppearanceSettings>>
    ) => {
      state.appearance = { ...state.appearance, ...action.payload };
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'auto'>) => {
      state.appearance.theme = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setPrimaryColor: (state, action: PayloadAction<string>) => {
      state.appearance.primaryColor = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setSecondaryColor: (state, action: PayloadAction<string>) => {
      state.appearance.secondaryColor = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setAccentColor: (state, action: PayloadAction<string>) => {
      state.appearance.accentColor = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setFontSize: (
      state,
      action: PayloadAction<'small' | 'medium' | 'large'>
    ) => {
      state.appearance.fontSize = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setFontFamily: (state, action: PayloadAction<string>) => {
      state.appearance.fontFamily = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setBorderRadius: (
      state,
      action: PayloadAction<'none' | 'small' | 'medium' | 'large'>
    ) => {
      state.appearance.borderRadius = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setShadows: (
      state,
      action: PayloadAction<'none' | 'small' | 'medium' | 'large'>
    ) => {
      state.appearance.shadows = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setAnimations: (
      state,
      action: PayloadAction<'none' | 'reduced' | 'normal'>
    ) => {
      state.appearance.animations = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    toggleCompactMode: state => {
      state.appearance.compactMode = !state.appearance.compactMode;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    // API settings
    updateAPISettings: (state, action: PayloadAction<Partial<APISettings>>) => {
      state.api = { ...state.api, ...action.payload };
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setBaseUrl: (state, action: PayloadAction<string>) => {
      state.api.baseUrl = action.payload;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setTimeout: (state, action: PayloadAction<number>) => {
      state.api.timeout = Math.max(5000, Math.min(120000, action.payload));
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setRetryAttempts: (state, action: PayloadAction<number>) => {
      state.api.retryAttempts = Math.max(0, Math.min(10, action.payload));
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    setRetryDelay: (state, action: PayloadAction<number>) => {
      state.api.retryDelay = Math.max(100, Math.min(10000, action.payload));
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    // Utility actions
    markAsClean: state => {
      state.isDirty = false;
      state.lastUpdate = new Date().toISOString();
    },

    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.lastUpdate = new Date().toISOString();
    },

    clearError: state => {
      state.error = null;
      state.lastUpdate = new Date().toISOString();
    },

    // Reset actions
    resetToDefaults: state => {
      state.trading = initialState.trading;
      state.notifications = initialState.notifications;
      state.security = initialState.security;
      state.performance = initialState.performance;
      state.appearance = initialState.appearance;
      state.api = initialState.api;
      state.isDirty = true;
      state.lastUpdate = new Date().toISOString();
    },

    // Update last update
    updateLastUpdate: state => {
      state.lastUpdate = new Date().toISOString();
    },
  },
  extraReducers: builder => {
    // Fetch settings
    builder
      .addCase(fetchSettings.pending, state => {
        state.error = null;
      })
      .addCase(fetchSettings.fulfilled, (state, action) => {
        // Merge fetched settings with current state
        Object.assign(state, action.payload);
        state.isDirty = false;
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(fetchSettings.rejected, (state, action) => {
        state.error = action.payload as string;
        state.lastUpdate = new Date().toISOString();
      });

    // Update settings
    builder
      .addCase(updateSettings.pending, state => {
        state.error = null;
      })
      .addCase(updateSettings.fulfilled, (state, action) => {
        // Merge updated settings with current state
        Object.assign(state, action.payload);
        state.isDirty = false;
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(updateSettings.rejected, (state, action) => {
        state.error = action.payload as string;
        state.lastUpdate = new Date().toISOString();
      });

    // Reset settings
    builder
      .addCase(resetSettings.pending, state => {
        state.error = null;
      })
      .addCase(resetSettings.fulfilled, (state, action) => {
        // Reset to fetched default settings
        Object.assign(state, action.payload);
        state.isDirty = false;
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(resetSettings.rejected, (state, action) => {
        state.error = action.payload as string;
        state.lastUpdate = new Date().toISOString();
      });

    // Import settings
    builder
      .addCase(importSettings.pending, state => {
        state.error = null;
      })
      .addCase(importSettings.fulfilled, (state, action) => {
        // Apply imported settings
        Object.assign(state, action.payload);
        state.isDirty = false;
        state.lastUpdate = new Date().toISOString();
      })
      .addCase(importSettings.rejected, (state, action) => {
        state.error = action.payload as string;
        state.lastUpdate = new Date().toISOString();
      });
  },
});

// Export actions
export const {
  // Trading settings
  updateTradingSettings,
  setDefaultLeverage,
  setDefaultPositionSize,
  setDefaultStopLoss,
  setDefaultTakeProfit,
  setMaxOpenPositions,

  // Notification settings
  updateNotificationSettings,
  setEmailEnabled,
  setEmailAddress,
  setPushEnabled,
  setInAppEnabled,

  // Security settings
  updateSecuritySettings,
  setTwoFactorAuth,
  setSessionTimeout,
  setMaxLoginAttempts,

  // Performance settings
  updatePerformanceSettings,
  setCachingEnabled,
  setCacheExpiry,
  setDebounceDelay,

  // Appearance settings
  updateAppearanceSettings,
  setTheme,
  setPrimaryColor,
  setSecondaryColor,
  setAccentColor,
  setFontSize,
  setFontFamily,
  setBorderRadius,
  setShadows,
  setAnimations,
  toggleCompactMode,

  // API settings
  updateAPISettings,
  setBaseUrl,
  setTimeout,
  setRetryAttempts,
  setRetryDelay,

  // Utility actions
  markAsClean,
  setError,
  clearError,

  // Reset actions
  resetToDefaults,
  updateLastUpdate,
} = settingsSlice.actions;

// Export selectors
export const selectSettings = (state: { settings: SettingsState }) =>
  state.settings;
export const selectTradingSettings = (state: { settings: SettingsState }) =>
  state.settings.trading;
export const selectNotificationSettings = (state: {
  settings: SettingsState;
}) => state.settings.notifications;
export const selectSecuritySettings = (state: { settings: SettingsState }) =>
  state.settings.security;
export const selectPerformanceSettings = (state: { settings: SettingsState }) =>
  state.settings.performance;
export const selectAppearanceSettings = (state: { settings: SettingsState }) =>
  state.settings.appearance;
export const selectAPISettings = (state: { settings: SettingsState }) =>
  state.settings.api;
export const selectLastUpdate = (state: { settings: SettingsState }) =>
  state.settings.lastUpdate;
export const selectIsDirty = (state: { settings: SettingsState }) =>
  state.settings.isDirty;
export const selectError = (state: { settings: SettingsState }) =>
  state.settings.error;

// Helper selectors
export const selectIsDarkMode = (state: { settings: SettingsState }) => {
  const theme = state.settings.appearance.theme;
  if (theme === 'auto') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  return theme === 'dark';
};

export const selectIsCompactMode = (state: { settings: SettingsState }) =>
  state.settings.appearance.compactMode;

export const selectIsTwoFactorEnabled = (state: { settings: SettingsState }) =>
  state.settings.security.twoFactorAuth;

export const selectIsCachingEnabled = (state: { settings: SettingsState }) =>
  state.settings.performance.enableCaching;

export const selectIsEmailEnabled = (state: { settings: SettingsState }) =>
  state.settings.notifications.email.enabled;

export const selectIsPushEnabled = (state: { settings: SettingsState }) =>
  state.settings.notifications.push.enabled;

export const selectIsInAppEnabled = (state: { settings: SettingsState }) =>
  state.settings.notifications.inApp.enabled;

export const selectHasChanges = (state: { settings: SettingsState }) =>
  state.settings.isDirty;

// Export reducer
export default settingsSlice.reducer;
