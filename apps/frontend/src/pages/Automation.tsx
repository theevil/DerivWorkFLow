/**
 * Automation Dashboard Page
 */

import { 
  Container, 
  Title, 
  Group, 
  Button, 
  Grid, 
  Card,
  Text,
  Badge,
  Stack,
  ActionIcon,
  Tooltip,
  Modal,
  Alert,
  Progress,
  SimpleGrid,
  NumberFormatter,
  Box,
  Loader,
  Center
} from '@mantine/core';
import { 
  IconSettings, 
  IconRefresh, 
  IconAlertTriangle,
  IconActivity,
  IconRobot,
  IconChartLine,
  IconClock,
  IconCheck,
  IconX,
  IconPlayerPlay,
  IconPlayerStop
} from '@tabler/icons-react';
import { useEffect, useState } from 'react';
import { useDisclosure } from '@mantine/hooks';
import { notifications } from '@mantine/notifications';

import { WorkerStatusCard } from '../components/automation/WorkerStatusCard';
import { AutoTradingConfigModal } from '../components/automation/AutoTradingConfigModal';
import { AlertsList } from '../components/automation/AlertsList';
import { useAutomationStore, automationActions, automationSelectors } from '../stores/automation';
import type { AutoTradingConfig, EmergencyStopRequest } from '../types/automation';

export function Automation() {
  const [configModalOpened, { open: openConfigModal, close: closeConfigModal }] = useDisclosure(false);
  const [emergencyModalOpened, { open: openEmergencyModal, close: closeEmergencyModal }] = useDisclosure(false);
  const [emergencyReason, setEmergencyReason] = useState('');
  const [isEmergencyLoading, setIsEmergencyLoading] = useState(false);

  // Store state
  const {
    config,
    systemStatus,
    alerts,
    performance,
    isConfigLoading,
    isStatusLoading,
    isAlertsLoading,
    isPerformanceLoading,
    unacknowledgedCount,
    lastStatusUpdate,
  } = useAutomationStore();

  // Store actions
  const {
    loadConfig,
    updateConfig,
    loadSystemStatus,
    refreshSystemStatus,
    loadAlerts,
    acknowledgeAlert,
    loadPerformance,
    triggerEmergencyStop,
    triggerMarketScan,
    triggerPositionMonitor,
    triggerModelRetrain,
    runHealthCheck,
  } = useAutomationStore();

  // Computed values
  const isSystemHealthy = systemStatus ? automationSelectors.isSystemHealthy({ systemStatus } as any) : false;
  const isAutoTradingEnabled = automationSelectors.isAutoTradingEnabled({ config } as any);
  const hasUnacknowledgedAlerts = unacknowledgedCount > 0;

  // Initialize store on mount
  useEffect(() => {
    automationActions.initialize();
  }, []);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const cleanup = automationActions.startAutoRefresh();
    return cleanup;
  }, []);

  const handleConfigSave = async (newConfig: AutoTradingConfig) => {
    try {
      await updateConfig(newConfig);
      notifications.show({
        title: 'Configuration Updated',
        message: 'Auto trading configuration has been saved successfully.',
        color: 'green',
        icon: <IconCheck size={16} />,
      });
    } catch (error) {
      notifications.show({
        title: 'Configuration Error',
        message: 'Failed to update configuration. Please try again.',
        color: 'red',
        icon: <IconX size={16} />,
      });
      throw error;
    }
  };

  const handleEmergencyStop = async () => {
    if (!emergencyReason.trim()) {
      notifications.show({
        title: 'Reason Required',
        message: 'Please provide a reason for the emergency stop.',
        color: 'orange',
      });
      return;
    }

    setIsEmergencyLoading(true);
    try {
      const request: EmergencyStopRequest = {
        reason: emergencyReason,
        close_positions: true,
      };
      
      await triggerEmergencyStop(request);
      
      notifications.show({
        title: 'Emergency Stop Triggered',
        message: 'All positions are being closed and auto trading has been disabled.',
        color: 'red',
        icon: <IconAlertTriangle size={16} />,
      });
      
      closeEmergencyModal();
      setEmergencyReason('');
    } catch (error) {
      notifications.show({
        title: 'Emergency Stop Failed',
        message: 'Failed to trigger emergency stop. Please try again.',
        color: 'red',
        icon: <IconX size={16} />,
      });
    } finally {
      setIsEmergencyLoading(false);
    }
  };

  const handleManualTrigger = async (action: 'scan' | 'monitor' | 'retrain') => {
    try {
      let taskId: string;
      let actionName: string;

      switch (action) {
        case 'scan':
          taskId = await triggerMarketScan();
          actionName = 'Market Scan';
          break;
        case 'monitor':
          taskId = await triggerPositionMonitor();
          actionName = 'Position Monitor';
          break;
        case 'retrain':
          taskId = await triggerModelRetrain();
          actionName = 'Model Retrain';
          break;
      }

      notifications.show({
        title: `${actionName} Triggered`,
        message: `Task ${taskId} has been queued successfully.`,
        color: 'blue',
        icon: <IconPlayerPlay size={16} />,
      });
    } catch (error) {
      notifications.show({
        title: 'Trigger Failed',
        message: 'Failed to trigger the action. Please try again.',
        color: 'red',
        icon: <IconX size={16} />,
      });
    }
  };

  const handleHealthCheck = async () => {
    try {
      await runHealthCheck();
      notifications.show({
        title: 'Health Check Complete',
        message: 'System health check has been completed.',
        color: 'green',
        icon: <IconCheck size={16} />,
      });
    } catch (error) {
      notifications.show({
        title: 'Health Check Failed',
        message: 'Health check failed. System may have issues.',
        color: 'red',
        icon: <IconX size={16} />,
      });
    }
  };

  if (isStatusLoading && !systemStatus) {
    return (
      <Container size="xl" py="xl">
        <Center h={400}>
          <Stack align="center" gap="md">
            <Loader size="xl" />
            <Text size="lg" c="dimmed">Loading automation system...</Text>
          </Stack>
        </Center>
      </Container>
    );
  }

  return (
    <Container size="xl" py="xl">
      <Stack gap="xl">
        {/* Header */}
        <Group justify="space-between">
          <Stack gap="xs">
            <Title order={1}>Automation Dashboard</Title>
            <Text size="lg" c="dimmed">
              Monitor and control your AI-powered trading automation
            </Text>
          </Stack>

          <Group gap="sm">
            <Tooltip label="Refresh All Data">
              <ActionIcon
                size="lg"
                variant="subtle"
                onClick={refreshSystemStatus}
                loading={isStatusLoading}
              >
                <IconRefresh size={20} />
              </ActionIcon>
            </Tooltip>
            
            <Button
              leftSection={<IconSettings size={16} />}
              onClick={openConfigModal}
              variant="light"
            >
              Configure
            </Button>
            
            <Button
              leftSection={<IconAlertTriangle size={16} />}
              color="red"
              onClick={openEmergencyModal}
              disabled={!isAutoTradingEnabled}
            >
              Emergency Stop
            </Button>
          </Group>
        </Group>

        {/* System Health Alert */}
        {systemStatus && !isSystemHealthy && (
          <Alert
            icon={<IconAlertTriangle size={16} />}
            color="red"
            title="System Health Issues Detected"
          >
            The automation system is experiencing issues. Please check worker status and resolve any problems.
          </Alert>
        )}

        {/* Unacknowledged Alerts */}
        {hasUnacknowledgedAlerts && (
          <Alert
            icon={<IconAlertTriangle size={16} />}
            color="orange"
            title={`${unacknowledgedCount} Unacknowledged Alert${unacknowledgedCount === 1 ? '' : 's'}`}
          >
            You have new alerts that require attention. Please review them below.
          </Alert>
        )}

        {/* Key Metrics */}
        <SimpleGrid cols={{ base: 2, md: 4 }} spacing="md">
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text size="sm" c="dimmed">Auto Trading</Text>
              <IconRobot size={20} color={isAutoTradingEnabled ? 'green' : 'gray'} />
            </Group>
            <Badge
              color={isAutoTradingEnabled ? 'green' : 'gray'}
              variant="filled"
              size="lg"
            >
              {isAutoTradingEnabled ? 'ENABLED' : 'DISABLED'}
            </Badge>
          </Card>

          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text size="sm" c="dimmed">System Health</Text>
              <IconActivity size={20} color={isSystemHealthy ? 'green' : 'red'} />
            </Group>
            <Badge
              color={isSystemHealthy ? 'green' : 'red'}
              variant="filled"
              size="lg"
            >
              {isSystemHealthy ? 'HEALTHY' : 'ISSUES'}
            </Badge>
          </Card>

          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text size="sm" c="dimmed">Active Tasks</Text>
              <IconClock size={20} />
            </Group>
            <Text size="xl" fw={700}>
              {systemStatus?.celery_active_tasks ?? 0}
            </Text>
          </Card>

          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text size="sm" c="dimmed">7-Day Profit</Text>
              <IconChartLine size={20} />
            </Group>
            <Text size="xl" fw={700} c={performance && performance.trading_stats.total_profit > 0 ? 'green' : 'red'}>
              <NumberFormatter
                value={performance?.trading_stats.total_profit ?? 0}
                thousandSeparator
                decimalScale={2}
                prefix="$"
              />
            </Text>
          </Card>
        </SimpleGrid>

        {/* Worker Status */}
        <Grid>
          <Grid.Col span={{ base: 12, md: 6 }}>
            <WorkerStatusCard
              title="Market Monitor"
              status={systemStatus?.market_monitor ?? { active: false, redis_connected: false }}
              isLoading={isStatusLoading}
              onRefresh={refreshSystemStatus}
            />
          </Grid.Col>
          
          <Grid.Col span={{ base: 12, md: 6 }}>
            <WorkerStatusCard
              title="Trading Executor"
              status={systemStatus?.trading_executor ?? { 
                active_executions: 0, 
                total_executions: 0, 
                redis_connected: false,
                auto_trading_enabled: false,
                max_concurrent_positions: 0
              }}
              isLoading={isStatusLoading}
              onRefresh={refreshSystemStatus}
            />
          </Grid.Col>
        </Grid>

        {/* Manual Controls */}
        <Card shadow="sm" padding="lg" radius="md" withBorder>
          <Group justify="space-between" mb="lg">
            <Text fw={600} size="lg">Manual Controls</Text>
            <Text size="sm" c="dimmed">
              Last update: {lastStatusUpdate ? new Date(lastStatusUpdate).toLocaleTimeString() : 'Never'}
            </Text>
          </Group>

          <SimpleGrid cols={{ base: 2, md: 4 }} spacing="md">
            <Button
              variant="light"
              leftSection={<IconRefresh size={16} />}
              onClick={() => handleManualTrigger('scan')}
              fullWidth
            >
              Trigger Market Scan
            </Button>

            <Button
              variant="light"
              leftSection={<IconActivity size={16} />}
              onClick={() => handleManualTrigger('monitor')}
              fullWidth
            >
              Check Positions
            </Button>

            <Button
              variant="light"
              leftSection={<IconRobot size={16} />}
              onClick={() => handleManualTrigger('retrain')}
              fullWidth
            >
              Retrain Models
            </Button>

            <Button
              variant="light"
              leftSection={<IconCheck size={16} />}
              onClick={handleHealthCheck}
              fullWidth
            >
              Health Check
            </Button>
          </SimpleGrid>
        </Card>

        {/* Performance Summary */}
        {performance && (
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Text fw={600} size="lg" mb="lg">7-Day Performance Summary</Text>
            
            <SimpleGrid cols={{ base: 2, md: 4 }} spacing="md">
              <Box>
                <Text size="sm" c="dimmed">Total Trades</Text>
                <Text size="xl" fw={700}>{performance.trading_stats.total_trades}</Text>
              </Box>
              
              <Box>
                <Text size="sm" c="dimmed">Win Rate</Text>
                <Text size="xl" fw={700} c="green">
                  <NumberFormatter
                    value={performance.trading_stats.win_rate * 100}
                    decimalScale={1}
                    suffix="%"
                  />
                </Text>
              </Box>
              
              <Box>
                <Text size="sm" c="dimmed">Average Profit</Text>
                <Text size="xl" fw={700} c={performance.trading_stats.avg_profit > 0 ? 'green' : 'red'}>
                  <NumberFormatter
                    value={performance.trading_stats.avg_profit}
                    thousandSeparator
                    decimalScale={2}
                    prefix="$"
                  />
                </Text>
              </Box>
              
              <Box>
                <Text size="sm" c="dimmed">Profitable Trades</Text>
                <Text size="xl" fw={700}>
                  {performance.trading_stats.profitable_trades} / {performance.trading_stats.total_trades}
                </Text>
              </Box>
            </SimpleGrid>
          </Card>
        )}

        {/* Alerts */}
        <AlertsList
          alerts={alerts}
          onAcknowledge={acknowledgeAlert}
          isLoading={isAlertsLoading}
        />
      </Stack>

      {/* Configuration Modal */}
      <AutoTradingConfigModal
        opened={configModalOpened}
        onClose={closeConfigModal}
        currentConfig={config ?? undefined}
        onSave={handleConfigSave}
      />

      {/* Emergency Stop Modal */}
      <Modal
        opened={emergencyModalOpened}
        onClose={closeEmergencyModal}
        title="Emergency Stop"
        centered
      >
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
            style={{ width: '100%', minHeight: '80px' }}
          />

          <Group justify="flex-end" gap="sm">
            <Button variant="subtle" onClick={closeEmergencyModal} disabled={isEmergencyLoading}>
              Cancel
            </Button>
            <Button
              color="red"
              loading={isEmergencyLoading}
              onClick={handleEmergencyStop}
              leftSection={<IconPlayerStop size={16} />}
            >
              Emergency Stop
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Container>
  );
}
