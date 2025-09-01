/**
 * Automation Dashboard Page - Fixed JSX Structure
 */

import { useState, useEffect } from 'react';
import { Container, Stack, Alert, Modal, Text, Group, Grid, Box, Title, Button, Badge, Center, Loader } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';
import { NumberFormatter } from '@mantine/core';
import {
  IconRobot,
  IconShield,
  IconBolt,
  IconTrendingUp,
  IconEye,
  IconActivity,
  IconBrain,
  IconAlertTriangle,
  IconSettings,
  IconPlayerStop,
  IconRefresh,
  IconDatabase,
  IconServer,
  IconNetwork
} from '@tabler/icons-react';

// Components
import { WorkerStatusCard } from '../components/automation/WorkerStatusCard';
import { AutoTradingConfigModal } from '../components/automation/AutoTradingConfigModal';
import { AlertsList } from '../components/automation/AlertsList';
import { Layout } from '../components/Layout';
import { useAutomationStore, automationActions, automationSelectors } from '../stores/automation';
import type { AutoTradingConfig, EmergencyStopRequest } from '../types/automation';

export function Automation() {
  const [configModalOpened, { open: openConfigModal, close: closeConfigModal }] = useDisclosure(false);
  const [emergencyModalOpened, { open: openEmergencyModal, close: closeEmergencyModal }] = useDisclosure(false);
  const [emergencyReason, setEmergencyReason] = useState('');
  const [lastStatusUpdate, setLastStatusUpdate] = useState<string | null>(null);

  // Store state
  const {
    systemStatus,
    config,
    alerts,
    performance,
    isStatusLoading,
    isConfigLoading
  } = useAutomationStore();

  // Computed values
  const isAutoTradingEnabled = automationSelectors.isAutoTradingEnabled(useAutomationStore.getState());
  const isSystemHealthy = automationSelectors.isSystemHealthy(useAutomationStore.getState());
  const hasUnacknowledgedAlerts = automationSelectors.hasUnacknowledgedAlerts(useAutomationStore.getState());

  // Effects
  useEffect(() => {
    refreshSystemStatus();
    const interval = setInterval(refreshSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // Handlers
  const refreshSystemStatus = async () => {
    const store = useAutomationStore.getState();
    await store.loadSystemStatus();
    await store.loadConfig();
    await store.loadAlerts();
    await store.loadPerformance();
    setLastStatusUpdate(new Date().toISOString());
  };

  const handleManualTrigger = async (type: 'scan' | 'monitor' | 'retrain') => {
    try {
      const store = useAutomationStore.getState();
      switch (type) {
        case 'scan':
          await store.triggerMarketScan();
          notifications.show({
            title: 'Market Scan Triggered',
            message: 'Market scanning has been initiated',
            color: 'green'
          });
          break;
        case 'monitor':
          await store.triggerPositionMonitor();
          notifications.show({
            title: 'Position Monitor Triggered',
            message: 'Position monitoring has been initiated',
            color: 'blue'
          });
          break;
        case 'retrain':
          await store.triggerModelRetrain();
          notifications.show({
            title: 'Model Retraining Triggered',
            message: 'AI model retraining has been initiated',
            color: 'violet'
          });
          break;
      }
      setTimeout(refreshSystemStatus, 2000);
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: `Failed to trigger ${type}`,
        color: 'red'
      });
    }
  };

  const handleHealthCheck = async () => {
    try {
      const store = useAutomationStore.getState();
      await store.runHealthCheck();
      notifications.show({
        title: 'Health Check Complete',
        message: 'System health check has been completed',
        color: 'green'
      });
      setTimeout(refreshSystemStatus, 1000);
    } catch (error) {
      notifications.show({
        title: 'Health Check Failed',
        message: 'Failed to complete health check',
        color: 'red'
      });
    }
  };

  const handleEmergencyStop = async () => {
    if (!emergencyReason.trim()) {
      notifications.show({
        title: 'Reason Required',
        message: 'Please provide a reason for the emergency stop',
        color: 'yellow'
      });
      return;
    }

    const request: EmergencyStopRequest = {
      reason: emergencyReason,
      close_positions: true
    };

    try {
      const store = useAutomationStore.getState();
      await store.triggerEmergencyStop(request);
      notifications.show({
        title: 'Emergency Stop Activated',
        message: 'All automated trading has been stopped',
        color: 'red'
      });
      closeEmergencyModal();
      setEmergencyReason('');
      setTimeout(refreshSystemStatus, 1000);
    } catch (error) {
      notifications.show({
        title: 'Emergency Stop Failed',
        message: 'Failed to execute emergency stop',
        color: 'red'
      });
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      const store = useAutomationStore.getState();
      await store.acknowledgeAlert(alertId);
      notifications.show({
        title: 'Alert Acknowledged',
        message: 'Alert has been acknowledged',
        color: 'green'
      });
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to acknowledge alert',
        color: 'red'
      });
    }
  };

  const handleConfigSave = async (config: AutoTradingConfig) => {
    try {
      const store = useAutomationStore.getState();
      await store.updateConfig(config);
      notifications.show({
        title: 'Configuration Saved',
        message: 'Auto trading configuration has been updated',
        color: 'green'
      });
      closeConfigModal();
      setTimeout(refreshSystemStatus, 1000);
    } catch (error) {
      notifications.show({
        title: 'Configuration Failed',
        message: 'Failed to save configuration',
        color: 'red'
      });
    }
  };

  // Loading state
  if (!systemStatus) {
    return (
      <Layout>
        <Container size="xl" py="md">
          <div className="flex items-center justify-center min-h-96">
            <div className="loading-spinner" />
            <Text ml="md">Loading automation dashboard...</Text>
          </div>
        </Container>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="flex flex-col gap-8">
        <div className="mx-6">
          <Stack gap="lg">
            {/* Header */}
            <div className="gradient-header fade-in rounded-2xl p-6 shadow-lg">
              <Group justify="space-between" align="center">
                <Group gap="md">
                  <div className="retro-icon-turquoise rounded-2xl p-3">
                    <IconRobot size={24} />
                  </div>
                  <Box>
                    <Title order={2} className="retro-text-secondary text-headline">
                      AI Automation Dashboard
                    </Title>
                    <Text size="sm" className="retro-text-accent">
                      Intelligent trading automation control center
                    </Text>
                  </Box>
                </Group>

                <Group gap="sm">
                  <button
                    className="retro-icon-coral rounded-xl p-2 transition-all hover:scale-110"
                    onClick={refreshSystemStatus}
                    disabled={isStatusLoading}
                    aria-label="Refresh automation status"
                    title="Refresh automation status"
                  >
                    <IconRefresh size={16} />
                  </button>
                  
                  <button className="btn-secondary text-sm" onClick={openConfigModal}>
                    <IconSettings size={14} className="mr-2" />
                    Configure
                  </button>
                  
                  <button
                    className="btn-danger text-sm"
                    onClick={openEmergencyModal}
                    disabled={!isAutoTradingEnabled}
                  >
                    <IconAlertTriangle size={14} className="mr-2" />
                    Emergency Stop
                  </button>
                </Group>
              </Group>
            </div>

            {/* System Health Alert */}
            {systemStatus && !isSystemHealthy && (
              <Alert
                icon={<IconAlertTriangle size={16} />}
                color="red"
                title="System Health Alert"
                className="alertPulse"
              >
                You have new alerts that require attention. Please review them below.
              </Alert>
            )}

            {/* Status Cards - Organized in Groups of 3 */}
            <div className="space-y-6">
              {/* Grupo 1: Métricas Principales */}
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, sm: 6, md: 4 }}>
                  <div className="card metric-card">
                    <Group justify="space-between" mb="xs">
                      <div className={`retro-icon-${isAutoTradingEnabled ? 'turquoise' : 'coral'} rounded-xl p-2`}>
                        <IconRobot size={18} />
                      </div>
                      <span className={`badge-${isAutoTradingEnabled ? 'success' : 'warning'}`}>
                        {isAutoTradingEnabled ? 'ACTIVE' : 'OFF'}
                      </span>
                    </Group>
                    <Text fw={700} size="sm" mb="xs" className="text-title">AI Auto Trading</Text>
                    <Text size="xs" className="text-caption">
                      {isAutoTradingEnabled ? 'System trading automatically' : 'Manual control only'}
                    </Text>
                  </div>
                </Grid.Col>

                <Grid.Col span={{ base: 12, sm: 6, md: 4 }}>
                  <div className="card metric-card">
                    <Group justify="space-between" mb="xs">
                      <div className={`retro-icon-${isSystemHealthy ? 'turquoise' : 'coral'} rounded-xl p-2`}>
                        <IconShield size={18} />
                      </div>
                      <div className="relative">
                        <div className={`w-8 h-8 rounded-full border-4 ${isSystemHealthy ? 'border-retro-turquoise-400' : 'border-retro-red-400'} flex items-center justify-center`}>
                          <Text fw={700} ta="center" size="xs" className="text-title">
                            {isSystemHealthy ? '100' : '25'}
                          </Text>
                        </div>
                      </div>
                    </Group>
                    <Text fw={700} size="sm" mb="xs" className="text-title">System Health</Text>
                    <Text size="xs" className="text-caption">
                      {isSystemHealthy ? 'All systems operational' : 'Issues detected'}
                    </Text>
                  </div>
                </Grid.Col>

                <Grid.Col span={{ base: 12, sm: 6, md: 4 }}>
                  <div className="card metric-card">
                    <Group justify="space-between" mb="xs">
                      <div className="retro-icon-coral rounded-xl p-2">
                        <IconBolt size={18} />
                      </div>
                      <Text size="xl" fw={900} className="text-title">
                        {systemStatus?.celery_active_tasks ?? 0}
                      </Text>
                    </Group>
                    <Text fw={700} size="sm" mb="xs" className="text-title">Active Tasks</Text>
                    <Text size="xs" className="text-caption">Background processes</Text>
                  </div>
                </Grid.Col>
              </Grid>

              {/* Grupo 2: Métricas de Performance */}
              <Grid gutter="lg">
                <Grid.Col span={{ base: 12, sm: 6, md: 4 }}>
                  <div className="card metric-card">
                    <Group justify="space-between" mb="xs">
                      <div className={`retro-icon-${performance && performance.trading_stats.total_profit > 0 ? 'turquoise' : 'coral'} rounded-xl p-2`}>
                        <IconTrendingUp size={18} />
                      </div>
                      <Text size="lg" fw={900} className={`text-${performance && performance.trading_stats.total_profit > 0 ? 'profit' : 'loss'}`}>
                        <NumberFormatter
                          value={performance?.trading_stats.total_profit ?? 0}
                          thousandSeparator
                          decimalScale={2}
                          prefix="$"
                        />
                      </Text>
                    </Group>
                    <Text fw={700} size="sm" mb="xs" className="text-title">7-Day Profit</Text>
                    <Text size="xs" className="text-caption">
                      {performance ? `${performance.trading_stats.total_trades} trades` : 'No data'}
                    </Text>
                  </div>
                </Grid.Col>

                <Grid.Col span={{ base: 12, sm: 6, md: 4 }}>
                  <div className="card metric-card">
                    <Group justify="space-between" mb="xs">
                      <div className="retro-icon-turquoise rounded-xl p-2">
                        <IconDatabase size={18} />
                      </div>
                      <Text size="xl" fw={900} className="text-title">
                        {performance?.trading_stats.total_trades ?? 0}
                      </Text>
                    </Group>
                    <Text fw={700} size="sm" mb="xs" className="text-title">Total Trades</Text>
                    <Text size="xs" className="text-caption">Automated + Manual</Text>
                  </div>
                </Grid.Col>

                <Grid.Col span={{ base: 12, sm: 6, md: 4 }}>
                  <div className="card metric-card">
                    <Group justify="space-between" mb="xs">
                      <div className="retro-icon-turquoise rounded-xl p-2">
                        <IconTrendingUp size={18} />
                      </div>
                      <Text size="xl" fw={900} className="text-title">
                        {performance ? `${(performance.trading_stats.win_rate * 100).toFixed(1)}%` : '0%'}
                      </Text>
                    </Group>
                    <Text fw={700} size="sm" mb="xs" className="text-title">Win Rate</Text>
                    <Text size="xs" className="text-caption">Success ratio</Text>
                  </div>
                </Grid.Col>
              </Grid>
            </div>

            {/* Workers & Controls */}
            <Grid>
              <Grid.Col span={{ base: 12, lg: 8 }}>
                <div className="card">
                  <Group justify="space-between" mb="md">
                    <Group gap="sm">
                      <div className="retro-icon-turquoise rounded-xl p-2">
                        <IconServer size={18} />
                      </div>
                      <Text fw={700} size="lg" className="text-headline">System Workers</Text>
                    </Group>
                    <button 
                      className="retro-icon-coral rounded-xl p-2 transition-all hover:scale-110"
                      onClick={refreshSystemStatus}
                      disabled={isStatusLoading}
                      aria-label="Refresh worker status"
                      title="Refresh worker status"
                    >
                      <IconRefresh size={14} />
                    </button>
                  </Group>

                  <Grid>
                    <Grid.Col span={{ base: 12, md: 6 }}>
                      <div className="worker-card rounded-xl p-4">
                        <Group justify="space-between" mb="sm">
                          <Group gap="xs">
                            <div className="retro-icon-turquoise rounded-lg p-1">
                              <IconEye size={14} />
                            </div>
                            <Text fw={700} size="sm" className="text-title">Market Monitor</Text>
                          </Group>
                          <span className={`badge-${systemStatus?.market_monitor?.active ? 'success' : 'danger'}`}>
                            {systemStatus?.market_monitor?.active ? 'ON' : 'OFF'}
                          </span>
                        </Group>

                        <Stack gap="xs">
                          <Group justify="space-between">
                            <Text size="xs" className="text-caption">Redis</Text>
                            <span className={`badge-${systemStatus?.market_monitor?.redis_connected ? 'success' : 'danger'}`}>
                              {systemStatus?.market_monitor?.redis_connected ? 'OK' : 'NO'}
                            </span>
                          </Group>
                          <Group justify="space-between">
                            <Text size="xs" className="text-caption">Last Scan</Text>
                            <Text size="xs" className="text-title">
                              {systemStatus?.market_monitor?.last_scan 
                                ? new Date(systemStatus.market_monitor.last_scan).toLocaleTimeString()
                                : 'Never'
                              }
                            </Text>
                          </Group>
                        </Stack>
                      </div>
                    </Grid.Col>
                    
                    <Grid.Col span={{ base: 12, md: 6 }}>
                      <div className="worker-card rounded-xl p-4">
                        <Group justify="space-between" mb="sm">
                          <Group gap="xs">
                            <div className="retro-icon-coral rounded-lg p-1">
                              <IconBolt size={14} />
                            </div>
                            <Text fw={700} size="sm" className="text-title">Trading Executor</Text>
                          </Group>
                          <span className={`badge-${systemStatus?.trading_executor?.redis_connected ? 'info' : 'danger'}`}>
                            {systemStatus?.trading_executor?.redis_connected ? 'READY' : 'OFF'}
                          </span>
                        </Group>

                        <Stack gap="xs">
                          <Group justify="space-between">
                            <Text size="xs" className="text-caption">Active</Text>
                            <Text size="xs" fw={700} className="text-title">{systemStatus?.trading_executor?.active_executions ?? 0}</Text>
                          </Group>
                          <Group justify="space-between">
                            <Text size="xs" className="text-caption">Total</Text>
                            <Text size="xs" fw={700} className="text-title">{systemStatus?.trading_executor?.total_executions ?? 0}</Text>
                          </Group>
                        </Stack>
                      </div>
                    </Grid.Col>
                  </Grid>
                </div>
              </Grid.Col>

              <Grid.Col span={{ base: 12, lg: 4 }}>
                <div className="card">
                  <Group justify="space-between" mb="md">
                    <Group gap="sm">
                      <div className="retro-icon-coral rounded-xl p-2">
                        <IconSettings size={18} />
                      </div>
                      <Text fw={700} size="lg" className="text-headline">Quick Actions</Text>
                    </Group>
                  </Group>

                  <Stack gap="sm">
                    <button className="btn-success w-full" onClick={() => handleManualTrigger('scan')}>
                      <IconEye size={14} className="mr-2" />
                      Market Scan
                    </button>

                    <button className="btn-primary w-full" onClick={() => handleManualTrigger('monitor')}>
                      <IconActivity size={14} className="mr-2" />
                      Check Positions
                    </button>

                    <button className="btn-secondary w-full" onClick={() => handleManualTrigger('retrain')}>
                      <IconBrain size={14} className="mr-2" />
                      Retrain AI
                    </button>

                    <button className="btn-warning w-full" onClick={handleHealthCheck}>
                      <IconShield size={14} className="mr-2" />
                      Health Check
                    </button>
                  </Stack>
                </div>
              </Grid.Col>
            </Grid>

            {/* Performance Section */}
            {performance && (
              <div className="card-elevated">
                <Group justify="space-between" mb="lg">
                  <Group gap="md">
                    <div className="retro-icon-turquoise rounded-xl p-3">
                      <IconTrendingUp size={28} />
                    </div>
                    <Box>
                      <Text fw={700} size="xl" className="text-headline">Performance Analytics</Text>
                      <Text size="sm" className="text-caption">7-day trading performance overview</Text>
                    </Box>
                  </Group>
                  <span className="badge-info">Last 7 days</span>
                </Group>
                
                <Grid>
                  <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}>
                    <div className="neumorph-inset p-4 performance-card">
                      <Group justify="space-between" mb="md">
                        <div className="retro-icon-turquoise rounded-lg p-2">
                          <IconDatabase size={20} />
                        </div>
                        <Text size="2xl" fw={900} className="text-title">
                          {performance.trading_stats.total_trades}
                        </Text>
                      </Group>
                      <Text fw={700} className="text-title" mb="xs">Total Trades</Text>
                      <Text size="xs" className="text-caption">Automated + Manual</Text>
                    </div>
                  </Grid.Col>
                  
                  <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}>
                    <div className="neumorph-inset p-4 performance-card">
                      <Group justify="space-between" mb="md">
                        <div className="retro-icon-turquoise rounded-lg p-2">
                          <IconTrendingUp size={20} />
                        </div>
                        <Group gap="xs">
                          <Text size="2xl" fw={900} className="text-title">
                            <NumberFormatter
                              value={performance.trading_stats.win_rate * 100}
                              decimalScale={1}
                              suffix="%"
                            />
                          </Text>
                          <div className="w-10 h-10 rounded-full border-4 border-retro-turquoise-400 flex items-center justify-center">
                            <Text fw={600} ta="center" size="xs" className="text-title">✓</Text>
                          </div>
                        </Group>
                      </Group>
                      <Text fw={700} className="text-title" mb="xs">Win Rate</Text>
                      <Text size="xs" className="text-caption">Success ratio</Text>
                    </div>
                  </Grid.Col>
                  
                  <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}>
                    <div className="neumorph-inset p-4 performance-card">
                      <Group justify="space-between" mb="md">
                        <div className={`retro-icon-${performance.trading_stats.avg_profit > 0 ? 'turquoise' : 'coral'} rounded-lg p-2`}>
                          <IconTrendingUp size={20} />
                        </div>
                        <Text size="xl" fw={900} className={`text-${performance.trading_stats.avg_profit > 0 ? 'profit' : 'loss'}`}>
                          <NumberFormatter
                            value={performance.trading_stats.avg_profit}
                            thousandSeparator
                            decimalScale={2}
                            prefix="$"
                          />
                        </Text>
                      </Group>
                      <Text fw={700} className="text-title" mb="xs">Avg Profit</Text>
                      <Text size="xs" className="text-caption">Per trade</Text>
                    </div>
                  </Grid.Col>
                  
                  <Grid.Col span={{ base: 12, sm: 6, lg: 3 }}>
                    <div className="neumorph-inset p-4 performance-card">
                      <Group justify="space-between" mb="md">
                        <div className="retro-icon-coral rounded-lg p-2">
                          <IconActivity size={20} />
                        </div>
                        <Group gap="xs">
                          <Text size="xl" fw={900} className="text-title">
                            {performance.trading_stats.profitable_trades}
                          </Text>
                          <Text size="md" className="text-caption">
                            / {performance.trading_stats.total_trades}
                          </Text>
                        </Group>
                      </Group>
                      <Text fw={700} className="text-title" mb="xs">Profitable</Text>
                      <Text size="xs" className="text-caption">Winning trades</Text>
                    </div>
                  </Grid.Col>
                </Grid>

                <div className="border-t-2 border-retro-brown mt-6 pt-6">
                  <Group justify="space-between">
                    <Group gap="lg">
                      <Box ta="center">
                        <Text size="sm" className="text-caption" mb="xs">Max Profit</Text>
                        <Text fw={700} className="text-profit">
                          <NumberFormatter
                            value={performance.trading_stats.max_profit}
                            thousandSeparator
                            decimalScale={2}
                            prefix="$"
                          />
                        </Text>
                      </Box>
                      
                      <Box ta="center">
                        <Text size="sm" className="text-caption" mb="xs">Max Loss</Text>
                        <Text fw={700} className="text-loss">
                          <NumberFormatter
                            value={performance.trading_stats.min_profit}
                            thousandSeparator
                            decimalScale={2}
                            prefix="$"
                          />
                        </Text>
                      </Box>

                      <Box ta="center">
                        <Text size="sm" className="text-caption" mb="xs">Total P&L</Text>
                        <Text fw={700} className={`text-${performance.trading_stats.total_profit > 0 ? 'profit' : 'loss'}`}>
                          <NumberFormatter
                            value={performance.trading_stats.total_profit}
                            thousandSeparator
                            decimalScale={2}
                            prefix="$"
                          />
                        </Text>
                      </Box>
                    </Group>

                    <button className="btn-primary">
                      <IconTrendingUp size={16} className="mr-2" />
                      View Detailed Report
                    </button>
                  </Group>
                </div>
              </div>
            )}

            {/* Alerts */}
            <AlertsList alerts={alerts} onAcknowledge={acknowledgeAlert} />

            {/* Modals */}
            <AutoTradingConfigModal
              opened={configModalOpened}
              onClose={closeConfigModal}
              currentConfig={config ?? undefined}
              onSave={handleConfigSave}
            />

            {/* Emergency Stop Modal */}
            <Modal opened={emergencyModalOpened} onClose={closeEmergencyModal} title="Emergency Stop" centered>
              <Stack gap="md">
                <Alert
                  icon={<IconAlertTriangle size={16} />}
                  color="red"
                  title="Emergency Stop Warning"
                >
                  This will immediately disable auto trading and close all open positions. 
                  This action cannot be undone.
                </Alert>

                <Text size="sm" fw={500}>Reason for Emergency Stop:</Text>
                <textarea
                  placeholder="Please provide a reason for the emergency stop..."
                  value={emergencyReason}
                  onChange={(e) => setEmergencyReason(e.target.value)}
                  rows={3}
                  className="input-primary w-full min-h-20"
                />

                <Group justify="flex-end" gap="sm">
                  <Button variant="subtle" onClick={closeEmergencyModal}>
                    Cancel
                  </Button>
                  <Button
                    color="red"
                    onClick={handleEmergencyStop}
                    leftSection={<IconPlayerStop size={16} />}
                  >
                    Emergency Stop
                  </Button>
                </Group>
              </Stack>
            </Modal>
          </Stack>
        </div>
      </div>
    </Layout>
  );
}
