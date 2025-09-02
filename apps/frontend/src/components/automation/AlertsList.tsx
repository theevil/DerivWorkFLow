/**
 * Alerts List component for displaying automation alerts and notifications
 */

import {
  Card,
  Group,
  Text,
  Badge,
  Button,
  Stack,
  ScrollArea,
  ActionIcon,
  Tooltip,
  Alert,
  Loader,
  Empty,
  Box,
  ThemeIcon,
} from '@mantine/core';
import {
  IconAlertTriangle,
  IconCheck,
  IconX,
  IconInfoCircle,
  IconClock,
  IconBell,
  IconBellOff,
} from '@tabler/icons-react';
import { useState } from 'react';
import type { Alert as AlertType } from '../../types/automation';

interface AlertsListProps {
  alerts: AlertType[];
  onAcknowledge: (alertId: string) => Promise<void>;
  isLoading?: boolean;
}

export function AlertsList({
  alerts,
  onAcknowledge,
  isLoading = false,
}: AlertsListProps) {
  const [acknowledgingIds, setAcknowledgingIds] = useState<Set<string>>(
    new Set()
  );

  const handleAcknowledge = async (alertId: string) => {
    setAcknowledgingIds(prev => new Set(prev).add(alertId));
    try {
      await onAcknowledge(alertId);
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    } finally {
      setAcknowledgingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(alertId);
        return newSet;
      });
    }
  };

  const getAlertIcon = (type: AlertType['type']) => {
    switch (type) {
      case 'emergency_stop':
        return { icon: IconAlertTriangle, color: 'red' };
      case 'risk_warning':
        return { icon: IconAlertTriangle, color: 'yellow' };
      case 'position_closed':
        return { icon: IconInfoCircle, color: 'blue' };
      case 'system_error':
        return { icon: IconX, color: 'red' };
      default:
        return { icon: IconBell, color: 'gray' };
    }
  };

  const getAlertTitle = (type: AlertType['type']) => {
    switch (type) {
      case 'emergency_stop':
        return 'Emergency Stop Triggered';
      case 'risk_warning':
        return 'Risk Warning';
      case 'position_closed':
        return 'Position Closed';
      case 'system_error':
        return 'System Error';
      default:
        return 'Alert';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    return date.toLocaleDateString();
  };

  // Separate unacknowledged and acknowledged alerts
  const unacknowledgedAlerts = alerts.filter(alert => !alert.acknowledged);
  const acknowledgedAlerts = alerts.filter(alert => alert.acknowledged);

  if (isLoading) {
    return (
      <Card shadow='sm' padding='lg' radius='md' withBorder>
        <Group justify='center' py='xl'>
          <Loader size='lg' />
          <Text c='dimmed'>Loading alerts...</Text>
        </Group>
      </Card>
    );
  }

  if (alerts.length === 0) {
    return (
      <Card shadow='sm' padding='lg' radius='md' withBorder>
        <Group justify='center' py='xl'>
          <ThemeIcon size='xl' variant='light' color='green'>
            <IconCheck size={24} />
          </ThemeIcon>
          <Stack gap='xs' align='center'>
            <Text size='lg' fw={600}>
              No Alerts
            </Text>
            <Text size='sm' c='dimmed'>
              Your automation system is running smoothly
            </Text>
          </Stack>
        </Group>
      </Card>
    );
  }

  return (
    <Card shadow='sm' padding='lg' radius='md' withBorder>
      <Group justify='space-between' mb='md'>
        <Group gap='sm'>
          <Text fw={600} size='lg'>
            Alerts & Notifications
          </Text>
          {unacknowledgedAlerts.length > 0 && (
            <Badge color='red' variant='filled'>
              {unacknowledgedAlerts.length} new
            </Badge>
          )}
        </Group>

        <Group gap='xs'>
          <Badge variant='light' color='gray'>
            {alerts.length} total
          </Badge>
        </Group>
      </Group>

      <ScrollArea h={400}>
        <Stack gap='md'>
          {/* Unacknowledged Alerts */}
          {unacknowledgedAlerts.length > 0 && (
            <Box>
              <Text size='sm' fw={500} c='dimmed' mb='sm'>
                New Alerts ({unacknowledgedAlerts.length})
              </Text>
              <Stack gap='sm'>
                {unacknowledgedAlerts.map(alert => {
                  const alertConfig = getAlertIcon(alert.type);
                  const IconComponent = alertConfig.icon;

                  return (
                    <Alert
                      key={alert.id}
                      icon={<IconComponent size={16} />}
                      color={alertConfig.color}
                      title={getAlertTitle(alert.type)}
                      withCloseButton={false}
                      style={{
                        border: `2px solid var(--mantine-color-${alertConfig.color}-3)`,
                        backgroundColor: `var(--mantine-color-${alertConfig.color}-0)`,
                      }}
                    >
                      <Group justify='space-between' align='flex-start'>
                        <Box style={{ flex: 1 }}>
                          <Text size='sm' mb='xs'>
                            {alert.reason}
                          </Text>

                          {alert.positions_closed &&
                            alert.positions_closed.length > 0 && (
                              <Text size='xs' c='dimmed' mb='xs'>
                                Positions closed:{' '}
                                {alert.positions_closed.length}
                              </Text>
                            )}

                          <Group gap='xs'>
                            <IconClock size={12} />
                            <Text size='xs' c='dimmed'>
                              {formatTimestamp(alert.timestamp)}
                            </Text>
                          </Group>
                        </Box>

                        <Button
                          size='xs'
                          variant='subtle'
                          color={alertConfig.color}
                          loading={acknowledgingIds.has(alert.id)}
                          onClick={() => handleAcknowledge(alert.id)}
                          leftSection={<IconCheck size={12} />}
                        >
                          Acknowledge
                        </Button>
                      </Group>
                    </Alert>
                  );
                })}
              </Stack>
            </Box>
          )}

          {/* Acknowledged Alerts */}
          {acknowledgedAlerts.length > 0 && (
            <Box>
              <Text size='sm' fw={500} c='dimmed' mb='sm'>
                Acknowledged ({acknowledgedAlerts.length})
              </Text>
              <Stack gap='sm'>
                {acknowledgedAlerts.map(alert => {
                  const alertConfig = getAlertIcon(alert.type);
                  const IconComponent = alertConfig.icon;

                  return (
                    <Card
                      key={alert.id}
                      padding='sm'
                      radius='sm'
                      withBorder
                      style={{
                        opacity: 0.7,
                        backgroundColor: 'var(--mantine-color-gray-0)',
                      }}
                    >
                      <Group justify='space-between' align='flex-start'>
                        <Group gap='sm' align='flex-start'>
                          <ThemeIcon
                            size='sm'
                            color={alertConfig.color}
                            variant='light'
                          >
                            <IconComponent size={12} />
                          </ThemeIcon>

                          <Box style={{ flex: 1 }}>
                            <Text size='sm' fw={500} mb='xs'>
                              {getAlertTitle(alert.type)}
                            </Text>
                            <Text size='sm' c='dimmed' mb='xs'>
                              {alert.reason}
                            </Text>

                            <Group gap='xs'>
                              <IconClock size={12} />
                              <Text size='xs' c='dimmed'>
                                {formatTimestamp(alert.timestamp)}
                              </Text>
                            </Group>
                          </Box>
                        </Group>

                        <Tooltip label='Acknowledged'>
                          <ThemeIcon size='sm' color='green' variant='light'>
                            <IconCheck size={12} />
                          </ThemeIcon>
                        </Tooltip>
                      </Group>
                    </Card>
                  );
                })}
              </Stack>
            </Box>
          )}
        </Stack>
      </ScrollArea>
    </Card>
  );
}
