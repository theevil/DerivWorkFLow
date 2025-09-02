/**
 * Automation Dashboard Page - Refactored with Atomic Design
 */

import { useState, useEffect } from 'react';
import { Container, Stack, Alert, Modal, Text, Group } from '@mantine/core';
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
} from '@tabler/icons-react';

// Atomic Design Components
import { RetroButton, RetroCard, RetroIcon } from '../components/atoms';
import {
  MetricsGrid,
  WorkersPanel,
  PerformanceSection,
} from '../components/organisms';
import type {
  MetricData,
  WorkerData,
  ActionButton,
  PerformanceData,
} from '../components/organisms';
import { AutoTradingConfigModal } from '../components/automation/AutoTradingConfigModal';
import { AlertsList } from '../components/automation/AlertsList';

// Hooks and Store
import {
  useAutomationStore,
  automationActions,
  automationSelectors,
} from '../stores/automation';
import type {
  AutoTradingConfig,
  EmergencyStopRequest,
} from '../types/automation';

export function AutomationRefactored() {
  const [
    configModalOpened,
    { open: openConfigModal, close: closeConfigModal },
  ] = useDisclosure(false);
  const [
    emergencyModalOpened,
    { open: openEmergencyModal, close: closeEmergencyModal },
  ] = useDisclosure(false);
  const [emergencyReason, setEmergencyReason] = useState('');
  const [lastStatusUpdate, setLastStatusUpdate] = useState<string | null>(null);

  // Store state
  const {
    systemStatus,
    automationConfig,
    alerts,
    performance,
    isStatusLoading,
    isEmergencyLoading,
    isConfigLoading,
  } = useAutomationStore();

  // Computed values
  const isAutoTradingEnabled = automationSelectors.isAutoTradingEnabled(
    useAutomationStore.getState()
  );
  const isSystemHealthy = automationSelectors.isSystemHealthy(
    useAutomationStore.getState()
  );
  const unacknowledgedAlerts = automationSelectors.getUnacknowledgedAlerts(
    useAutomationStore.getState()
  );

  // Effects
  useEffect(() => {
    refreshSystemStatus();
    const interval = setInterval(refreshSystemStatus, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  // Handlers
  const refreshSystemStatus = async () => {
    await automationActions.fetchSystemStatus();
    await automationActions.fetchAutomationConfig();
    await automationActions.fetchAlerts();
    await automationActions.fetchPerformance();
    setLastStatusUpdate(new Date().toISOString());
  };

  const handleManualTrigger = async (type: 'scan' | 'monitor' | 'retrain') => {
    try {
      switch (type) {
        case 'scan':
          await automationActions.triggerMarketScan();
          notifications.show({
            title: 'Market Scan Triggered',
            message: 'Market scanning has been initiated',
            color: 'green',
          });
          break;
        case 'monitor':
          await automationActions.triggerPositionMonitor();
          notifications.show({
            title: 'Position Monitor Triggered',
            message: 'Position monitoring has been initiated',
            color: 'blue',
          });
          break;
        case 'retrain':
          await automationActions.triggerModelRetrain();
          notifications.show({
            title: 'Model Retraining Triggered',
            message: 'AI model retraining has been initiated',
            color: 'violet',
          });
          break;
      }
      setTimeout(refreshSystemStatus, 2000);
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: `Failed to trigger ${type}`,
        color: 'red',
      });
    }
  };

  const handleHealthCheck = async () => {
    try {
      await automationActions.runHealthCheck();
      notifications.show({
        title: 'Health Check Complete',
        message: 'System health check has been completed',
        color: 'green',
      });
      setTimeout(refreshSystemStatus, 1000);
    } catch (error) {
      notifications.show({
        title: 'Health Check Failed',
        message: 'Failed to complete health check',
        color: 'red',
      });
    }
  };

  const handleEmergencyStop = async () => {
    if (!emergencyReason.trim()) {
      notifications.show({
        title: 'Reason Required',
        message: 'Please provide a reason for the emergency stop',
        color: 'yellow',
      });
      return;
    }

    const request: EmergencyStopRequest = {
      reason: emergencyReason,
      force_close_positions: true,
    };

    try {
      await automationActions.triggerEmergencyStop(request);
      notifications.show({
        title: 'Emergency Stop Activated',
        message: 'All automated trading has been stopped',
        color: 'red',
      });
      closeEmergencyModal();
      setEmergencyReason('');
      setTimeout(refreshSystemStatus, 1000);
    } catch (error) {
      notifications.show({
        title: 'Emergency Stop Failed',
        message: 'Failed to execute emergency stop',
        color: 'red',
      });
    }
  };

  const acknowledgeAlert = async (alertId: string) => {
    try {
      await automationActions.acknowledgeAlert(alertId);
      notifications.show({
        title: 'Alert Acknowledged',
        message: 'Alert has been acknowledged',
        color: 'green',
      });
    } catch (error) {
      notifications.show({
        title: 'Error',
        message: 'Failed to acknowledge alert',
        color: 'red',
      });
    }
  };

  const handleConfigSave = async (config: AutoTradingConfig) => {
    try {
      await automationActions.configureAutoTrading(config);
      notifications.show({
        title: 'Configuration Saved',
        message: 'Auto trading configuration has been updated',
        color: 'green',
      });
      closeConfigModal();
      setTimeout(refreshSystemStatus, 1000);
    } catch (error) {
      notifications.show({
        title: 'Configuration Failed',
        message: 'Failed to save configuration',
        color: 'red',
      });
    }
  };

  // Loading state
  if (!systemStatus) {
    return (
      <Container size='xl' py='md'>
        <div className='flex items-center justify-center min-h-96'>
          <div className='loading-spinner' />
          <Text ml='md'>Loading automation dashboard...</Text>
        </div>
      </Container>
    );
  }

  // Preparar datos para las métricas principales
  const mainMetrics: MetricData[] = [
    {
      id: 'auto-trading',
      title: 'AI Auto Trading',
      value: '',
      subtitle: isAutoTradingEnabled
        ? 'System trading automatically'
        : 'Manual control only',
      icon: <IconRobot size={18} />,
      iconVariant: isAutoTradingEnabled ? 'turquoise' : 'coral',
      badge: {
        text: isAutoTradingEnabled ? 'ACTIVE' : 'OFF',
        variant: isAutoTradingEnabled ? 'success' : 'warning',
      },
    },
    {
      id: 'system-health',
      title: 'System Health',
      value: (
        <div
          className={`w-8 h-8 rounded-full border-4 ${
            isSystemHealthy
              ? 'border-retro-turquoise-400'
              : 'border-retro-red-400'
          } flex items-center justify-center`}
        >
          <Text fw={700} ta='center' size='xs' className='text-title'>
            {isSystemHealthy ? '100' : '25'}
          </Text>
        </div>
      ),
      subtitle: isSystemHealthy ? 'All systems operational' : 'Issues detected',
      icon: <IconShield size={18} />,
      iconVariant: isSystemHealthy ? 'turquoise' : 'coral',
    },
    {
      id: 'active-tasks',
      title: 'Active Tasks',
      value: systemStatus?.celery_active_tasks ?? 0,
      subtitle: 'Background processes',
      icon: <IconBolt size={18} />,
      iconVariant: 'coral',
    },
    {
      id: 'profit',
      title: '7-Day Profit',
      value: (
        <NumberFormatter
          value={performance?.trading_stats.total_profit ?? 0}
          thousandSeparator
          decimalScale={2}
          prefix='$'
        />
      ),
      subtitle: performance
        ? `${performance.trading_stats.total_trades} trades`
        : 'No data',
      icon: <IconTrendingUp size={18} />,
      iconVariant:
        performance && performance.trading_stats.total_profit > 0
          ? 'turquoise'
          : 'coral',
    },
  ];

  // Preparar datos para los workers
  const workersData: WorkerData[] = [
    {
      id: 'market-monitor',
      title: 'Market Monitor',
      subtitle: 'AI-powered market analysis',
      icon: <IconEye size={14} />,
      iconVariant: 'turquoise',
      status: {
        text: systemStatus?.market_monitor?.active ? 'ON' : 'OFF',
        variant: systemStatus?.market_monitor?.active ? 'success' : 'danger',
      },
      statusItems: [
        {
          label: 'Redis',
          value: systemStatus?.market_monitor?.redis_connected ? 'OK' : 'NO',
          variant: systemStatus?.market_monitor?.redis_connected
            ? 'success'
            : 'danger',
        },
        {
          label: 'Last Scan',
          value: systemStatus?.market_monitor?.last_scan
            ? new Date(
                systemStatus.market_monitor.last_scan
              ).toLocaleTimeString()
            : 'Never',
        },
      ],
    },
    {
      id: 'trading-executor',
      title: 'Trading Executor',
      subtitle: 'Automated trade execution',
      icon: <IconBolt size={14} />,
      iconVariant: 'coral',
      status: {
        text: systemStatus?.trading_executor?.redis_connected ? 'READY' : 'OFF',
        variant: systemStatus?.trading_executor?.redis_connected
          ? 'info'
          : 'danger',
      },
      statusItems: [
        {
          label: 'Active',
          value: `${systemStatus?.trading_executor?.active_executions ?? 0}`,
        },
        {
          label: 'Total',
          value: `${systemStatus?.trading_executor?.total_executions ?? 0}`,
        },
      ],
    },
  ];

  // Preparar acciones rápidas
  const quickActions: ActionButton[] = [
    {
      label: 'Market Scan',
      icon: <IconEye size={14} />,
      variant: 'success',
      onClick: () => handleManualTrigger('scan'),
    },
    {
      label: 'Check Positions',
      icon: <IconActivity size={14} />,
      variant: 'primary',
      onClick: () => handleManualTrigger('monitor'),
    },
    {
      label: 'Retrain AI',
      icon: <IconBrain size={14} />,
      variant: 'secondary',
      onClick: () => handleManualTrigger('retrain'),
    },
    {
      label: 'Health Check',
      icon: <IconShield size={14} />,
      variant: 'warning',
      onClick: handleHealthCheck,
    },
  ];

  return (
    <Container size='xl' py='md'>
      <Stack gap='lg'>
        {/* Header */}
        <RetroCard variant='default' padding='lg' className='gradient-header'>
          <Group justify='space-between' align='center'>
            <Group gap='md'>
              <RetroIcon variant='turquoise' size='lg'>
                <IconRobot size={24} />
              </RetroIcon>
              <div>
                <Text fw={700} size='xl' className='text-headline'>
                  AI Automation Dashboard
                </Text>
                <Text size='sm' className='text-caption'>
                  Intelligent trading automation control center
                </Text>
              </div>
            </Group>

            <Group gap='sm'>
              <button
                className='retro-icon-coral rounded-xl p-2 transition-all hover:scale-110'
                onClick={refreshSystemStatus}
                disabled={isStatusLoading}
                aria-label='Refresh automation status'
                title='Refresh automation status'
              >
                <IconRefresh size={16} />
              </button>

              <RetroButton
                variant='secondary'
                size='sm'
                leftIcon={<IconSettings size={14} />}
                onClick={openConfigModal}
              >
                Configure
              </RetroButton>

              <RetroButton
                variant='danger'
                size='sm'
                leftIcon={<IconAlertTriangle size={14} />}
                onClick={openEmergencyModal}
                disabled={!isAutoTradingEnabled}
              >
                Emergency Stop
              </RetroButton>
            </Group>
          </Group>
        </RetroCard>

        {/* System Health Alert */}
        {systemStatus && !isSystemHealthy && (
          <Alert
            icon={<IconAlertTriangle size={16} />}
            color='red'
            title='System Health Alert'
            className='alertPulse'
          >
            You have new alerts that require attention. Please review them
            below.
          </Alert>
        )}

        {/* Main Metrics Grid - Organized in groups of 3 */}
        <MetricsGrid metrics={mainMetrics} />

        {/* Workers Panel */}
        <WorkersPanel
          workers={workersData}
          quickActions={quickActions}
          onRefresh={refreshSystemStatus}
          isRefreshing={isStatusLoading}
        />

        {/* Performance Section */}
        {performance && (
          <PerformanceSection
            performance={performance}
            onViewReport={() => console.log('View detailed report')}
          />
        )}

        {/* Alerts */}
        <AlertsList alerts={alerts} onAcknowledge={acknowledgeAlert} />

        {/* Modals */}
        <AutoTradingConfigModal
          opened={configModalOpened}
          onClose={closeConfigModal}
          config={automationConfig}
          onSave={handleConfigSave}
          loading={isConfigLoading}
        />

        {/* Emergency Stop Modal */}
        <Modal
          opened={emergencyModalOpened}
          onClose={closeEmergencyModal}
          title='Emergency Stop'
          centered
        >
          <Stack gap='md'>
            <Alert
              icon={<IconAlertTriangle size={16} />}
              color='red'
              title='Emergency Stop Warning'
            >
              This will immediately disable auto trading and close all open
              positions. This action cannot be undone.
            </Alert>

            <Text size='sm' fw={500}>
              Reason for Emergency Stop:
            </Text>
            <textarea
              placeholder='Please provide a reason for the emergency stop...'
              value={emergencyReason}
              onChange={e => setEmergencyReason(e.target.value)}
              rows={3}
              className='input-primary w-full min-h-20'
            />

            <Group justify='flex-end' gap='sm'>
              <RetroButton
                variant='secondary'
                onClick={closeEmergencyModal}
                disabled={isEmergencyLoading}
              >
                Cancel
              </RetroButton>
              <RetroButton
                variant='danger'
                loading={isEmergencyLoading}
                onClick={handleEmergencyStop}
                leftIcon={<IconPlayerStop size={16} />}
              >
                Emergency Stop
              </RetroButton>
            </Group>
          </Stack>
        </Modal>
      </Stack>
    </Container>
  );
}
