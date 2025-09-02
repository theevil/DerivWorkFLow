import React, { useState, useEffect } from 'react';
import {
  TextInput,
  PasswordInput,
  NumberInput,
  Switch,
  Button,
  Card,
  Group,
  Stack,
  Title,
  Text,
  Divider,
  Alert,
  Select,
  Grid,
  Badge,
  ActionIcon,
  Tooltip,
} from '@mantine/core';
import {
  IconKey,
  IconSettings,
  IconRobot,
  IconShield,
  IconBrain,
  IconDatabase,
  IconCheck,
  IconX,
  IconEye,
  IconEyeOff,
  IconTestPipe,
  IconRefresh,
  IconAlertTriangle,
  IconInfoCircle,
  IconTrendingUp,
  IconTarget,
  IconCalculator,
  IconStack,
  IconDeviceFloppy,
} from '@tabler/icons-react';
import { Layout } from '../components/Layout';
import { notifications } from '@mantine/notifications';
import { api } from '../lib/api';
import { useAuthStore } from '../stores/auth';

interface UserSettings {
  // Deriv API Configuration
  derivToken: string;
  derivAppId: string;

  // Trading Parameters
  profitTop: number;
  profitLoss: number;
  stopLoss: number;
  takeProfit: number;
  maxDailyLoss: number;
  positionSize: number;

  // AI Configuration
  aiConfidenceThreshold: number;
  aiAnalysisInterval: number;
  maxPositionsPerUser: number;
  aiModel: string;
  aiTemperature: number;
  aiMaxTokens: number;
  aiProvider: string; // local, openai, hybrid

  // OpenAI Configuration
  openaiApiKey: string;
  langchainApiKey: string;
  langsmithProject: string;

  // Risk Management
  autoStopLossEnabled: boolean;
  autoTakeProfitEnabled: boolean;
  emergencyStopEnabled: boolean;
  circuitBreakerEnabled: boolean;

  // Automation Settings
  autoTradingEnabled: boolean;
  marketScanInterval: number;
  positionMonitorInterval: number;
  signalExecutionDelay: number;
  maxConcurrentPositions: number;

  // Learning Configuration
  learningDataLookbackDays: number;
  minTrainingSamples: number;
  modelRetrainIntervalHours: number;
}

const defaultSettings: UserSettings = {
  derivToken: '',
  derivAppId: '1089',
  profitTop: 15.0, // Conservative profit target (10-20% range)
  profitLoss: 3.0, // Small loss tolerance (2-5% range)
  stopLoss: 10.0, // Moderate stop loss (5-15% range)
  takeProfit: 25.0, // Good profit target (20-30% range)
  maxDailyLoss: 50.0, // Daily loss limit ($25-100 range)
  positionSize: 5.0, // Conservative position size ($2-10 range)
  aiConfidenceThreshold: 0.7, // High confidence threshold (0.6-0.8 range)
  aiAnalysisInterval: 60, // 1 minute analysis (30-120 sec range)
  maxPositionsPerUser: 3, // Conservative concurrent positions (2-5 range)
  aiModel: 'phi-3-mini', // Default to local AI model
  aiTemperature: 0.2, // Low creativity for trading (0.1-0.3 range)
  aiMaxTokens: 1000,
  aiProvider: 'local', // Default to local AI
  openaiApiKey: '',
  langchainApiKey: '',
  langsmithProject: 'deriv-trading',
  autoStopLossEnabled: true,
  autoTakeProfitEnabled: true,
  emergencyStopEnabled: true,
  circuitBreakerEnabled: true,
  autoTradingEnabled: false,
  marketScanInterval: 45, // Moderate scanning (30-90 sec range)
  positionMonitorInterval: 15, // Regular monitoring (10-30 sec range)
  signalExecutionDelay: 3, // Quick execution (2-10 sec range)
  maxConcurrentPositions: 3, // Conservative limit (2-5 range)
  learningDataLookbackDays: 14, // 2 weeks lookback (7-30 days range)
  minTrainingSamples: 150, // Adequate training data (100-300 range)
  modelRetrainIntervalHours: 24, // Daily retraining (12-48 hours range)
};

const aiModelOptions = [
  // Local AI Models (Recommended for microtransactions)
  { value: 'phi-3-mini', label: 'Phi-3 Mini (Local - Recommended)' },
  { value: 'gemma-2b', label: 'Gemma 2B (Local)' },
  { value: 'llama3.1-3b', label: 'Llama 3.1 3B (Local)' },
  { value: 'llama3.1-8b', label: 'Llama 3.1 8B (Local)' },
  { value: 'mistral-7b', label: 'Mistral 7B (Local)' },
  // OpenAI Models
  { value: 'gpt-4o-mini', label: 'GPT-4o Mini (OpenAI)' },
  { value: 'gpt-4o', label: 'GPT-4o (OpenAI)' },
  { value: 'gpt-4-turbo', label: 'GPT-4 Turbo (OpenAI)' },
  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo (OpenAI)' },
];

const aiProviderOptions = [
  { value: 'local', label: 'Local AI (Recommended)' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'hybrid', label: 'Hybrid (Local + OpenAI)' },
];

// Common input styles for consistency
const inputStyles = {
  label: {
    fontSize: '16px',
    fontWeight: 700,
    color: '#000000',
    marginBottom: '8px',
    textShadow: 'none',
  },
  description: {
    fontSize: '14px',
    color: '#000000',
    marginBottom: '10px',
    fontWeight: 600,
  },
  input: {
    fontSize: '15px',
    fontWeight: 500,
    padding: '12px 16px',
    borderWidth: '2px',
    borderRadius: '12px',
    borderColor: '#8D6E63',
    backgroundColor: '#FFFFFF',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    transition: 'all 0.2s ease',
    color: '#000000',
    '&::placeholder': {
      color: '#666666',
      fontSize: '14px',
      fontWeight: 400,
      opacity: 1,
    },
    '&:focus': {
      borderColor: '#00BCD4',
      backgroundColor: '#FFFFFF',
      boxShadow: '0 4px 12px rgba(0, 188, 212, 0.2)',
      outline: 'none',
    },
    '&:hover': {
      borderColor: '#6D4C41',
      backgroundColor: '#FAFAFA',
    },
  },
  leftSection: {
    marginLeft: '8px',
    color: '#8D6E63',
  },
};

export function SettingsPage() {
  const { isAuthenticated, token } = useAuthStore();
  const [settings, setSettings] = useState<UserSettings>(defaultSettings);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savingSection, setSavingSection] = useState<string | null>(null);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<
    'success' | 'error' | null
  >(null);
  const [showApiKeys, setShowApiKeys] = useState(false);
  const [unsavedChanges, setUnsavedChanges] = useState(false);

  useEffect(() => {
    if (isAuthenticated && token) {
      // Debug authentication status
      console.log('Settings page - Auth status:', {
        isAuthenticated,
        hasToken: !!token,
      });
      api.debugAuth();

      // Ensure token is set in API client
      api.setToken(token);

      loadSettings();
    } else if (!isAuthenticated) {
      // Don't show notification here, just log for debugging
      console.log(
        'User not authenticated, settings page will show login prompt'
      );
    }
  }, [isAuthenticated, token]);

  // Add a function to check if we should attempt to load settings
  const shouldLoadSettings = () => {
    return isAuthenticated && token && !loading;
  };

  const loadSettings = async () => {
    if (!isAuthenticated || !token) {
      console.log('User not authenticated, skipping settings load');
      return;
    }

    setLoading(true);
    try {
      // Load user settings from the settings endpoint
      const userSettings = await api.getSettings();

      // Load user trading parameters
      const tradingParams = await api.getTradingParameters();

      // Load automation configuration
      const automationConfig = await api.getAutoTradingConfig();

      // Merge with default settings
      setSettings(prev => ({
        ...prev,
        // Deriv settings
        derivToken: userSettings?.deriv_token ? '***configured***' : '',
        derivAppId: userSettings?.deriv_app_id || prev.derivAppId,

        // Trading parameters
        profitTop: tradingParams?.profit_top || prev.profitTop,
        profitLoss: tradingParams?.profit_loss || prev.profitLoss,
        stopLoss: tradingParams?.stop_loss || prev.stopLoss,
        takeProfit: tradingParams?.take_profit || prev.takeProfit,
        maxDailyLoss: tradingParams?.max_daily_loss || prev.maxDailyLoss,
        positionSize: tradingParams?.position_size || prev.positionSize,

        // AI Configuration
        aiConfidenceThreshold:
          userSettings?.ai_confidence_threshold || prev.aiConfidenceThreshold,
        aiAnalysisInterval:
          userSettings?.ai_analysis_interval || prev.aiAnalysisInterval,
        maxPositionsPerUser:
          userSettings?.max_positions_per_user || prev.maxPositionsPerUser,
        aiModel: userSettings?.ai_model || prev.aiModel,
        aiTemperature: userSettings?.ai_temperature || prev.aiTemperature,
        aiMaxTokens: userSettings?.ai_max_tokens || prev.aiMaxTokens,

        // OpenAI Configuration
        openaiApiKey: userSettings?.openai_api_key ? '***configured***' : '',
        langchainApiKey: userSettings?.langchain_api_key
          ? '***configured***'
          : '',
        langsmithProject:
          userSettings?.langsmith_project || prev.langsmithProject,

        // Risk Management
        autoStopLossEnabled:
          userSettings?.auto_stop_loss_enabled ?? prev.autoStopLossEnabled,
        autoTakeProfitEnabled:
          userSettings?.auto_take_profit_enabled ?? prev.autoTakeProfitEnabled,
        emergencyStopEnabled:
          userSettings?.emergency_stop_enabled ?? prev.emergencyStopEnabled,
        circuitBreakerEnabled:
          userSettings?.circuit_breaker_enabled ?? prev.circuitBreakerEnabled,

        // Automation Settings
        autoTradingEnabled:
          automationConfig?.enabled ?? prev.autoTradingEnabled,
        marketScanInterval:
          automationConfig?.config?.market_scan_interval ||
          prev.marketScanInterval,
        positionMonitorInterval:
          automationConfig?.config?.position_monitor_interval ||
          prev.positionMonitorInterval,
        signalExecutionDelay:
          userSettings?.signal_execution_delay || prev.signalExecutionDelay,
        maxConcurrentPositions:
          automationConfig?.config?.max_concurrent_positions ||
          prev.maxConcurrentPositions,

        // Learning Configuration
        learningDataLookbackDays:
          userSettings?.learning_data_lookback_days ||
          prev.learningDataLookbackDays,
        minTrainingSamples:
          userSettings?.min_training_samples || prev.minTrainingSamples,
        modelRetrainIntervalHours:
          userSettings?.model_retrain_interval_hours ||
          prev.modelRetrainIntervalHours,
      }));
    } catch (error: any) {
      console.error('Error loading settings:', error);

      // Handle authentication errors specifically
      if (
        error.message?.includes('Not authenticated') ||
        error.message?.includes('401')
      ) {
        notifications.show({
          title: 'Authentication Required',
          message: 'Please log in to access settings',
          color: 'orange',
          icon: <IconAlertTriangle size={16} />,
        });
        return;
      }

      notifications.show({
        title: 'Error',
        message: 'Failed to load settings. Please try again later.',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setLoading(false);
    }
  };

  const saveSection = async (sectionName: string, sectionData: any) => {
    if (!isAuthenticated || !token) {
      notifications.show({
        title: 'Authentication Required',
        message: 'Please log in to save settings',
        color: 'orange',
        icon: <IconAlertTriangle size={16} />,
      });
      return;
    }

    setSavingSection(sectionName);
    try {
      if (sectionName === 'deriv') {
        // Save Deriv token
        if (
          sectionData.derivToken &&
          sectionData.derivToken !== '***configured***'
        ) {
          await api.setDerivToken(sectionData.derivToken);
        }
        // Save Deriv app ID via settings
        await api.updateSettings({ deriv_app_id: sectionData.derivAppId });
      }

      if (sectionName === 'trading') {
        // Convert frontend field names to backend field names
        const tradingData = {
          profit_top: sectionData.profitTop,
          profit_loss: sectionData.profitLoss,
          stop_loss: sectionData.stopLoss,
          take_profit: sectionData.takeProfit,
          max_daily_loss: sectionData.maxDailyLoss,
          position_size: sectionData.positionSize,
        };

        // Try to update first, if it fails, create new
        try {
          await api.updateTradingParameters(tradingData);
        } catch (error: any) {
          if (error.message?.includes('not found')) {
            await api.createTradingParameters(tradingData);
          } else {
            throw error;
          }
        }
      }

      if (sectionName === 'automation') {
        // Convert to automation config format
        const automationData = {
          enabled: sectionData.autoTradingEnabled,
          max_concurrent_positions: sectionData.maxConcurrentPositions,
          market_scan_interval: sectionData.marketScanInterval,
          position_monitor_interval: sectionData.positionMonitorInterval,
          auto_stop_loss: sectionData.autoStopLossEnabled,
          auto_take_profit: sectionData.autoTakeProfitEnabled,
        };
        await api.configureAutoTrading(automationData);
      }

      if (sectionName === 'ai') {
        // Convert frontend field names to backend field names
        const aiData = {
          openai_api_key:
            sectionData.openaiApiKey !== '***configured***'
              ? sectionData.openaiApiKey
              : undefined,
          langchain_api_key:
            sectionData.langchainApiKey !== '***configured***'
              ? sectionData.langchainApiKey
              : undefined,
          langsmith_project: sectionData.langsmithProject,
          ai_model: sectionData.aiModel,
          ai_confidence_threshold: sectionData.aiConfidenceThreshold,
          ai_temperature: sectionData.aiTemperature,
          ai_analysis_interval: sectionData.aiAnalysisInterval,
          ai_max_tokens: sectionData.aiMaxTokens,
          max_positions_per_user: sectionData.maxPositionsPerUser,
          learning_data_lookback_days: sectionData.learningDataLookbackDays,
          min_training_samples: sectionData.minTrainingSamples,
          model_retrain_interval_hours: sectionData.modelRetrainIntervalHours,
        };
        await api.updateSettings(aiData);
      }

      if (sectionName === 'risk') {
        const riskData = {
          auto_stop_loss_enabled: sectionData.autoStopLossEnabled,
          auto_take_profit_enabled: sectionData.autoTakeProfitEnabled,
          emergency_stop_enabled: sectionData.emergencyStopEnabled,
          circuit_breaker_enabled: sectionData.circuitBreakerEnabled,
        };
        await api.updateSettings(riskData);
      }

      notifications.show({
        title: 'Section Saved',
        message: `${sectionName} settings have been saved successfully`,
        color: 'green',
        icon: <IconCheck size={16} />,
      });
    } catch (error: any) {
      console.error(`Error saving ${sectionName} settings:`, error);

      // Handle authentication errors specifically
      if (
        error.message?.includes('Not authenticated') ||
        error.message?.includes('401')
      ) {
        notifications.show({
          title: 'Authentication Required',
          message: 'Please log in to save settings',
          color: 'orange',
          icon: <IconAlertTriangle size={16} />,
        });
        return;
      }

      notifications.show({
        title: 'Save Error',
        message: error.message || `Failed to save ${sectionName} settings`,
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setSavingSection(null);
    }
  };

  const saveSettings = async () => {
    if (!isAuthenticated || !token) {
      notifications.show({
        title: 'Authentication Required',
        message: 'Please log in to save settings',
        color: 'orange',
        icon: <IconAlertTriangle size={16} />,
      });
      return;
    }

    setSaving(true);
    try {
      // Save Deriv token
      if (settings.derivToken && settings.derivToken !== '***configured***') {
        await api.setDerivToken(settings.derivToken);
      }

      // Save trading parameters
      const tradingData = {
        profit_top: settings.profitTop,
        profit_loss: settings.profitLoss,
        stop_loss: settings.stopLoss,
        take_profit: settings.takeProfit,
        max_daily_loss: settings.maxDailyLoss,
        position_size: settings.positionSize,
      };

      try {
        await api.updateTradingParameters(tradingData);
      } catch (error: any) {
        if (error.message?.includes('not found')) {
          await api.createTradingParameters(tradingData);
        } else {
          throw error;
        }
      }

      // Save automation configuration
      const automationData = {
        enabled: settings.autoTradingEnabled,
        max_concurrent_positions: settings.maxConcurrentPositions,
        market_scan_interval: settings.marketScanInterval,
        position_monitor_interval: settings.positionMonitorInterval,
        auto_stop_loss: settings.autoStopLossEnabled,
        auto_take_profit: settings.autoTakeProfitEnabled,
      };
      await api.configureAutoTrading(automationData);

      // Save AI and other settings
      const settingsData = {
        deriv_app_id: settings.derivAppId,
        openai_api_key:
          settings.openaiApiKey !== '***configured***'
            ? settings.openaiApiKey
            : undefined,
        langchain_api_key:
          settings.langchainApiKey !== '***configured***'
            ? settings.langchainApiKey
            : undefined,
        langsmith_project: settings.langsmithProject,
        ai_model: settings.aiModel,
        ai_confidence_threshold: settings.aiConfidenceThreshold,
        ai_temperature: settings.aiTemperature,
        ai_analysis_interval: settings.aiAnalysisInterval,
        ai_max_tokens: settings.aiMaxTokens,
        max_positions_per_user: settings.maxPositionsPerUser,
        auto_stop_loss_enabled: settings.autoStopLossEnabled,
        auto_take_profit_enabled: settings.autoTakeProfitEnabled,
        emergency_stop_enabled: settings.emergencyStopEnabled,
        circuit_breaker_enabled: settings.circuitBreakerEnabled,
        signal_execution_delay: settings.signalExecutionDelay,
        learning_data_lookback_days: settings.learningDataLookbackDays,
        min_training_samples: settings.minTrainingSamples,
        model_retrain_interval_hours: settings.modelRetrainIntervalHours,
      };
      await api.updateSettings(settingsData);

      setUnsavedChanges(false);
      notifications.show({
        title: 'Settings Saved',
        message: 'All settings have been saved successfully',
        color: 'green',
        icon: <IconCheck size={16} />,
      });
    } catch (error: any) {
      console.error('Error saving settings:', error);

      // Handle authentication errors specifically
      if (
        error.message?.includes('Not authenticated') ||
        error.message?.includes('401')
      ) {
        notifications.show({
          title: 'Authentication Required',
          message: 'Please log in to save settings',
          color: 'orange',
          icon: <IconAlertTriangle size={16} />,
        });
        return;
      }

      notifications.show({
        title: 'Save Error',
        message: error.message || 'Failed to save settings',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setSaving(false);
    }
  };

  const testDerivConnection = async () => {
    if (!settings.derivToken || settings.derivToken === '***configured***') {
      notifications.show({
        title: 'Token Required',
        message: 'Please enter your Deriv API token',
        color: 'orange',
        icon: <IconAlertTriangle size={16} />,
      });
      return;
    }

    if (!isAuthenticated || !token) {
      notifications.show({
        title: 'Authentication Required',
        message: 'Please log in to test connection',
        color: 'orange',
        icon: <IconAlertTriangle size={16} />,
      });
      return;
    }

    setTestingConnection(true);
    setConnectionStatus(null);

    try {
      await api.testDerivConnection(settings.derivToken);
      setConnectionStatus('success');
      notifications.show({
        title: 'Connection Successful',
        message: 'Deriv API token is valid',
        color: 'green',
        icon: <IconCheck size={16} />,
      });
    } catch (error: any) {
      setConnectionStatus('error');

      // Handle authentication errors specifically
      if (
        error.message?.includes('Not authenticated') ||
        error.message?.includes('401')
      ) {
        notifications.show({
          title: 'Authentication Required',
          message: 'Please log in to test connection',
          color: 'orange',
          icon: <IconAlertTriangle size={16} />,
        });
        return;
      }

      notifications.show({
        title: 'Connection Error',
        message: error.message || 'Invalid Deriv API token',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setTestingConnection(false);
    }
  };

  const handleSettingChange = (key: keyof UserSettings, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value,
    }));
    setUnsavedChanges(true);
  };

  const testLocalAI = async () => {
    if (!isAuthenticated || !token) {
      notifications.show({
        title: 'Authentication Required',
        message: 'Please log in to test local AI',
        color: 'orange',
        icon: <IconAlertTriangle size={16} />,
      });
      return;
    }

    setTestingConnection(true);
    try {
      const result = await api.testLocalAI();

      if (result.status === 'available') {
        notifications.show({
          title: 'Local AI Test Successful',
          message: `Found ${result.working_models?.length || 0} working models`,
          color: 'green',
          icon: <IconCheck size={16} />,
        });
      } else {
        notifications.show({
          title: 'Local AI Test Failed',
          message: result.message || 'No working models found',
          color: 'red',
          icon: <IconX size={16} />,
        });
      }
    } catch (error: any) {
      console.error('Error testing local AI:', error);
      notifications.show({
        title: 'Test Error',
        message: error.message || 'Failed to test local AI',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setTestingConnection(false);
    }
  };

  const initializeLocalAI = async () => {
    if (!isAuthenticated || !token) {
      notifications.show({
        title: 'Authentication Required',
        message: 'Please log in to initialize local AI',
        color: 'orange',
        icon: <IconAlertTriangle size={16} />,
      });
      return;
    }

    try {
      // Initialize the default model
      const result = await api.initializeLocalModel('phi-3-mini');

      if (result.status === 'success') {
        notifications.show({
          title: 'Local AI Initialized',
          message: 'Models initialized successfully',
          color: 'green',
          icon: <IconCheck size={16} />,
        });
      } else {
        notifications.show({
          title: 'Initialization Failed',
          message: result.message || 'Failed to initialize models',
          color: 'red',
          icon: <IconX size={16} />,
        });
      }
    } catch (error: any) {
      console.error('Error initializing local AI:', error);
      notifications.show({
        title: 'Initialization Error',
        message: error.message || 'Failed to initialize local AI',
        color: 'red',
        icon: <IconX size={16} />,
      });
    }
  };

  const resetToDefaults = async () => {
    if (!isAuthenticated || !token) {
      notifications.show({
        title: 'Authentication Required',
        message: 'Please log in to reset settings',
        color: 'orange',
        icon: <IconAlertTriangle size={16} />,
      });
      return;
    }

    try {
      await api.resetSettingsToDefaults();
      setSettings(defaultSettings);
      setUnsavedChanges(true);
      notifications.show({
        title: 'Settings Reset',
        message: 'Default values have been restored',
        color: 'blue',
        icon: <IconRefresh size={16} />,
      });
    } catch (error: any) {
      console.error('Error resetting settings:', error);

      // Handle authentication errors specifically
      if (
        error.message?.includes('Not authenticated') ||
        error.message?.includes('401')
      ) {
        notifications.show({
          title: 'Authentication Required',
          message: 'Please log in to reset settings',
          color: 'orange',
          icon: <IconAlertTriangle size={16} />,
        });
        return;
      }

      notifications.show({
        title: 'Reset Error',
        message: error.message || 'Failed to reset settings',
        color: 'red',
        icon: <IconX size={16} />,
      });
    }
  };

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className='p-8 max-w-7xl mx-auto'>
          <div className='flex items-center justify-center min-h-[60vh]'>
            <Card className='p-8 max-w-md w-full text-center'>
              <IconX size={48} className='text-red-500 mx-auto mb-4' />
              <Title
                order={2}
                className='text-2xl font-bold text-retro-brown-800 mb-4'
              >
                Authentication Required
              </Title>
              <Text size='lg' className='text-retro-brown-600 mb-6'>
                Please log in to access the settings page and configure your
                trading bot.
              </Text>
              <div className='flex gap-4'>
                <Button
                  component='a'
                  href='/login'
                  size='lg'
                  className='flex-1'
                  styles={{
                    root: {
                      backgroundColor: 'var(--retro-turquoise)',
                      color: 'var(--retro-dark)',
                      '&:hover': {
                        backgroundColor: 'var(--retro-cream)',
                      },
                    },
                  }}
                >
                  Go to Login
                </Button>
                <Button
                  component='a'
                  href='/register'
                  size='lg'
                  variant='outline'
                  className='flex-1'
                  styles={{
                    root: {
                      borderColor: 'var(--retro-turquoise)',
                      color: 'var(--retro-turquoise)',
                      '&:hover': {
                        backgroundColor: 'var(--retro-cream)',
                        color: 'var(--retro-dark)',
                      },
                    },
                  }}
                >
                  Register
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className='p-8 max-w-7xl mx-auto'>
        <div className='mb-8'>
          <Title
            order={1}
            className='text-4xl font-bold text-retro-brown-800 mb-3'
          >
            Bot Configuration
          </Title>
          <Text size='lg' className='text-retro-brown-600 leading-relaxed'>
            Configure all necessary parameters for optimal trading bot
            performance. Adjust settings carefully based on your risk tolerance
            and trading strategy.
          </Text>
        </div>

        {unsavedChanges && (
          <Alert
            icon={<IconAlertTriangle size={18} />}
            title='Unsaved Changes'
            color='orange'
            className='mb-6 p-4 rounded-xl border-2 border-orange-200 bg-white'
            styles={{
              root: { backgroundColor: 'white' },
              title: { fontSize: '16px', fontWeight: 600 },
              message: { fontSize: '14px' },
            }}
          >
            You have unsaved changes. Don't forget to save your configuration.
          </Alert>
        )}

        <Grid>
          <Grid.Col span={{ base: 12, lg: 8 }}>
            <Stack gap={80}>
              {/* Deriv API Configuration */}
              <Card className='relative p-6 shadow-xl border-3 border-retro-brown-300 bg-white overflow-hidden rounded-2xl mb-6'>
                {/* Header with icon and title inside card */}
                <div className='flex items-center justify-between mb-6'>
                  <div className='flex items-center gap-4'>
                    <div className='p-3 rounded-xl bg-white border-2 border-retro-brown-300 shadow-md'>
                      <IconKey className='text-retro-brown-600' size={24} />
                    </div>
                    <div>
                      <Title
                        order={2}
                        className='text-xl font-bold text-retro-brown-800 mb-1'
                      >
                        Deriv API Configuration
                      </Title>
                      <Text
                        size='sm'
                        className='text-retro-brown-600 font-medium'
                      >
                        Connect your Deriv account for live trading
                      </Text>
                    </div>
                  </div>
                  {connectionStatus && (
                    <Badge
                      size='lg'
                      color={connectionStatus === 'success' ? 'green' : 'red'}
                      variant='filled'
                      className='px-4 py-2 text-sm font-bold shadow-lg'
                      radius='xl'
                    >
                      {connectionStatus === 'success'
                        ? '✓ Connected'
                        : '✗ Error'}
                    </Badge>
                  )}
                </div>

                <Stack gap='xl'>
                  <div>
                    <Text size='sm' className='text-black font-bold mb-2'>
                      Deriv App ID
                    </Text>
                    <Text size='xs' className='text-black font-semibold mb-3'>
                      Application ID registered in Deriv (default: 1089)
                    </Text>
                    <div className='relative'>
                      <TextInput
                        size='md'
                        placeholder='1089'
                        value={settings.derivAppId}
                        onChange={e =>
                          handleSettingChange(
                            'derivAppId',
                            e.currentTarget.value
                          )
                        }
                        styles={{
                          ...inputStyles,
                          input: {
                            ...inputStyles.input,
                            paddingLeft: '50px',
                            paddingRight: '16px',
                          },
                        }}
                      />
                      <div
                        className='absolute left-6 pointer-events-none flex items-center justify-center'
                        style={{ height: '20px', top: '17px' }}
                      >
                        <IconDatabase size={20} className='text-cyan-600' />
                      </div>
                    </div>
                  </div>

                  <div>
                    <Text size='sm' className='text-black font-bold mb-2'>
                      Deriv API Token
                    </Text>
                    <Text size='xs' className='text-black font-semibold mb-3'>
                      Authentication token to connect with Deriv API
                    </Text>
                    <div className='relative'>
                      <PasswordInput
                        size='md'
                        placeholder='Enter your Deriv API token (e.g., a1-xxxxxxxxxxxx)'
                        value={settings.derivToken}
                        onChange={e =>
                          handleSettingChange(
                            'derivToken',
                            e.currentTarget.value
                          )
                        }
                        visible={showApiKeys}
                        onVisibilityChange={setShowApiKeys}
                        rightSection={
                          <Tooltip label='Test connection'>
                            <ActionIcon
                              variant='filled'
                              color='cyan'
                              size='sm'
                              onClick={testDerivConnection}
                              loading={testingConnection}
                              className='mr-2'
                            >
                              <IconTestPipe size={14} />
                            </ActionIcon>
                          </Tooltip>
                        }
                        styles={{
                          ...inputStyles,
                          input: {
                            ...inputStyles.input,
                            paddingLeft: '50px',
                            paddingRight: '16px',
                          },
                        }}
                      />
                      <div
                        className='absolute left-6 pointer-events-none flex items-center justify-center'
                        style={{ height: '20px', top: '17px' }}
                      >
                        <IconKey size={20} className='text-red-600' />
                      </div>
                    </div>
                  </div>

                  <Alert
                    icon={<IconInfoCircle size={20} />}
                    color='blue'
                    className='p-5 rounded-xl border-2 border-blue-200 bg-white'
                    styles={{
                      root: { backgroundColor: 'white' },
                      message: {
                        fontSize: '14px',
                        lineHeight: '1.6',
                        color: '#000000',
                      },
                    }}
                  >
                    <Text
                      size='sm'
                      className='leading-relaxed text-black font-semibold'
                    >
                      <strong className='text-blue-800 font-bold'>
                        How to get your Deriv token:
                      </strong>
                      <br />
                      1. Go to your Deriv account
                      <br />
                      2. Navigate to Settings → Security and privacy → API
                      tokens
                      <br />
                      3. Create a new token with trading permissions
                      <br />
                      4. Copy and paste the token here
                    </Text>
                  </Alert>

                  {/* Save Button for Deriv Section */}
                  <div className='flex justify-end pt-6 border-t-2 border-retro-brown-200 mt-6'>
                    <Button
                      onClick={() =>
                        saveSection('deriv', {
                          derivToken: settings.derivToken,
                          derivAppId: settings.derivAppId,
                        })
                      }
                      loading={savingSection === 'deriv'}
                      size='lg'
                      className='px-8 py-3 text-base font-bold shadow-lg flex items-center justify-center'
                      styles={{
                        root: {
                          background: 'var(--retro-turquoise)',
                          color: 'var(--retro-dark)',
                          border: '2px solid var(--retro-turquoise)',
                          borderRadius: '12px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px',
                          '&:hover': {
                            background: 'var(--retro-cream)',
                            color: 'var(--retro-dark)',
                            borderColor: 'var(--retro-cream)',
                            transform: 'translateY(-2px)',
                          },
                        },
                        inner: {
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px',
                        },
                      }}
                      leftSection={<IconDeviceFloppy size={18} />}
                    >
                      Save Deriv Settings
                    </Button>
                  </div>
                </Stack>
              </Card>

              {/* Trading Parameters */}
              <Card className='relative p-6 shadow-xl border-3 border-retro-brown-300 bg-white overflow-hidden rounded-2xl mb-6'>
                {/* Header with icon and title inside card */}
                <div className='flex items-center gap-4 mb-6'>
                  <div className='p-3 rounded-xl bg-white border-2 border-retro-brown-300 shadow-md'>
                    <IconSettings className='text-retro-brown-600' size={24} />
                  </div>
                  <div>
                    <Title
                      order={2}
                      className='text-xl font-bold text-black mb-1'
                    >
                      Trading Parameters
                    </Title>
                    <Text size='sm' className='text-black font-semibold'>
                      Set your risk management and position sizing rules
                    </Text>
                  </div>
                </div>

                <div className='flex flex-col md:flex-row md:gap-8 gap-4'>
                  <div className='flex-1'>
                    <div className='flex flex-col'>
                      <Text size='sm' className='text-black font-bold mb-2'>
                        Profit Target (%)
                      </Text>
                      <Text size='xs' className='text-black font-semibold mb-3'>
                        Target profit percentage (Recommended: 10-20%)
                      </Text>
                      <div className='relative'>
                        <NumberInput
                          size='md'
                          value={settings.profitTop}
                          onChange={value =>
                            handleSettingChange('profitTop', value || 0)
                          }
                          min={0.1}
                          max={100}
                          step={0.1}
                          decimalScale={1}
                          placeholder='15.0'
                          styles={{
                            ...inputStyles,
                            input: {
                              ...inputStyles.input,
                              paddingLeft: '50px',
                              paddingRight: '40px',
                            },
                          }}
                        />
                        <div
                          className='absolute pointer-events-none'
                          style={{ left: '76px', top: '13px' }}
                        >
                          <span className='text-green-600 font-bold text-sm'>
                            %
                          </span>
                        </div>
                        <div
                          className='absolute left-6 pointer-events-none flex items-center justify-center'
                          style={{ height: '20px', top: '17px' }}
                        >
                          <IconTrendingUp
                            size={20}
                            className='text-green-600'
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className='flex-1'>
                    <div className='flex flex-col'>
                      <Text size='sm' className='text-black font-bold mb-2'>
                        Stop Loss (%)
                      </Text>
                      <Text size='xs' className='text-black font-semibold mb-3'>
                        Maximum loss percentage (Recommended: 5-15%)
                      </Text>
                      <div className='relative'>
                        <NumberInput
                          size='md'
                          value={settings.stopLoss}
                          onChange={value =>
                            handleSettingChange('stopLoss', value || 0)
                          }
                          min={0.1}
                          max={100}
                          step={0.1}
                          decimalScale={1}
                          placeholder='10.0'
                          styles={{
                            ...inputStyles,
                            input: {
                              ...inputStyles.input,
                              paddingLeft: '50px',
                              paddingRight: '40px',
                            },
                          }}
                        />
                        <div
                          className='absolute pointer-events-none'
                          style={{ left: '76px', top: '13px' }}
                        >
                          <span className='text-red-600 font-bold text-sm'>
                            %
                          </span>
                        </div>
                        <div
                          className='absolute left-6 pointer-events-none flex items-center justify-center'
                          style={{ height: '20px', top: '17px' }}
                        >
                          <IconShield size={20} className='text-red-600' />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className='flex flex-col md:flex-row md:gap-8 gap-4'>
                  <div className='flex-1'>
                    <div className='flex flex-col'>
                      <Text size='sm' className='text-black font-bold mb-2'>
                        Take Profit (%)
                      </Text>
                      <Text size='xs' className='text-black font-semibold mb-3'>
                        Percentage to take profits (Recommended: 20-30%)
                      </Text>
                      <div className='relative'>
                        <NumberInput
                          size='md'
                          value={settings.takeProfit}
                          onChange={value =>
                            handleSettingChange('takeProfit', value || 0)
                          }
                          min={0.1}
                          max={100}
                          step={0.1}
                          decimalScale={1}
                          placeholder='25.0'
                          styles={{
                            ...inputStyles,
                            input: {
                              ...inputStyles.input,
                              paddingLeft: '50px',
                              paddingRight: '40px',
                            },
                          }}
                        />
                        <div
                          className='absolute pointer-events-none'
                          style={{ left: '76px', top: '13px' }}
                        >
                          <span className='text-blue-600 font-bold text-sm'>
                            %
                          </span>
                        </div>
                        <div
                          className='absolute left-6 pointer-events-none flex items-center justify-center'
                          style={{ height: '20px', top: '17px' }}
                        >
                          <IconTarget size={20} className='text-blue-600' />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className='flex-1'>
                    <div className='flex flex-col'>
                      <Text size='sm' className='text-black font-bold mb-2'>
                        Max Daily Loss ($)
                      </Text>
                      <Text size='xs' className='text-black font-semibold mb-3'>
                        Maximum to lose per day (Recommended: $25-100)
                      </Text>
                      <div className='relative'>
                        <NumberInput
                          size='md'
                          value={settings.maxDailyLoss}
                          onChange={value =>
                            handleSettingChange('maxDailyLoss', value || 0)
                          }
                          min={1}
                          max={10000}
                          step={1}
                          placeholder='50'
                          styles={{
                            ...inputStyles,
                            input: {
                              ...inputStyles.input,
                              paddingLeft: '50px',
                              paddingRight: '40px',
                            },
                          }}
                        />
                        <div
                          className='absolute pointer-events-none'
                          style={{ left: '76px', top: '13px' }}
                        >
                          <span className='text-red-600 font-bold text-sm'>
                            $
                          </span>
                        </div>
                        <div
                          className='absolute left-6 pointer-events-none flex items-center justify-center'
                          style={{ height: '20px', top: '17px' }}
                        >
                          <IconAlertTriangle
                            size={20}
                            className='text-red-600'
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className='flex flex-col md:flex-row md:gap-8 gap-4'>
                  <div className='flex-1'>
                    <div className='flex flex-col'>
                      <Text size='sm' className='text-black font-bold mb-2'>
                        Position Size ($)
                      </Text>
                      <Text size='xs' className='text-black font-semibold mb-3'>
                        Amount to invest per trade (Recommended: $2-10)
                      </Text>
                      <div className='relative'>
                        <NumberInput
                          size='md'
                          value={settings.positionSize}
                          onChange={value =>
                            handleSettingChange('positionSize', value || 0)
                          }
                          min={1}
                          max={10000}
                          step={1}
                          placeholder='5'
                          styles={{
                            ...inputStyles,
                            input: {
                              ...inputStyles.input,
                              paddingLeft: '50px',
                              paddingRight: '40px',
                            },
                          }}
                        />
                        <div
                          className='absolute pointer-events-none'
                          style={{ left: '76px', top: '13px' }}
                        >
                          <span className='text-green-600 font-bold text-sm'>
                            $
                          </span>
                        </div>
                        <div
                          className='absolute left-6 pointer-events-none flex items-center justify-center'
                          style={{ height: '20px', top: '17px' }}
                        >
                          <IconCalculator
                            size={20}
                            className='text-green-600'
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className='flex-1'>
                    <div className='flex flex-col'>
                      <Text size='sm' className='text-black font-bold mb-2'>
                        Max Concurrent Positions
                      </Text>
                      <Text size='xs' className='text-black font-semibold mb-3'>
                        Maximum number of open positions (Recommended: 2-5)
                      </Text>
                      <div className='relative'>
                        <NumberInput
                          size='md'
                          value={settings.maxConcurrentPositions}
                          onChange={value =>
                            handleSettingChange(
                              'maxConcurrentPositions',
                              value || 0
                            )
                          }
                          min={1}
                          max={20}
                          step={1}
                          placeholder='3'
                          styles={{
                            ...inputStyles,
                            input: {
                              ...inputStyles.input,
                              paddingLeft: '50px',
                              paddingRight: '40px',
                            },
                          }}
                        />
                        <div
                          className='absolute pointer-events-none'
                          style={{ left: '76px', top: '13px' }}
                        >
                          <span className='text-purple-600 font-bold text-sm'>
                            #
                          </span>
                        </div>
                        <div
                          className='absolute left-6 pointer-events-none flex items-center justify-center'
                          style={{ height: '20px', top: '17px' }}
                        >
                          <IconStack size={20} className='text-purple-600' />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Save Button for Trading Section */}
                <div className='flex justify-end pt-6 border-t-2 border-retro-brown-200 mt-6'>
                  <Button
                    onClick={() =>
                      saveSection('trading', {
                        profitTop: settings.profitTop,
                        profitLoss: settings.profitLoss,
                        stopLoss: settings.stopLoss,
                        takeProfit: settings.takeProfit,
                        maxDailyLoss: settings.maxDailyLoss,
                        positionSize: settings.positionSize,
                      })
                    }
                    loading={savingSection === 'trading'}
                    size='lg'
                    className='px-8 py-3 text-base font-bold shadow-lg flex items-center justify-center'
                    styles={{
                      root: {
                        background: 'var(--retro-gold)',
                        color: 'var(--retro-dark)',
                        border: '2px solid var(--retro-gold)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px',
                        '&:hover': {
                          background: 'var(--retro-cream)',
                          color: 'var(--retro-dark)',
                          borderColor: 'var(--retro-cream)',
                          transform: 'translateY(-2px)',
                        },
                      },
                      inner: {
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px',
                      },
                    }}
                    leftSection={<IconDeviceFloppy size={18} />}
                  >
                    Save Trading Parameters
                  </Button>
                </div>
              </Card>

              {/* AI Configuration */}
              <Card className='relative p-6 shadow-xl border-3 border-retro-brown-300 bg-white overflow-hidden rounded-2xl mb-6'>
                {/* Header with icon and title inside card */}
                <div className='flex items-center gap-4 mb-6'>
                  <div className='p-3 rounded-xl bg-white border-2 border-retro-brown-300 shadow-md'>
                    <IconBrain className='text-retro-brown-600' size={24} />
                  </div>
                  <div>
                    <Title
                      order={2}
                      className='text-xl font-bold text-black mb-1'
                    >
                      AI Configuration
                    </Title>
                    <Text size='sm' className='text-black font-semibold'>
                      Configure AI models and analysis parameters
                    </Text>
                  </div>
                </div>

                <Stack gap='lg'>
                  {/* AI Provider Selection */}
                  <div className='flex flex-col'>
                    <Text size='sm' className='text-black font-bold mb-2'>
                      AI Provider
                    </Text>
                    <Text size='xs' className='text-black font-semibold mb-3'>
                      Choose your AI provider (Local AI recommended for
                      microtransactions)
                    </Text>
                    <div className='relative'>
                      <select
                        value={settings.aiProvider || 'local'}
                        onChange={e =>
                          handleSettingChange('aiProvider', e.target.value)
                        }
                        aria-label='Select AI provider'
                        className='w-full px-4 py-3 text-base font-medium border-2 border-retro-brown-300 rounded-xl bg-white shadow-md transition-all duration-200 focus:border-cyan-500 focus:shadow-lg focus:outline-none hover:border-retro-brown-400'
                        style={{
                          fontSize: '15px',
                          fontWeight: 500,
                          color: '#000000',
                          backgroundColor: '#FFFFFF',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                        }}
                      >
                        {aiProviderOptions.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Local AI Status */}
                  {(settings.aiProvider === 'local' ||
                    settings.aiProvider === 'hybrid') && (
                    <div className='flex flex-col'>
                      <Text size='sm' className='text-black font-bold mb-2'>
                        Local AI Status
                      </Text>
                      <Text size='xs' className='text-black font-semibold mb-3'>
                        Local AI models status and configuration
                      </Text>
                      <div className='flex gap-4'>
                        <Button
                          size='md'
                          onClick={() => testLocalAI()}
                          loading={testingConnection}
                          className='px-6 py-3 text-base font-bold shadow-lg flex items-center justify-center'
                          styles={{
                            root: {
                              background: 'var(--retro-turquoise)',
                              color: 'var(--retro-dark)',
                              border: '2px solid var(--retro-turquoise)',
                              borderRadius: '12px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              gap: '8px',
                              '&:hover': {
                                background: 'var(--retro-cream)',
                                color: 'var(--retro-dark)',
                                borderColor: 'var(--retro-cream)',
                                transform: 'translateY(-2px)',
                              },
                            },
                            inner: {
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              gap: '8px',
                            },
                          }}
                          leftSection={<IconTestPipe size={18} />}
                        >
                          Test Local AI
                        </Button>
                        <Button
                          size='md'
                          onClick={() => initializeLocalAI()}
                          className='px-6 py-3 text-base font-bold shadow-lg flex items-center justify-center'
                          styles={{
                            root: {
                              background: 'var(--retro-gold)',
                              color: 'var(--retro-dark)',
                              border: '2px solid var(--retro-gold)',
                              borderRadius: '12px',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              gap: '8px',
                              '&:hover': {
                                background: 'var(--retro-cream)',
                                color: 'var(--retro-dark)',
                                borderColor: 'var(--retro-cream)',
                                transform: 'translateY(-2px)',
                              },
                            },
                            inner: {
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              gap: '8px',
                            },
                          }}
                          leftSection={<IconRefresh size={18} />}
                        >
                          Initialize Models
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* OpenAI API Key (only show if OpenAI or Hybrid is selected) */}
                  {(settings.aiProvider === 'openai' ||
                    settings.aiProvider === 'hybrid') && (
                    <div className='flex flex-col'>
                      <Text size='sm' className='text-black font-bold mb-2'>
                        OpenAI API Key
                      </Text>
                      <Text size='xs' className='text-black font-semibold mb-3'>
                        OpenAI API key for AI analysis (Required for OpenAI
                        provider)
                      </Text>
                      <div className='relative'>
                        <PasswordInput
                          size='md'
                          placeholder='sk-proj-...'
                          value={settings.openaiApiKey}
                          onChange={e =>
                            handleSettingChange(
                              'openaiApiKey',
                              e.currentTarget.value
                            )
                          }
                          visible={showApiKeys}
                          onVisibilityChange={setShowApiKeys}
                          styles={{
                            ...inputStyles,
                            input: {
                              ...inputStyles.input,
                              paddingLeft: '50px',
                              paddingRight: '16px',
                            },
                          }}
                        />
                        <div
                          className='absolute left-6 pointer-events-none flex items-center justify-center'
                          style={{ height: '20px', top: '17px' }}
                        >
                          <IconBrain size={20} className='text-purple-600' />
                        </div>
                      </div>
                    </div>
                  )}

                  <div className='flex flex-col md:flex-row md:gap-8 gap-4'>
                    <div className='flex-1'>
                      <div>
                        <Text size='sm' className='text-black font-bold mb-2'>
                          AI Model
                        </Text>
                        <Text
                          size='xs'
                          className='text-black font-semibold mb-3'
                        >
                          OpenAI model to use for analysis
                        </Text>
                        <div className='relative'>
                          <select
                            value={settings.aiModel}
                            onChange={e =>
                              handleSettingChange('aiModel', e.target.value)
                            }
                            aria-label='Select AI model for analysis'
                            className='w-full px-4 py-3 text-base font-medium border-2 border-retro-brown-300 rounded-xl bg-white shadow-md transition-all duration-200 focus:border-cyan-500 focus:shadow-lg focus:outline-none hover:border-retro-brown-400'
                            style={{
                              fontSize: '15px',
                              fontWeight: 500,
                              color: '#000000',
                              backgroundColor: '#FFFFFF',
                              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                            }}
                          >
                            {aiModelOptions.map(option => (
                              <option key={option.value} value={option.value}>
                                {option.label}
                              </option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>
                    <div className='flex-1'>
                      <div>
                        <Text size='sm' className='text-black font-bold mb-2'>
                          Confidence Threshold
                        </Text>
                        <Text
                          size='xs'
                          className='text-black font-semibold mb-3'
                        >
                          Minimum confidence to execute signals (0.6-0.8
                          recommended)
                        </Text>
                        <div className='relative'>
                          <NumberInput
                            size='md'
                            value={settings.aiConfidenceThreshold}
                            onChange={value =>
                              handleSettingChange(
                                'aiConfidenceThreshold',
                                value || 0
                              )
                            }
                            min={0}
                            max={1}
                            step={0.1}
                            decimalScale={1}
                            placeholder='0.7'
                            styles={{
                              ...inputStyles,
                              input: {
                                ...inputStyles.input,
                                paddingLeft: '50px',
                                paddingRight: '16px',
                              },
                            }}
                          />
                          <div
                            className='absolute left-6 pointer-events-none flex items-center justify-center'
                            style={{ height: '20px', top: '17px' }}
                          >
                            <IconBrain size={20} className='text-purple-600' />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className='flex flex-col md:flex-row md:gap-8 gap-4'>
                    <div className='flex-1'>
                      <div>
                        <Text size='sm' className='text-black font-bold mb-2'>
                          AI Temperature
                        </Text>
                        <Text
                          size='xs'
                          className='text-black font-semibold mb-3'
                        >
                          Model creativity level (0-1, Recommended: 0.1-0.3)
                        </Text>
                        <div className='relative'>
                          <NumberInput
                            size='md'
                            value={settings.aiTemperature}
                            onChange={value =>
                              handleSettingChange('aiTemperature', value || 0)
                            }
                            min={0}
                            max={1}
                            step={0.1}
                            decimalScale={1}
                            placeholder='0.2'
                            styles={{
                              ...inputStyles,
                              input: {
                                ...inputStyles.input,
                                paddingLeft: '50px',
                                paddingRight: '16px',
                              },
                            }}
                          />
                          <div
                            className='absolute left-6 pointer-events-none flex items-center justify-center'
                            style={{ height: '20px', top: '17px' }}
                          >
                            <IconBrain size={20} className='text-orange-600' />
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className='flex-1'>
                      <div>
                        <Text size='sm' className='text-black font-bold mb-2'>
                          Analysis Interval (sec)
                        </Text>
                        <Text
                          size='xs'
                          className='text-black font-semibold mb-3'
                        >
                          Market analysis frequency (Recommended: 30-120 sec)
                        </Text>
                        <div className='relative'>
                          <NumberInput
                            size='md'
                            value={settings.aiAnalysisInterval}
                            onChange={value =>
                              handleSettingChange(
                                'aiAnalysisInterval',
                                value || 0
                              )
                            }
                            min={10}
                            max={300}
                            step={5}
                            placeholder='60'
                            styles={{
                              ...inputStyles,
                              input: {
                                ...inputStyles.input,
                                paddingLeft: '50px',
                                paddingRight: '40px',
                              },
                            }}
                          />
                          <div
                            className='absolute pointer-events-none'
                            style={{ left: '76px', top: '13px' }}
                          >
                            <span className='text-blue-600 font-bold text-sm'>
                              sec
                            </span>
                          </div>
                          <div
                            className='absolute left-6 pointer-events-none flex items-center justify-center'
                            style={{ height: '20px', top: '17px' }}
                          >
                            <IconRefresh size={20} className='text-blue-600' />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className='flex flex-col md:flex-row md:gap-8 gap-4'>
                    <div className='flex-1'>
                      <div className='flex flex-col'>
                        <Text size='sm' className='text-black font-bold mb-2'>
                          LangChain API Key
                        </Text>
                        <Text
                          size='xs'
                          className='text-black font-semibold mb-3'
                        >
                          LangChain API key for advanced features
                        </Text>
                        <div className='relative'>
                          <TextInput
                            size='md'
                            value={settings.langchainApiKey}
                            onChange={e =>
                              handleSettingChange(
                                'langchainApiKey',
                                e.currentTarget.value
                              )
                            }
                            type={showApiKeys ? 'text' : 'password'}
                            placeholder='lsv2_pt_...'
                            styles={{
                              ...inputStyles,
                              input: {
                                ...inputStyles.input,
                                paddingLeft: '50px',
                                paddingRight: '16px',
                              },
                            }}
                          />
                          <div
                            className='absolute left-6 pointer-events-none flex items-center justify-center'
                            style={{ height: '20px', top: '17px' }}
                          >
                            <IconKey size={20} className='text-emerald-600' />
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className='flex-1'>
                      <div className='flex flex-col'>
                        <Text size='sm' className='text-black font-bold mb-2'>
                          LangSmith Project
                        </Text>
                        <Text
                          size='xs'
                          className='text-black font-semibold mb-3'
                        >
                          Project name in LangSmith for tracking
                        </Text>
                        <div className='relative'>
                          <TextInput
                            size='md'
                            value={settings.langsmithProject}
                            onChange={e =>
                              handleSettingChange(
                                'langsmithProject',
                                e.currentTarget.value
                              )
                            }
                            placeholder='deriv-trading'
                            styles={{
                              ...inputStyles,
                              input: {
                                ...inputStyles.input,
                                paddingLeft: '50px',
                                paddingRight: '16px',
                              },
                            }}
                          />
                          <div
                            className='absolute left-6 pointer-events-none flex items-center justify-center'
                            style={{ height: '20px', top: '17px' }}
                          >
                            <IconDatabase
                              size={20}
                              className='text-amber-600'
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Save Button for AI Section */}
                  <div className='flex justify-end pt-6 border-t-2 border-retro-brown-200 mt-6'>
                    <Button
                      onClick={() =>
                        saveSection('ai', {
                          openaiApiKey: settings.openaiApiKey,
                          langchainApiKey: settings.langchainApiKey,
                          langsmithProject: settings.langsmithProject,
                          aiModel: settings.aiModel,
                          aiConfidenceThreshold: settings.aiConfidenceThreshold,
                          aiTemperature: settings.aiTemperature,
                          aiAnalysisInterval: settings.aiAnalysisInterval,
                          aiMaxTokens: settings.aiMaxTokens,
                        })
                      }
                      loading={savingSection === 'ai'}
                      size='lg'
                      className='px-8 py-3 text-base font-bold shadow-lg flex items-center justify-center'
                      styles={{
                        root: {
                          background: 'var(--retro-coral)',
                          color: 'var(--retro-cream)',
                          border: '2px solid var(--retro-coral)',
                          borderRadius: '12px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px',
                          '&:hover': {
                            background: 'var(--retro-red)',
                            color: 'var(--retro-cream)',
                            borderColor: 'var(--retro-red)',
                            transform: 'translateY(-2px)',
                          },
                        },
                        inner: {
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px',
                        },
                      }}
                      leftSection={<IconDeviceFloppy size={18} />}
                    >
                      Save AI Configuration
                    </Button>
                  </div>
                </Stack>
              </Card>

              {/* Risk Management */}
              <Card className='relative p-6 shadow-xl border-3 border-retro-brown-300 bg-white overflow-hidden rounded-2xl mb-6'>
                {/* Header with icon and title inside card */}
                <div className='flex items-center gap-4 mb-6'>
                  <div className='p-3 rounded-xl bg-white border-2 border-retro-brown-300 shadow-md'>
                    <IconShield className='text-retro-brown-600' size={24} />
                  </div>
                  <div>
                    <Title
                      order={2}
                      className='text-xl font-bold text-black mb-1'
                    >
                      Risk Management
                    </Title>
                    <Text size='sm' className='text-black font-semibold'>
                      Configure automatic risk control features
                    </Text>
                  </div>
                </div>

                <div className='flex flex-col md:flex-row md:gap-8 gap-4'>
                  <div className='flex-1'>
                    <div className='p-4 rounded-xl border-2 border-retro-brown-300 bg-white shadow-md'>
                      <Switch
                        size='md'
                        label='Automatic Stop Loss'
                        description='Enable automatic stop loss protection'
                        checked={settings.autoStopLossEnabled}
                        onChange={e =>
                          handleSettingChange(
                            'autoStopLossEnabled',
                            e.currentTarget.checked
                          )
                        }
                        styles={{
                          label: {
                            fontSize: '16px',
                            fontWeight: 600,
                            color: '#8B4513',
                            marginBottom: '4px',
                          },
                          description: { fontSize: '14px', color: '#A0522D' },
                        }}
                      />
                    </div>
                  </div>
                  <div className='flex-1'>
                    <div className='p-4 rounded-xl border-2 border-retro-brown-300 bg-white shadow-md'>
                      <Switch
                        size='md'
                        label='Automatic Take Profit'
                        description='Enable automatic take profit protection'
                        checked={settings.autoTakeProfitEnabled}
                        onChange={e =>
                          handleSettingChange(
                            'autoTakeProfitEnabled',
                            e.currentTarget.checked
                          )
                        }
                        styles={{
                          label: {
                            fontSize: '16px',
                            fontWeight: 600,
                            color: '#8B4513',
                            marginBottom: '4px',
                          },
                          description: { fontSize: '14px', color: '#A0522D' },
                        }}
                      />
                    </div>
                  </div>
                </div>

                <div className='flex flex-col md:flex-row md:gap-8 gap-4'>
                  <div className='flex-1'>
                    <div className='p-4 rounded-xl border-2 border-retro-brown-300 bg-white shadow-md'>
                      <Switch
                        size='md'
                        label='Emergency Stop'
                        description='Stop all trading in case of emergency'
                        checked={settings.emergencyStopEnabled}
                        onChange={e =>
                          handleSettingChange(
                            'emergencyStopEnabled',
                            e.currentTarget.checked
                          )
                        }
                        styles={{
                          label: {
                            fontSize: '16px',
                            fontWeight: 600,
                            color: '#8B4513',
                            marginBottom: '4px',
                          },
                          description: { fontSize: '14px', color: '#A0522D' },
                        }}
                      />
                    </div>
                  </div>
                  <div className='flex-1'>
                    <div className='p-4 rounded-xl border-2 border-retro-brown-300 bg-white shadow-md'>
                      <Switch
                        size='md'
                        label='Circuit Breaker'
                        description='Stop trading automatically if limits are reached'
                        checked={settings.circuitBreakerEnabled}
                        onChange={e =>
                          handleSettingChange(
                            'circuitBreakerEnabled',
                            e.currentTarget.checked
                          )
                        }
                        styles={{
                          label: {
                            fontSize: '16px',
                            fontWeight: 600,
                            color: '#8B4513',
                            marginBottom: '4px',
                          },
                          description: { fontSize: '14px', color: '#A0522D' },
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Save Button for Risk Management Section */}
                <div className='flex justify-end pt-6 border-t-2 border-retro-brown-200'>
                  <Button
                    onClick={() =>
                      saveSection('risk', {
                        autoStopLossEnabled: settings.autoStopLossEnabled,
                        autoTakeProfitEnabled: settings.autoTakeProfitEnabled,
                        emergencyStopEnabled: settings.emergencyStopEnabled,
                        circuitBreakerEnabled: settings.circuitBreakerEnabled,
                      })
                    }
                    loading={savingSection === 'risk'}
                    size='lg'
                    className='px-8 py-3 text-base font-bold shadow-lg flex items-center justify-center'
                    leftSection={<IconDeviceFloppy size={18} />}
                    styles={{
                      root: {
                        background: 'var(--retro-red)',
                        color: 'var(--retro-cream)',
                        border: '2px solid var(--retro-red)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px',
                        '&:hover': {
                          background: 'var(--retro-coral)',
                          color: 'var(--retro-cream)',
                          borderColor: 'var(--retro-coral)',
                          transform: 'translateY(-2px)',
                        },
                      },
                      inner: {
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px',
                      },
                    }}
                  >
                    Save Risk Settings
                  </Button>
                </div>
              </Card>

              {/* Automation Settings */}
              <Card className='relative p-6 shadow-xl border-3 border-retro-brown-300 bg-white overflow-hidden rounded-2xl mb-6'>
                {/* Header with icon and title inside card */}
                <div className='flex items-center gap-4 mb-6'>
                  <div className='p-3 rounded-xl bg-white border-2 border-retro-brown-300 shadow-md'>
                    <IconRobot className='text-retro-brown-600' size={24} />
                  </div>
                  <div>
                    <Title
                      order={2}
                      className='text-xl font-bold text-black mb-1'
                    >
                      Automation Settings
                    </Title>
                    <Text size='sm' className='text-black font-semibold'>
                      Configure automated trading behavior
                    </Text>
                  </div>
                </div>

                <Stack gap='lg'>
                  <div className='p-6 rounded-xl border-2 border-retro-brown-300 bg-white shadow-md'>
                    <Switch
                      label='Automatic Trading'
                      description='Enable fully automatic trading (Use with caution!)'
                      checked={settings.autoTradingEnabled}
                      onChange={e =>
                        handleSettingChange(
                          'autoTradingEnabled',
                          e.currentTarget.checked
                        )
                      }
                      size='lg'
                      color='orange'
                      styles={{
                        label: {
                          fontSize: '18px',
                          fontWeight: 700,
                          color: '#ea580c',
                          marginBottom: '6px',
                        },
                        description: {
                          fontSize: '14px',
                          color: '#c2410c',
                          fontWeight: 500,
                        },
                      }}
                    />
                  </div>

                  <div className='flex flex-col md:flex-row md:gap-8 gap-4'>
                    <div className='flex-1'>
                      <div>
                        <Text size='sm' className='text-black font-bold mb-2'>
                          Market Scan Interval (sec)
                        </Text>
                        <Text
                          size='xs'
                          className='text-black font-semibold mb-3'
                        >
                          Market scanning frequency (30-90 sec recommended)
                        </Text>
                        <div className='relative'>
                          <NumberInput
                            size='md'
                            value={settings.marketScanInterval}
                            onChange={value =>
                              handleSettingChange(
                                'marketScanInterval',
                                value || 0
                              )
                            }
                            min={5}
                            max={300}
                            step={5}
                            placeholder='45'
                            styles={{
                              ...inputStyles,
                              input: {
                                ...inputStyles.input,
                                paddingLeft: '50px',
                                paddingRight: '40px',
                              },
                            }}
                          />
                          <div
                            className='absolute pointer-events-none'
                            style={{ left: '76px', top: '13px' }}
                          >
                            <span className='text-yellow-600 font-bold text-sm'>
                              sec
                            </span>
                          </div>
                          <div
                            className='absolute left-6 pointer-events-none flex items-center justify-center'
                            style={{ height: '20px', top: '17px' }}
                          >
                            <IconRefresh
                              size={20}
                              className='text-yellow-600'
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className='flex-1'>
                      <div>
                        <Text size='sm' className='text-black font-bold mb-2'>
                          Position Monitor Interval (sec)
                        </Text>
                        <Text
                          size='xs'
                          className='text-black font-semibold mb-3'
                        >
                          Position monitoring frequency (10-30 sec recommended)
                        </Text>
                        <div className='relative'>
                          <NumberInput
                            size='md'
                            value={settings.positionMonitorInterval}
                            onChange={value =>
                              handleSettingChange(
                                'positionMonitorInterval',
                                value || 0
                              )
                            }
                            min={1}
                            max={60}
                            step={1}
                            placeholder='15'
                            styles={{
                              ...inputStyles,
                              input: {
                                ...inputStyles.input,
                                paddingLeft: '50px',
                                paddingRight: '40px',
                              },
                            }}
                          />
                          <div
                            className='absolute pointer-events-none'
                            style={{ left: '76px', top: '13px' }}
                          >
                            <span className='text-orange-600 font-bold text-sm'>
                              sec
                            </span>
                          </div>
                          <div
                            className='absolute left-6 pointer-events-none flex items-center justify-center'
                            style={{ height: '20px', top: '17px' }}
                          >
                            <IconSettings
                              size={20}
                              className='text-orange-600'
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className='flex flex-col md:flex-row md:gap-8 gap-4'>
                    <div className='flex-1'>
                      <div className='flex flex-col'>
                        <Text size='sm' className='text-black font-bold mb-2'>
                          Signal Execution Delay (sec)
                        </Text>
                        <Text
                          size='xs'
                          className='text-black font-semibold mb-3'
                        >
                          Delay before executing signals (2-10 sec recommended)
                        </Text>
                        <div className='relative'>
                          <NumberInput
                            size='md'
                            value={settings.signalExecutionDelay}
                            onChange={value =>
                              handleSettingChange(
                                'signalExecutionDelay',
                                value || 0
                              )
                            }
                            min={0}
                            max={30}
                            step={1}
                            placeholder='3'
                            styles={{
                              ...inputStyles,
                              input: {
                                ...inputStyles.input,
                                paddingLeft: '50px',
                                paddingRight: '40px',
                              },
                            }}
                          />
                          <div
                            className='absolute pointer-events-none'
                            style={{ left: '76px', top: '13px' }}
                          >
                            <span className='text-indigo-600 font-bold text-sm'>
                              sec
                            </span>
                          </div>
                          <div
                            className='absolute left-6 pointer-events-none flex items-center justify-center'
                            style={{ height: '20px', top: '17px' }}
                          >
                            <IconSettings
                              size={20}
                              className='text-indigo-600'
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className='flex-1'>
                      <div className='flex flex-col'>
                        <Text size='sm' className='text-black font-bold mb-2'>
                          Historical Data Days
                        </Text>
                        <Text
                          size='xs'
                          className='text-black font-semibold mb-3'
                        >
                          Days of historical data for analysis (7-30
                          recommended)
                        </Text>
                        <div className='relative'>
                          <NumberInput
                            size='md'
                            value={settings.learningDataLookbackDays}
                            onChange={value =>
                              handleSettingChange(
                                'learningDataLookbackDays',
                                value || 0
                              )
                            }
                            min={1}
                            max={365}
                            step={1}
                            placeholder='14'
                            styles={{
                              ...inputStyles,
                              input: {
                                ...inputStyles.input,
                                paddingLeft: '50px',
                                paddingRight: '40px',
                              },
                            }}
                          />
                          <div
                            className='absolute pointer-events-none'
                            style={{ left: '76px', top: '13px' }}
                          >
                            <span className='text-teal-600 font-bold text-sm'>
                              days
                            </span>
                          </div>
                          <div
                            className='absolute left-6 pointer-events-none flex items-center justify-center'
                            style={{ height: '20px', top: '17px' }}
                          >
                            <IconDatabase size={20} className='text-teal-600' />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Save Button for Automation Section */}
                  <div className='flex justify-end pt-6 border-t-2 border-retro-brown-200'>
                    <Button
                      onClick={() =>
                        saveSection('automation', {
                          autoTradingEnabled: settings.autoTradingEnabled,
                          marketScanInterval: settings.marketScanInterval,
                          positionMonitorInterval:
                            settings.positionMonitorInterval,
                          signalExecutionDelay: settings.signalExecutionDelay,
                          maxConcurrentPositions:
                            settings.maxConcurrentPositions,
                          learningDataLookbackDays:
                            settings.learningDataLookbackDays,
                          enabled: settings.autoTradingEnabled,
                          profitTarget: settings.profitTop,
                          stopLoss: settings.stopLoss,
                          maxDailyLoss: settings.maxDailyLoss,
                          maxPositions: settings.maxConcurrentPositions,
                          riskLevel: 'medium',
                          symbols: ['R_10', 'R_25', 'R_50', 'R_75', 'R_100'],
                        })
                      }
                      loading={savingSection === 'automation'}
                      size='lg'
                      className='px-8 py-3 text-base font-bold shadow-lg flex items-center justify-center'
                      leftSection={<IconDeviceFloppy size={18} />}
                      styles={{
                        root: {
                          background: 'var(--retro-brown)',
                          color: 'var(--retro-cream)',
                          border: '2px solid var(--retro-brown)',
                          borderRadius: '12px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px',
                          '&:hover': {
                            background: 'var(--retro-dark)',
                            color: 'var(--retro-cream)',
                            borderColor: 'var(--retro-dark)',
                            transform: 'translateY(-2px)',
                          },
                        },
                        inner: {
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px',
                        },
                      }}
                    >
                      Save Automation Settings
                    </Button>
                  </div>
                </Stack>
              </Card>
            </Stack>
          </Grid.Col>

          {/* Sidebar with actions */}
          <Grid.Col span={{ base: 12, lg: 4 }}>
            <div className='flex flex-col lg:flex-row gap-6'>
              {/* Actions Column */}
              <div className='flex-1'>
                <Card className='card p-6 shadow-lg border-2 border-retro-brown-200 rounded-2xl bg-white'>
                  <div className='text-center mb-4'>
                    <Title
                      order={3}
                      className='text-lg font-bold text-retro-brown-800 mb-2'
                    >
                      Actions
                    </Title>
                    <Text size='sm' className='text-retro-brown-600'>
                      Save and test your configuration
                    </Text>
                  </div>

                  <Stack gap='md'>
                    <Button
                      onClick={saveSettings}
                      loading={saving}
                      disabled={!unsavedChanges}
                      size='md'
                      className='w-full py-3 text-base font-semibold flex items-center justify-center'
                      leftSection={<IconDeviceFloppy size={18} />}
                      styles={{
                        root: {
                          background: unsavedChanges
                            ? 'var(--retro-turquoise)'
                            : 'var(--retro-brown)',
                          color: 'var(--retro-dark)',
                          border: '2px solid var(--retro-turquoise)',
                          borderRadius: '12px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px',
                          '&:hover': {
                            background: unsavedChanges
                              ? 'var(--retro-cream)'
                              : 'var(--retro-brown)',
                            color: 'var(--retro-dark)',
                            borderColor: 'var(--retro-cream)',
                            transform: 'translateY(-2px)',
                          },
                        },
                        inner: {
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px',
                        },
                      }}
                    >
                      Save Configuration
                    </Button>

                    <Button
                      variant='outline'
                      onClick={testDerivConnection}
                      loading={testingConnection}
                      disabled={!settings.derivToken}
                      size='md'
                      className='w-full py-2 font-semibold border-2 flex items-center justify-center'
                      leftSection={<IconTestPipe size={16} />}
                      styles={{
                        root: {
                          borderColor: 'var(--retro-turquoise)',
                          color: 'var(--retro-turquoise)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          '&:hover': {
                            backgroundColor: 'var(--retro-cream)',
                            color: 'var(--retro-dark)',
                            borderColor: 'var(--retro-turquoise)',
                          },
                        },
                        inner: {
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px',
                        },
                      }}
                    >
                      Test Deriv Connection
                    </Button>

                    <Button
                      variant='light'
                      color='orange'
                      onClick={resetToDefaults}
                      size='md'
                      className='w-full py-2 font-semibold flex items-center justify-center bg-white'
                      leftSection={<IconRefresh size={16} />}
                      styles={{
                        root: {
                          backgroundColor: 'white',
                          color: '#ea580c',
                          borderColor: '#ea580c',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          '&:hover': { backgroundColor: '#f8f9fa' },
                        },
                        inner: {
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px',
                        },
                      }}
                    >
                      Reset to Defaults
                    </Button>
                  </Stack>
                </Card>
              </div>

              {/* System Status Column */}
              <div className='flex-1'>
                <Card className='card p-6 shadow-lg border-2 border-retro-brown-200 rounded-2xl bg-white'>
                  <Title
                    order={4}
                    className='text-lg font-bold text-retro-brown-800 mb-4'
                  >
                    System Status
                  </Title>
                  <Stack gap='sm'>
                    <Group
                      justify='space-between'
                      className='p-2 rounded-lg bg-white border border-retro-brown-200'
                    >
                      <Text
                        size='xs'
                        className='font-semibold text-retro-brown-700'
                      >
                        Deriv API
                      </Text>
                      <Badge
                        color={
                          connectionStatus === 'success' ? 'green' : 'gray'
                        }
                        size='sm'
                        variant='filled'
                      >
                        {connectionStatus === 'success'
                          ? 'Connected'
                          : 'Not configured'}
                      </Badge>
                    </Group>
                    <Group
                      justify='space-between'
                      className='p-2 rounded-lg bg-white border border-retro-brown-200'
                    >
                      <Text
                        size='xs'
                        className='font-semibold text-retro-brown-700'
                      >
                        OpenAI API
                      </Text>
                      <Badge
                        color={settings.openaiApiKey ? 'green' : 'gray'}
                        size='sm'
                        variant='filled'
                      >
                        {settings.openaiApiKey
                          ? 'Configured'
                          : 'Not configured'}
                      </Badge>
                    </Group>
                    <Group
                      justify='space-between'
                      className='p-2 rounded-lg bg-white border border-retro-brown-200'
                    >
                      <Text
                        size='xs'
                        className='font-semibold text-retro-brown-700'
                      >
                        Auto Trading
                      </Text>
                      <Badge
                        color={settings.autoTradingEnabled ? 'orange' : 'gray'}
                        size='sm'
                        variant='filled'
                      >
                        {settings.autoTradingEnabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                    </Group>
                  </Stack>
                </Card>
              </div>

              {/* Info Alert Column */}
              <div className='flex-1'>
                <Alert
                  icon={<IconInfoCircle size={16} />}
                  color='blue'
                  className='p-4 rounded-xl border-2 border-blue-200 bg-white h-full'
                  styles={{
                    root: { backgroundColor: 'white' },
                    message: { fontSize: '13px', lineHeight: '1.4' },
                  }}
                >
                  <Text size='xs' className='font-medium'>
                    Make sure to configure all parameters correctly before
                    enabling automatic trading.
                  </Text>
                </Alert>
              </div>
            </div>
          </Grid.Col>
        </Grid>
      </div>
    </Layout>
  );
}
