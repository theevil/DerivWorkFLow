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
} from '@tabler/icons-react';
import { Layout } from '../components/Layout';
import { notifications } from '@mantine/notifications';
import { api } from '../lib/api';

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
  profitTop: 15.0,          // Conservative profit target (10-20% range)
  profitLoss: 3.0,          // Small loss tolerance (2-5% range)
  stopLoss: 10.0,           // Moderate stop loss (5-15% range)
  takeProfit: 25.0,         // Good profit target (20-30% range)
  maxDailyLoss: 50.0,       // Daily loss limit ($25-100 range)
  positionSize: 5.0,        // Conservative position size ($2-10 range)
  aiConfidenceThreshold: 0.7, // High confidence threshold (0.6-0.8 range)
  aiAnalysisInterval: 60,   // 1 minute analysis (30-120 sec range)
  maxPositionsPerUser: 3,   // Conservative concurrent positions (2-5 range)
  aiModel: 'gpt-4o-mini',
  aiTemperature: 0.2,       // Low creativity for trading (0.1-0.3 range)
  aiMaxTokens: 1000,
  openaiApiKey: '',
  langchainApiKey: '',
  langsmithProject: 'deriv-trading',
  autoStopLossEnabled: true,
  autoTakeProfitEnabled: true,
  emergencyStopEnabled: true,
  circuitBreakerEnabled: true,
  autoTradingEnabled: false,
  marketScanInterval: 45,   // Moderate scanning (30-90 sec range)
  positionMonitorInterval: 15, // Regular monitoring (10-30 sec range)
  signalExecutionDelay: 3,  // Quick execution (2-10 sec range)
  maxConcurrentPositions: 3, // Conservative limit (2-5 range)
  learningDataLookbackDays: 14, // 2 weeks lookback (7-30 days range)
  minTrainingSamples: 150,  // Adequate training data (100-300 range)
  modelRetrainIntervalHours: 24, // Daily retraining (12-48 hours range)
};

const aiModelOptions = [
  { value: 'gpt-4o-mini', label: 'GPT-4o Mini (Recommended)' },
  { value: 'gpt-4o', label: 'GPT-4o' },
  { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
  { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
];

// Common input styles for consistency
const inputStyles = {
  label: { 
    fontSize: '16px', 
    fontWeight: 700, 
    color: '#2D1B0E', 
    marginBottom: '8px',
    textShadow: 'none'
  },
  description: { 
    fontSize: '14px', 
    color: '#5D4037', 
    marginBottom: '10px',
    fontWeight: 500
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
    color: '#2D1B0E',
    '&::placeholder': {
      color: '#8D6E63',
      fontSize: '14px',
      fontWeight: 400,
      opacity: 0.8
    },
    '&:focus': { 
      borderColor: '#00BCD4',
      backgroundColor: '#FFFFFF',
      boxShadow: '0 4px 12px rgba(0, 188, 212, 0.2)',
      outline: 'none'
    },
    '&:hover': {
      borderColor: '#6D4C41',
      backgroundColor: '#FAFAFA'
    }
  }
};

export function SettingsPage() {
  const [settings, setSettings] = useState<UserSettings>(defaultSettings);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savingSection, setSavingSection] = useState<string | null>(null);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'success' | 'error' | null>(null);
  const [showApiKeys, setShowApiKeys] = useState(false);
  const [unsavedChanges, setUnsavedChanges] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      // Load user trading parameters
      const tradingParams = await api.get('/trading/parameters');
      
      // Load user profile data
      const userProfile = await api.get('/auth/me');
      
      // Merge with default settings
      setSettings(prev => ({
        ...prev,
        derivToken: userProfile.data.derivToken || '',
        profitTop: tradingParams.data?.profitTop || prev.profitTop,
        profitLoss: tradingParams.data?.profitLoss || prev.profitLoss,
        stopLoss: tradingParams.data?.stopLoss || prev.stopLoss,
        takeProfit: tradingParams.data?.takeProfit || prev.takeProfit,
        maxDailyLoss: tradingParams.data?.maxDailyLoss || prev.maxDailyLoss,
        positionSize: tradingParams.data?.positionSize || prev.positionSize,
      }));
    } catch (error) {
      console.error('Error loading settings:', error);
      notifications.show({
        title: 'Error',
        message: 'Failed to load settings',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setLoading(false);
    }
  };

  const saveSection = async (sectionName: string, sectionData: any) => {
    setSavingSection(sectionName);
    try {
      if (sectionName === 'deriv' && sectionData.derivToken) {
        await api.post('/deriv/token', { token: sectionData.derivToken });
      }

      if (sectionName === 'trading') {
        await api.post('/trading/parameters', sectionData);
      }

      if (sectionName === 'automation') {
        await api.post('/automation/configure', sectionData);
      }

      if (sectionName === 'ai' || sectionName === 'risk') {
        // Save via settings endpoint
        await api.put('/settings/settings', sectionData);
      }

      notifications.show({
        title: 'Section Saved',
        message: `${sectionName} settings have been saved successfully`,
        color: 'green',
        icon: <IconCheck size={16} />,
      });
    } catch (error: any) {
      console.error(`Error saving ${sectionName} settings:`, error);
      notifications.show({
        title: 'Save Error',
        message: error.response?.data?.detail || `Failed to save ${sectionName} settings`,
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setSavingSection(null);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      // Save Deriv token
      if (settings.derivToken) {
        await api.post('/deriv/token', { token: settings.derivToken });
      }

      // Save trading parameters
      await api.post('/trading/parameters', {
        profitTop: settings.profitTop,
        profitLoss: settings.profitLoss,
        stopLoss: settings.stopLoss,
        takeProfit: settings.takeProfit,
        maxDailyLoss: settings.maxDailyLoss,
        positionSize: settings.positionSize,
      });

      // Save automation configuration
      await api.post('/automation/configure', {
        enabled: settings.autoTradingEnabled,
        profitTarget: settings.profitTop,
        stopLoss: settings.stopLoss,
        maxDailyLoss: settings.maxDailyLoss,
        maxPositions: settings.maxConcurrentPositions,
        riskLevel: 'medium',
        symbols: ['R_10', 'R_25', 'R_50', 'R_75', 'R_100'],
      });

      setUnsavedChanges(false);
      notifications.show({
        title: 'Settings Saved',
        message: 'All settings have been saved successfully',
        color: 'green',
        icon: <IconCheck size={16} />,
      });
    } catch (error: any) {
      console.error('Error saving settings:', error);
      notifications.show({
        title: 'Save Error',
        message: error.response?.data?.detail || 'Failed to save settings',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setSaving(false);
    }
  };

  const testDerivConnection = async () => {
    if (!settings.derivToken) {
      notifications.show({
        title: 'Token Required',
        message: 'Please enter your Deriv API token',
        color: 'orange',
        icon: <IconAlertTriangle size={16} />,
      });
      return;
    }

    setTestingConnection(true);
    setConnectionStatus(null);
    
    try {
      await api.post('/deriv/token', { token: settings.derivToken });
      setConnectionStatus('success');
      notifications.show({
        title: 'Connection Successful',
        message: 'Deriv API token is valid',
        color: 'green',
        icon: <IconCheck size={16} />,
      });
    } catch (error: any) {
      setConnectionStatus('error');
      notifications.show({
        title: 'Connection Error',
        message: error.response?.data?.detail || 'Invalid Deriv API token',
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

  const resetToDefaults = () => {
    setSettings(defaultSettings);
    setUnsavedChanges(true);
    notifications.show({
      title: 'Settings Reset',
      message: 'Default values have been restored',
      color: 'blue',
      icon: <IconRefresh size={16} />,
    });
  };

  return (
    <Layout>
      <div className="p-8 max-w-7xl mx-auto">
        <div className="mb-8">
          <Title order={1} className="text-4xl font-bold text-retro-brown-800 mb-3">
            Bot Configuration
          </Title>
          <Text size="lg" className="text-retro-brown-600 leading-relaxed">
            Configure all necessary parameters for optimal trading bot performance. Adjust settings carefully based on your risk tolerance and trading strategy.
          </Text>
        </div>

        {unsavedChanges && (
          <Alert
            icon={<IconAlertTriangle size={18} />}
            title="Unsaved Changes"
            color="orange"
            className="mb-6 p-4 rounded-xl border-2 border-orange-200"
            styles={{
              root: { backgroundColor: 'rgba(255, 165, 0, 0.1)' },
              title: { fontSize: '16px', fontWeight: 600 },
              message: { fontSize: '14px' }
            }}
          >
            You have unsaved changes. Don't forget to save your configuration.
          </Alert>
        )}

        <Grid>
          <Grid.Col span={{ base: 12, lg: 8 }}>
            <Stack gap={80}>
              {/* Deriv API Configuration */}
              <Card className="relative p-0 shadow-xl border-3 border-retro-brown-300 bg-gradient-to-br from-white to-retro-cream-50 overflow-hidden">
                {/* Header with icon and title inside card */}
                <div className="relative p-6 bg-gradient-to-r from-retro-coral-100 to-retro-coral-50 border-b-3 border-retro-brown-200">
                  <Group justify="space-between" align="center">
                    <Group gap="lg" align="center">
                      <div className="p-4 rounded-2xl bg-retro-coral-200 border-3 border-retro-coral-400 shadow-lg">
                        <IconKey className="text-retro-coral-700" size={32} />
                      </div>
                      <div>
                        <Title order={2} className="text-2xl font-bold text-retro-brown-800 mb-1">
                          Deriv API Configuration
                        </Title>
                        <Text size="md" className="text-retro-brown-600 font-medium">
                          Connect your Deriv account for live trading
                        </Text>
                      </div>
                    </Group>
                    {connectionStatus && (
                      <Badge 
                        size="xl"
                        color={connectionStatus === 'success' ? 'green' : 'red'}
                        variant="filled"
                        className="px-6 py-3 text-base font-bold shadow-lg"
                        radius="xl"
                      >
                        {connectionStatus === 'success' ? '✓ Connected' : '✗ Error'}
                      </Badge>
                    )}
                  </Group>
                </div>
                
                {/* Content area */}
                <div className="p-8">

                <Stack gap="xl">
                  <TextInput
                    size="md"
                    label="Deriv App ID"
                    description="Application ID registered in Deriv (default: 1089)"
                    placeholder="1089"
                    value={settings.derivAppId}
                    onChange={(e) => handleSettingChange('derivAppId', e.currentTarget.value)}
                    leftSection={<IconDatabase size={16} className="text-cyan-600" />}
                    styles={{
                      ...inputStyles,
                      input: { 
                        ...inputStyles.input,
                        paddingLeft: '40px'
                      }
                    }}
                  />

                  <PasswordInput
                    size="md"
                    label="Deriv API Token"
                    description="Authentication token to connect with Deriv API"
                    placeholder="Enter your Deriv API token (e.g., a1-xxxxxxxxxxxx)"
                    value={settings.derivToken}
                    onChange={(e) => handleSettingChange('derivToken', e.currentTarget.value)}
                    visible={showApiKeys}
                    onVisibilityChange={setShowApiKeys}
                    leftSection={<IconKey size={16} className="text-red-600" />}
                    rightSection={
                      <Tooltip label="Test connection">
                        <ActionIcon
                          variant="filled"
                          color="cyan"
                          size="sm"
                          onClick={testDerivConnection}
                          loading={testingConnection}
                          className="mr-2"
                        >
                          <IconTestPipe size={14} />
                        </ActionIcon>
                      </Tooltip>
                    }
                    styles={{
                      ...inputStyles,
                      input: { 
                        ...inputStyles.input,
                        paddingLeft: '40px',
                        paddingRight: '60px'
                      }
                    }}
                  />

                  <Alert 
                    icon={<IconInfoCircle size={20} />} 
                    color="blue"
                    className="p-5 rounded-xl border-2 border-blue-200"
                    styles={{
                      root: { backgroundColor: 'rgba(59, 130, 246, 0.1)' },
                      message: { fontSize: '14px', lineHeight: '1.6' }
                    }}
                  >
                    <Text size="sm" className="leading-relaxed">
                      <strong className="text-blue-800">How to get your Deriv token:</strong><br />
                      1. Go to your Deriv account<br />
                      2. Navigate to Settings → Security and privacy → API tokens<br />
                      3. Create a new token with trading permissions<br />
                      4. Copy and paste the token here
                    </Text>
                  </Alert>

                  {/* Save Button for Deriv Section */}
                  <div className="flex justify-end pt-6 border-t-3 border-retro-brown-200 bg-retro-cream-50 -mx-8 px-8 py-6 rounded-b-xl">
                    <Button
                      onClick={() => saveSection('deriv', { derivToken: settings.derivToken, derivAppId: settings.derivAppId })}
                      loading={savingSection === 'deriv'}
                      size="xl"
                      className="px-12 py-4 text-lg font-bold shadow-xl"
                      leftSection={<IconCheck size={20} />}
                      gradient={{ from: 'teal', to: 'cyan' }}
                      variant="gradient"
                      radius="xl"
                    >
                      Save Deriv Settings
                    </Button>
                  </div>
                </Stack>
                </div>
              </Card>

              {/* Trading Parameters */}
              <Card className="relative p-0 shadow-xl border-3 border-retro-brown-300 bg-gradient-to-br from-white to-retro-cream-50 overflow-hidden">
                {/* Header with icon and title inside card */}
                <div className="relative p-6 bg-gradient-to-r from-retro-turquoise-100 to-retro-turquoise-50 border-b-3 border-retro-brown-200">
                  <Group gap="lg" align="center">
                    <div className="p-4 rounded-2xl bg-retro-turquoise-200 border-3 border-retro-turquoise-400 shadow-lg">
                      <IconSettings className="text-retro-turquoise-700" size={32} />
                    </div>
                    <div>
                      <Title order={2} className="text-2xl font-bold text-retro-brown-800 mb-1">
                        Trading Parameters
                      </Title>
                      <Text size="md" className="text-retro-brown-600 font-medium">
                        Set your risk management and position sizing rules
                      </Text>
                    </div>
                  </Group>
                </div>
                
                {/* Content area */}
                <div className="p-8">

                <Grid gutter="xl">
                  <Grid.Col span={{ base: 12, sm: 6 }}>
                    <NumberInput
                      size="md"
                      label="Profit Target (%)"
                      description="Target profit percentage (Recommended: 10-20%)"
                      value={settings.profitTop}
                      onChange={(value) => handleSettingChange('profitTop', value || 0)}
                      min={0.1}
                      max={100}
                      step={0.1}
                      decimalScale={1}
                      placeholder="15.0"
                      rightSection={<span className="text-green-600 font-bold text-sm">%</span>}
                      styles={inputStyles}
                    />
                  </Grid.Col>
                  <Grid.Col span={{ base: 12, sm: 6 }}>
                    <NumberInput
                      size="md"
                      label="Stop Loss (%)"
                      description="Maximum loss percentage (Recommended: 5-15%)"
                      value={settings.stopLoss}
                      onChange={(value) => handleSettingChange('stopLoss', value || 0)}
                      min={0.1}
                      max={100}
                      step={0.1}
                      decimalScale={1}
                      placeholder="10.0"
                      rightSection={<span className="text-red-600 font-bold text-sm">%</span>}
                      styles={inputStyles}
                    />
                  </Grid.Col>
                  <Grid.Col span={{ base: 12, sm: 6 }}>
                    <NumberInput
                      size="md"
                      label="Take Profit (%)"
                      description="Percentage to take profits (Recommended: 20-30%)"
                      value={settings.takeProfit}
                      onChange={(value) => handleSettingChange('takeProfit', value || 0)}
                      min={0.1}
                      max={100}
                      step={0.1}
                      decimalScale={1}
                      placeholder="25.0"
                      rightSection={<span className="text-blue-600 font-bold text-sm">%</span>}
                      styles={inputStyles}
                    />
                  </Grid.Col>
                  <Grid.Col span={{ base: 12, sm: 6 }}>
                    <NumberInput
                      size="md"
                      label="Max Daily Loss ($)"
                      description="Maximum to lose per day (Recommended: $25-100)"
                      value={settings.maxDailyLoss}
                      onChange={(value) => handleSettingChange('maxDailyLoss', value || 0)}
                      min={1}
                      max={10000}
                      step={1}
                      placeholder="50"
                      leftSection={<span className="text-red-600 font-bold text-sm">$</span>}
                      styles={{...inputStyles, input: {...inputStyles.input, paddingLeft: '32px'}}}
                    />
                  </Grid.Col>
                  <Grid.Col span={{ base: 12, sm: 6 }}>
                    <NumberInput
                      size="md"
                      label="Position Size ($)"
                      description="Amount to invest per trade (Recommended: $2-10)"
                      value={settings.positionSize}
                      onChange={(value) => handleSettingChange('positionSize', value || 0)}
                      min={1}
                      max={10000}
                      step={1}
                      placeholder="5"
                      leftSection={<span className="text-green-600 font-bold text-sm">$</span>}
                      styles={{...inputStyles, input: {...inputStyles.input, paddingLeft: '32px'}}}
                    />
                  </Grid.Col>
                  <Grid.Col span={{ base: 12, sm: 6 }}>
                    <NumberInput
                      size="md"
                      label="Max Concurrent Positions"
                      description="Maximum number of open positions (Recommended: 2-5)"
                      value={settings.maxConcurrentPositions}
                      onChange={(value) => handleSettingChange('maxConcurrentPositions', value || 0)}
                      min={1}
                      max={20}
                      step={1}
                      placeholder="3"
                      rightSection={<span className="text-purple-600 font-bold text-sm">#</span>}
                      styles={inputStyles}
                    />
                  </Grid.Col>
                </Grid>

                {/* Save Button for Trading Section */}
                <div className="flex justify-end pt-6 border-t-3 border-retro-brown-200 bg-retro-cream-50 -mx-8 px-8 py-6 rounded-b-xl">
                  <Button
                    onClick={() => saveSection('trading', {
                      profitTop: settings.profitTop,
                      profitLoss: settings.profitLoss,
                      stopLoss: settings.stopLoss,
                      takeProfit: settings.takeProfit,
                      maxDailyLoss: settings.maxDailyLoss,
                      positionSize: settings.positionSize,
                    })}
                    loading={savingSection === 'trading'}
                    size="xl"
                    className="px-12 py-4 text-lg font-bold shadow-xl"
                    leftSection={<IconCheck size={20} />}
                    gradient={{ from: 'indigo', to: 'purple' }}
                    variant="gradient"
                    radius="xl"
                  >
                    Save Trading Parameters
                  </Button>
                </div>
                </div>
              </Card>

              {/* AI Configuration */}
              <Card className="relative p-0 shadow-xl border-3 border-retro-brown-300 bg-gradient-to-br from-white to-retro-cream-50 overflow-hidden">
                {/* Header with icon and title inside card */}
                <div className="relative p-6 bg-gradient-to-r from-retro-violet-100 to-retro-violet-50 border-b-3 border-retro-brown-200">
                  <Group gap="lg" align="center">
                    <div className="p-4 rounded-2xl bg-retro-violet-200 border-3 border-retro-violet-400 shadow-lg">
                      <IconBrain className="text-retro-violet-700" size={32} />
                    </div>
                    <div>
                      <Title order={2} className="text-2xl font-bold text-retro-brown-800 mb-1">
                        AI Configuration
                      </Title>
                      <Text size="md" className="text-retro-brown-600 font-medium">
                        Configure AI models and analysis parameters
                      </Text>
                    </div>
                  </Group>
                </div>
                
                {/* Content area */}
                <div className="p-8">

                <Stack gap="lg">
                  <PasswordInput
                    size="md"
                    label="OpenAI API Key"
                    description="OpenAI API key for AI analysis (Required for intelligent trading)"
                    placeholder="sk-proj-..."
                    value={settings.openaiApiKey}
                    onChange={(e) => handleSettingChange('openaiApiKey', e.currentTarget.value)}
                    visible={showApiKeys}
                    onVisibilityChange={setShowApiKeys}
                    leftSection={<IconBrain size={16} className="text-purple-600" />}
                    styles={{
                      ...inputStyles,
                      input: { 
                        ...inputStyles.input,
                        paddingLeft: '40px'
                      }
                    }}
                  />

                  <Grid gutter="xl">
                    <Grid.Col span={{ base: 12, sm: 6 }}>
                      <Select
                        size="md"
                        label="AI Model"
                        description="OpenAI model to use for analysis"
                        data={aiModelOptions}
                        value={settings.aiModel}
                        onChange={(value) => handleSettingChange('aiModel', value || 'gpt-4o-mini')}
                        placeholder="Select AI model"
                        leftSection={<IconBrain size={16} className="text-indigo-600" />}
                        styles={{
                          ...inputStyles,
                          input: { 
                            ...inputStyles.input,
                            paddingLeft: '40px'
                          }
                        }}
                      />
                    </Grid.Col>
                    <Grid.Col span={{ base: 12, sm: 6 }}>
                      <NumberInput
                        size="md"
                        label="Confidence Threshold"
                        description="Minimum confidence to execute signals (0.6-0.8 recommended)"
                        value={settings.aiConfidenceThreshold}
                        onChange={(value) => handleSettingChange('aiConfidenceThreshold', value || 0)}
                        min={0}
                        max={1}
                        step={0.1}
                        decimalScale={1}
                        placeholder="0.7"
                        leftSection={<IconBrain size={16} className="text-orange-600" />}
                        styles={{
                          ...inputStyles,
                          input: { 
                            ...inputStyles.input,
                            paddingLeft: '40px'
                          }
                        }}
                      />
                    </Grid.Col>
                    <Grid.Col span={{ base: 12, sm: 6 }}>
                      <NumberInput
                        label="Temperatura de IA"
                        description="Creatividad del modelo (0-1)"
                        value={settings.aiTemperature}
                        onChange={(value) => handleSettingChange('aiTemperature', value || 0)}
                        min={0}
                        max={1}
                        step={0.1}
                        decimalScale={1}
                      />
                    </Grid.Col>
                    <Grid.Col span={{ base: 12, sm: 6 }}>
                      <NumberInput
                        label="Intervalo de Análisis (seg)"
                        description="Frecuencia de análisis de mercado"
                        value={settings.aiAnalysisInterval}
                        onChange={(value) => handleSettingChange('aiAnalysisInterval', value || 0)}
                        min={10}
                        max={300}
                        step={5}
                      />
                    </Grid.Col>
                  </Grid>

                  <TextInput
                    size="md"
                    label="LangChain API Key"
                    description="LangChain API key for advanced features"
                    value={settings.langchainApiKey}
                    onChange={(e) => handleSettingChange('langchainApiKey', e.currentTarget.value)}
                    type={showApiKeys ? 'text' : 'password'}
                    placeholder="lsv2_pt_..."
                    leftSection={<IconKey size={16} className="text-emerald-600" />}
                    styles={{
                      ...inputStyles,
                      input: { 
                        ...inputStyles.input,
                        paddingLeft: '40px'
                      }
                    }}
                  />

                  <TextInput
                    size="md"
                    label="LangSmith Project"
                    description="Project name in LangSmith for tracking"
                    value={settings.langsmithProject}
                    onChange={(e) => handleSettingChange('langsmithProject', e.currentTarget.value)}
                    placeholder="deriv-trading"
                    leftSection={<IconDatabase size={16} className="text-amber-600" />}
                    styles={{
                      ...inputStyles,
                      input: { 
                        ...inputStyles.input,
                        paddingLeft: '40px'
                      }
                    }}
                  />

                  {/* Save Button for AI Section */}
                  <div className="flex justify-end pt-6 border-t-2 border-retro-brown-200">
                    <Button
                      onClick={() => saveSection('ai', {
                        openaiApiKey: settings.openaiApiKey,
                        langchainApiKey: settings.langchainApiKey,
                        langsmithProject: settings.langsmithProject,
                        aiModel: settings.aiModel,
                        aiConfidenceThreshold: settings.aiConfidenceThreshold,
                        aiTemperature: settings.aiTemperature,
                        aiAnalysisInterval: settings.aiAnalysisInterval,
                        aiMaxTokens: settings.aiMaxTokens,
                      })}
                      loading={savingSection === 'ai'}
                      size="md"
                      className="px-8"
                      leftSection={<IconCheck size={16} />}
                    >
                      Save AI Configuration
                    </Button>
                  </div>
                </Stack>
                </div>
              </Card>

              {/* Risk Management */}
              <Card className="card p-8 shadow-lg border-2 border-retro-brown-200">
                <Group className="mb-6">
                  <div className="p-3 rounded-xl bg-retro-red-100 border-2 border-retro-red-300">
                    <IconShield className="text-retro-red-600" size={28} />
                  </div>
                  <div>
                    <Title order={2} className="text-2xl font-bold text-retro-brown-800 mb-1">
                      Risk Management
                    </Title>
                    <Text size="sm" className="text-retro-brown-600">
                      Configure automatic risk control features
                    </Text>
                  </div>
                </Group>

                <Grid gutter="xl">
                  <Grid.Col span={{ base: 12, sm: 6 }}>
                    <div className="p-4 rounded-xl border-2 border-retro-brown-200 bg-retro-cream-50">
                      <Switch
                        size="md"
                        label="Automatic Stop Loss"
                        description="Enable automatic stop loss protection"
                        checked={settings.autoStopLossEnabled}
                        onChange={(e) => handleSettingChange('autoStopLossEnabled', e.currentTarget.checked)}
                        styles={{
                          label: { fontSize: '16px', fontWeight: 600, color: '#8B4513', marginBottom: '4px' },
                          description: { fontSize: '14px', color: '#A0522D' }
                        }}
                      />
                    </div>
                  </Grid.Col>
                  <Grid.Col span={{ base: 12, sm: 6 }}>
                    <div className="p-4 rounded-xl border-2 border-retro-brown-200 bg-retro-cream-50">
                      <Switch
                        size="md"
                        label="Automatic Take Profit"
                        description="Enable automatic take profit protection"
                        checked={settings.autoTakeProfitEnabled}
                        onChange={(e) => handleSettingChange('autoTakeProfitEnabled', e.currentTarget.checked)}
                        styles={{
                          label: { fontSize: '16px', fontWeight: 600, color: '#8B4513', marginBottom: '4px' },
                          description: { fontSize: '14px', color: '#A0522D' }
                        }}
                      />
                    </div>
                  </Grid.Col>
                  <Grid.Col span={{ base: 12, sm: 6 }}>
                    <div className="p-4 rounded-xl border-2 border-retro-brown-200 bg-retro-cream-50">
                      <Switch
                        size="md"
                        label="Emergency Stop"
                        description="Stop all trading in case of emergency"
                        checked={settings.emergencyStopEnabled}
                        onChange={(e) => handleSettingChange('emergencyStopEnabled', e.currentTarget.checked)}
                        styles={{
                          label: { fontSize: '16px', fontWeight: 600, color: '#8B4513', marginBottom: '4px' },
                          description: { fontSize: '14px', color: '#A0522D' }
                        }}
                      />
                    </div>
                  </Grid.Col>
                  <Grid.Col span={{ base: 12, sm: 6 }}>
                    <div className="p-4 rounded-xl border-2 border-retro-brown-200 bg-retro-cream-50">
                      <Switch
                        size="md"
                        label="Circuit Breaker"
                        description="Stop trading automatically if limits are reached"
                        checked={settings.circuitBreakerEnabled}
                        onChange={(e) => handleSettingChange('circuitBreakerEnabled', e.currentTarget.checked)}
                        styles={{
                          label: { fontSize: '16px', fontWeight: 600, color: '#8B4513', marginBottom: '4px' },
                          description: { fontSize: '14px', color: '#A0522D' }
                        }}
                      />
                    </div>
                  </Grid.Col>
                </Grid>

                {/* Save Button for Risk Management Section */}
                <div className="flex justify-end pt-6 border-t-2 border-retro-brown-200">
                  <Button
                    onClick={() => saveSection('risk', {
                      autoStopLossEnabled: settings.autoStopLossEnabled,
                      autoTakeProfitEnabled: settings.autoTakeProfitEnabled,
                      emergencyStopEnabled: settings.emergencyStopEnabled,
                      circuitBreakerEnabled: settings.circuitBreakerEnabled,
                    })}
                    loading={savingSection === 'risk'}
                    size="md"
                    className="px-8"
                    leftSection={<IconCheck size={16} />}
                  >
                    Save Risk Settings
                  </Button>
                </div>
              </Card>

              {/* Automation Settings */}
              <Card className="card p-8 shadow-lg border-2 border-retro-brown-200">
                <Group className="mb-6">
                  <div className="p-3 rounded-xl bg-retro-yellow-100 border-2 border-retro-yellow-300">
                    <IconRobot className="text-retro-yellow-600" size={28} />
                  </div>
                  <div>
                    <Title order={2} className="text-2xl font-bold text-retro-brown-800 mb-1">
                      Automation Settings
                    </Title>
                    <Text size="sm" className="text-retro-brown-600">
                      Configure automated trading behavior
                    </Text>
                  </div>
                </Group>

                <Stack gap="lg">
                  <div className="p-6 rounded-xl border-2 border-orange-300 bg-orange-50">
                    <Switch
                      label="Automatic Trading"
                      description="Enable fully automatic trading (Use with caution!)"
                      checked={settings.autoTradingEnabled}
                      onChange={(e) => handleSettingChange('autoTradingEnabled', e.currentTarget.checked)}
                      size="lg"
                      color="orange"
                      styles={{
                        label: { fontSize: '18px', fontWeight: 700, color: '#ea580c', marginBottom: '6px' },
                        description: { fontSize: '14px', color: '#c2410c', fontWeight: 500 }
                      }}
                    />
                  </div>

                  <Grid>
                    <Grid.Col span={{ base: 12, sm: 6 }}>
                      <NumberInput
                        size="md"
                        label="Market Scan Interval (sec)"
                        description="Market scanning frequency (30-90 sec recommended)"
                        value={settings.marketScanInterval}
                        onChange={(value) => handleSettingChange('marketScanInterval', value || 0)}
                        min={5}
                        max={300}
                        step={5}
                        placeholder="45"
                        styles={{
                          label: { fontSize: '16px', fontWeight: 600, color: '#8B4513', marginBottom: '8px' },
                          description: { fontSize: '14px', color: '#A0522D', marginBottom: '8px' },
                          input: { 
                            fontSize: '15px', 
                            padding: '12px 16px',
                            borderWidth: '2px',
                            borderRadius: '12px',
                            '&:focus': { borderColor: '#20B2AA' }
                          }
                        }}
                      />
                    </Grid.Col>
                    <Grid.Col span={{ base: 12, sm: 6 }}>
                      <NumberInput
                        size="md"
                        label="Position Monitor Interval (sec)"
                        description="Position monitoring frequency (10-30 sec recommended)"
                        value={settings.positionMonitorInterval}
                        onChange={(value) => handleSettingChange('positionMonitorInterval', value || 0)}
                        min={1}
                        max={60}
                        step={1}
                        placeholder="15"
                        styles={{
                          label: { fontSize: '16px', fontWeight: 600, color: '#8B4513', marginBottom: '8px' },
                          description: { fontSize: '14px', color: '#A0522D', marginBottom: '8px' },
                          input: { 
                            fontSize: '15px', 
                            padding: '12px 16px',
                            borderWidth: '2px',
                            borderRadius: '12px',
                            '&:focus': { borderColor: '#20B2AA' }
                          }
                        }}
                      />
                    </Grid.Col>
                    <Grid.Col span={{ base: 12, sm: 6 }}>
                      <NumberInput
                        size="md"
                        label="Signal Execution Delay (sec)"
                        description="Delay before executing signals (2-10 sec recommended)"
                        value={settings.signalExecutionDelay}
                        onChange={(value) => handleSettingChange('signalExecutionDelay', value || 0)}
                        min={0}
                        max={30}
                        step={1}
                        placeholder="3"
                        styles={{
                          label: { fontSize: '16px', fontWeight: 600, color: '#8B4513', marginBottom: '8px' },
                          description: { fontSize: '14px', color: '#A0522D', marginBottom: '8px' },
                          input: { 
                            fontSize: '15px', 
                            padding: '12px 16px',
                            borderWidth: '2px',
                            borderRadius: '12px',
                            '&:focus': { borderColor: '#20B2AA' }
                          }
                        }}
                      />
                    </Grid.Col>
                    <Grid.Col span={{ base: 12, sm: 6 }}>
                      <NumberInput
                        size="md"
                        label="Historical Data Days"
                        description="Days of historical data for analysis (7-30 recommended)"
                        value={settings.learningDataLookbackDays}
                        onChange={(value) => handleSettingChange('learningDataLookbackDays', value || 0)}
                        min={1}
                        max={365}
                        step={1}
                        placeholder="14"
                        styles={{
                          label: { fontSize: '16px', fontWeight: 600, color: '#8B4513', marginBottom: '8px' },
                          description: { fontSize: '14px', color: '#A0522D', marginBottom: '8px' },
                          input: { 
                            fontSize: '15px', 
                            padding: '12px 16px',
                            borderWidth: '2px',
                            borderRadius: '12px',
                            '&:focus': { borderColor: '#20B2AA' }
                          }
                        }}
                      />
                    </Grid.Col>
                  </Grid>

                  {/* Save Button for Automation Section */}
                  <div className="flex justify-end pt-6 border-t-2 border-retro-brown-200">
                    <Button
                      onClick={() => saveSection('automation', {
                        autoTradingEnabled: settings.autoTradingEnabled,
                        marketScanInterval: settings.marketScanInterval,
                        positionMonitorInterval: settings.positionMonitorInterval,
                        signalExecutionDelay: settings.signalExecutionDelay,
                        maxConcurrentPositions: settings.maxConcurrentPositions,
                        learningDataLookbackDays: settings.learningDataLookbackDays,
                        enabled: settings.autoTradingEnabled,
                        profitTarget: settings.profitTop,
                        stopLoss: settings.stopLoss,
                        maxDailyLoss: settings.maxDailyLoss,
                        maxPositions: settings.maxConcurrentPositions,
                        riskLevel: 'medium',
                        symbols: ['R_10', 'R_25', 'R_50', 'R_75', 'R_100'],
                      })}
                      loading={savingSection === 'automation'}
                      size="md"
                      className="px-8"
                      leftSection={<IconCheck size={16} />}
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
            <Card className="card p-8 shadow-lg border-2 border-retro-brown-200 sticky top-8">
              <Stack gap="lg">
                <div className="text-center mb-4">
                  <Title order={3} className="text-xl font-bold text-retro-brown-800 mb-2">
                    Actions
                  </Title>
                  <Text size="sm" className="text-retro-brown-600">
                    Save and test your configuration
                  </Text>
                </div>
                
                <Button
                  onClick={saveSettings}
                  loading={saving}
                  disabled={!unsavedChanges}
                  size="lg"
                  className="w-full py-4 text-lg font-semibold"
                  leftSection={<IconCheck size={20} />}
                  styles={{
                    root: {
                      backgroundColor: unsavedChanges ? '#20B2AA' : '#CBD5E0',
                      '&:hover': { backgroundColor: unsavedChanges ? '#1a9b93' : '#CBD5E0' }
                    }
                  }}
                >
                  Save Configuration
                </Button>

                <Button
                  variant="outline"
                  onClick={testDerivConnection}
                  loading={testingConnection}
                  disabled={!settings.derivToken}
                  size="lg"
                  className="w-full py-3 font-semibold border-2"
                  leftSection={<IconTestPipe size={18} />}
                  styles={{
                    root: {
                      borderColor: '#20B2AA',
                      color: '#20B2AA',
                      '&:hover': { backgroundColor: '#E6FFFA' }
                    }
                  }}
                >
                  Test Deriv Connection
                </Button>

                <Button
                  variant="light"
                  color="orange"
                  onClick={resetToDefaults}
                  size="lg"
                  className="w-full py-3 font-semibold"
                  leftSection={<IconRefresh size={18} />}
                  styles={{
                    root: {
                      backgroundColor: 'rgba(255, 165, 0, 0.1)',
                      color: '#ea580c',
                      borderColor: '#ea580c',
                      '&:hover': { backgroundColor: 'rgba(255, 165, 0, 0.2)' }
                    }
                  }}
                >
                  Reset to Defaults
                </Button>

                <Divider />

                <div className="p-6 rounded-xl bg-retro-cream-50 border-2 border-retro-brown-200">
                  <Title order={4} className="text-lg font-bold text-retro-brown-800 mb-4">
                    System Status
                  </Title>
                  <Stack gap="md">
                    <Group justify="space-between" className="p-3 rounded-lg bg-white border border-retro-brown-200">
                      <Text size="sm" className="font-semibold text-retro-brown-700">Deriv API</Text>
                      <Badge 
                        color={connectionStatus === 'success' ? 'green' : 'gray'}
                        size="md"
                        variant="filled"
                      >
                        {connectionStatus === 'success' ? 'Connected' : 'Not configured'}
                      </Badge>
                    </Group>
                    <Group justify="space-between" className="p-3 rounded-lg bg-white border border-retro-brown-200">
                      <Text size="sm" className="font-semibold text-retro-brown-700">OpenAI API</Text>
                      <Badge 
                        color={settings.openaiApiKey ? 'green' : 'gray'}
                        size="md"
                        variant="filled"
                      >
                        {settings.openaiApiKey ? 'Configured' : 'Not configured'}
                      </Badge>
                    </Group>
                    <Group justify="space-between" className="p-3 rounded-lg bg-white border border-retro-brown-200">
                      <Text size="sm" className="font-semibold text-retro-brown-700">Auto Trading</Text>
                      <Badge 
                        color={settings.autoTradingEnabled ? 'orange' : 'gray'}
                        size="md"
                        variant="filled"
                      >
                        {settings.autoTradingEnabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                    </Group>
                  </Stack>
                </div>

                <Alert 
                  icon={<IconInfoCircle size={18} />} 
                  color="blue" 
                  className="p-4 rounded-xl border-2 border-blue-200"
                  styles={{
                    root: { backgroundColor: 'rgba(59, 130, 246, 0.1)' },
                    message: { fontSize: '14px', lineHeight: '1.5' }
                  }}
                >
                  <Text size="sm" className="font-medium">
                    Make sure to configure all parameters correctly before enabling automatic trading.
                  </Text>
                </Alert>
              </Stack>
            </Card>
          </Grid.Col>
        </Grid>
      </div>
    </Layout>
  );
}
