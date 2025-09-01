// Environment configuration for frontend
// Vite automatically loads environment variables with VITE_ prefix

interface AppConfig {
  // API Configuration
  apiUrl: string;
  apiTimeout: number;
  
  // WebSocket Configuration
  wsUrl: string;
  wsReconnectAttempts: number;
  wsReconnectInterval: number;
  
  // Application Configuration
  environment: string;
  debug: boolean;
  
  // Feature Flags
  enableRealTimeUpdates: boolean;
  enableNotifications: boolean;
  enableAnalytics: boolean;
  
  // UI Configuration
  defaultTheme: 'light' | 'dark' | 'auto';
  dataRefreshInterval: number;
  maxRetryAttempts: number;
  
  // Trading Configuration
  defaultPositionSize: number;
  maxDailyLoss: number;
  supportedSymbols: string[];
}

// Get environment variable with fallback
const getEnvVar = (key: string, defaultValue: string): string => {
  return import.meta.env[`VITE_${key}`] || defaultValue;
};

const getBooleanEnv = (key: string, defaultValue: boolean): boolean => {
  const value = getEnvVar(key, defaultValue.toString());
  return value.toLowerCase() === 'true';
};

const getNumberEnv = (key: string, defaultValue: number): number => {
  const value = getEnvVar(key, defaultValue.toString());
  return Number(value) || defaultValue;
};

const getArrayEnv = (key: string, defaultValue: string[]): string[] => {
  const value = getEnvVar(key, JSON.stringify(defaultValue));
  try {
    return JSON.parse(value);
  } catch {
    return defaultValue;
  }
};

export const config: AppConfig = {
  // API Configuration
  apiUrl: getEnvVar('API_URL', 'http://localhost:8000/api/v1'),
  apiTimeout: getNumberEnv('API_TIMEOUT', 30000),
  
  // WebSocket Configuration
  wsUrl: getEnvVar('WS_URL', 'ws://localhost:8000/api/v1/ws'),
  wsReconnectAttempts: getNumberEnv('WS_RECONNECT_ATTEMPTS', 5),
  wsReconnectInterval: getNumberEnv('WS_RECONNECT_INTERVAL', 3000),
  
  // Application Configuration
  environment: getEnvVar('ENVIRONMENT', 'development'),
  debug: getBooleanEnv('DEBUG', true),
  
  // Feature Flags
  enableRealTimeUpdates: getBooleanEnv('ENABLE_REAL_TIME_UPDATES', true),
  enableNotifications: getBooleanEnv('ENABLE_NOTIFICATIONS', true),
  enableAnalytics: getBooleanEnv('ENABLE_ANALYTICS', false),
  
  // UI Configuration
  defaultTheme: getEnvVar('DEFAULT_THEME', 'auto') as 'light' | 'dark' | 'auto',
  dataRefreshInterval: getNumberEnv('DATA_REFRESH_INTERVAL', 5000),
  maxRetryAttempts: getNumberEnv('MAX_RETRY_ATTEMPTS', 3),
  
  // Trading Configuration
  defaultPositionSize: getNumberEnv('DEFAULT_POSITION_SIZE', 10),
  maxDailyLoss: getNumberEnv('MAX_DAILY_LOSS', 100),
  supportedSymbols: getArrayEnv('SUPPORTED_SYMBOLS', [
    'R_10', 'R_25', 'R_50', 'R_75', 'R_100',
    'BOOM_1000', 'CRASH_1000', 'STEP_10', 'STEP_25'
  ]),
};

// Development-only logging
if (config.debug && config.environment === 'development') {
  console.log('App Configuration:', config);
}

export default config;

