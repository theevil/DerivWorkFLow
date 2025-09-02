/**
 * Worker Status Card component for displaying automation worker status
 */

import {
  Card,
  Group,
  Text,
  Badge,
  Stack,
  Progress,
  Tooltip,
  ActionIcon,
} from '@mantine/core';
import {
  IconRefresh,
  IconCheck,
  IconX,
  IconClock,
  IconActivity,
} from '@tabler/icons-react';
import type { WorkerStatus, ExecutorStatus } from '../../types/automation';

interface WorkerStatusCardProps {
  title: string;
  status: WorkerStatus | ExecutorStatus;
  isLoading?: boolean;
  onRefresh?: () => void;
}

export function WorkerStatusCard({
  title,
  status,
  isLoading = false,
  onRefresh,
}: WorkerStatusCardProps) {
  // Helper function to determine if status is WorkerStatus or ExecutorStatus
  const isWorkerStatus = (
    s: WorkerStatus | ExecutorStatus
  ): s is WorkerStatus => {
    return 'symbols_monitored' in s;
  };

  const isExecutorStatus = (
    s: WorkerStatus | ExecutorStatus
  ): s is ExecutorStatus => {
    return 'active_executions' in s;
  };

  // Determine overall health
  const isHealthy = status.redis_connected && (status.active ?? true);

  // Get status color
  const getStatusColor = () => {
    if (!status.redis_connected) return 'red';
    if (!status.active) return 'yellow';
    return 'green';
  };

  // Format last scan time
  const formatLastScan = (timestamp?: string) => {
    if (!timestamp) return 'Never';

    const now = new Date();
    const scanTime = new Date(timestamp);
    const diffMs = now.getTime() - scanTime.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    return scanTime.toLocaleDateString();
  };

  return (
    <Card shadow='sm' padding='lg' radius='md' withBorder>
      <Group justify='space-between' mb='md'>
        <Group gap='sm'>
          <Text fw={600} size='lg'>
            {title}
          </Text>
          <Badge
            color={getStatusColor()}
            variant='filled'
            leftSection={
              isHealthy ? <IconCheck size={12} /> : <IconX size={12} />
            }
          >
            {isHealthy ? 'Healthy' : 'Issues'}
          </Badge>
        </Group>

        {onRefresh && (
          <Tooltip label='Refresh Status'>
            <ActionIcon
              variant='subtle'
              color='gray'
              onClick={onRefresh}
              loading={isLoading}
            >
              <IconRefresh size={16} />
            </ActionIcon>
          </Tooltip>
        )}
      </Group>

      <Stack gap='md'>
        {/* Connection Status */}
        <Group justify='space-between'>
          <Group gap='xs'>
            <IconActivity
              size={16}
              color={status.redis_connected ? 'green' : 'red'}
            />
            <Text size='sm' c='dimmed'>
              Redis Connection
            </Text>
          </Group>
          <Badge
            color={status.redis_connected ? 'green' : 'red'}
            variant='light'
          >
            {status.redis_connected ? 'Connected' : 'Disconnected'}
          </Badge>
        </Group>

        {/* Worker-specific metrics */}
        {isWorkerStatus(status) && (
          <>
            {/* Symbols Monitored */}
            {status.symbols_monitored !== undefined && (
              <Group justify='space-between'>
                <Text size='sm' c='dimmed'>
                  Symbols Monitored
                </Text>
                <Text size='sm' fw={500}>
                  {status.symbols_monitored}
                </Text>
              </Group>
            )}

            {/* Last Scan */}
            <Group justify='space-between'>
              <Group gap='xs'>
                <IconClock size={16} />
                <Text size='sm' c='dimmed'>
                  Last Scan
                </Text>
              </Group>
              <Text size='sm' fw={500}>
                {formatLastScan(status.last_scan)}
              </Text>
            </Group>

            {/* Monitoring Intervals */}
            {status.monitoring_intervals && (
              <Stack gap='xs'>
                <Text size='sm' c='dimmed'>
                  Monitoring Intervals
                </Text>
                <Group gap='lg'>
                  <Group gap='xs'>
                    <Text size='xs' c='dimmed'>
                      Market:
                    </Text>
                    <Text size='xs' fw={500}>
                      {status.monitoring_intervals.market_scan}s
                    </Text>
                  </Group>
                  <Group gap='xs'>
                    <Text size='xs' c='dimmed'>
                      Position:
                    </Text>
                    <Text size='xs' fw={500}>
                      {status.monitoring_intervals.position_monitor}s
                    </Text>
                  </Group>
                </Group>
              </Stack>
            )}

            {/* Cache Status */}
            {status.cache_status && (
              <Stack gap='xs'>
                <Text size='sm' c='dimmed'>
                  Cache Status
                </Text>
                <Group gap='xs'>
                  {Object.entries(status.cache_status).map(
                    ([symbol, cached]) => (
                      <Badge
                        key={symbol}
                        size='xs'
                        color={cached ? 'green' : 'gray'}
                        variant='light'
                      >
                        {symbol}
                      </Badge>
                    )
                  )}
                </Group>
              </Stack>
            )}
          </>
        )}

        {/* Executor-specific metrics */}
        {isExecutorStatus(status) && (
          <>
            {/* Active Executions */}
            <Group justify='space-between'>
              <Text size='sm' c='dimmed'>
                Active Executions
              </Text>
              <Badge
                color={status.active_executions > 0 ? 'blue' : 'gray'}
                variant='light'
              >
                {status.active_executions}
              </Badge>
            </Group>

            {/* Total Executions */}
            <Group justify='space-between'>
              <Text size='sm' c='dimmed'>
                Total Executions
              </Text>
              <Text size='sm' fw={500}>
                {status.total_executions}
              </Text>
            </Group>

            {/* Auto Trading Status */}
            <Group justify='space-between'>
              <Text size='sm' c='dimmed'>
                Auto Trading
              </Text>
              <Badge
                color={status.auto_trading_enabled ? 'green' : 'yellow'}
                variant='light'
              >
                {status.auto_trading_enabled ? 'Enabled' : 'Disabled'}
              </Badge>
            </Group>

            {/* Max Positions */}
            <Group justify='space-between'>
              <Text size='sm' c='dimmed'>
                Max Concurrent Positions
              </Text>
              <Text size='sm' fw={500}>
                {status.max_concurrent_positions}
              </Text>
            </Group>

            {/* Execution Progress (if active) */}
            {status.active_executions > 0 && (
              <Stack gap='xs'>
                <Text size='sm' c='dimmed'>
                  Execution Activity
                </Text>
                <Progress
                  value={Math.min(
                    (status.active_executions /
                      status.max_concurrent_positions) *
                      100,
                    100
                  )}
                  color='blue'
                  size='sm'
                  animated
                />
              </Stack>
            )}
          </>
        )}
      </Stack>
    </Card>
  );
}
