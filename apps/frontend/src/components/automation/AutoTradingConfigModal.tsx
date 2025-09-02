/**
 * Auto Trading Configuration Modal component
 */

import {
  Modal,
  Group,
  Text,
  Switch,
  NumberInput,
  Button,
  Stack,
  Alert,
  Divider,
  Badge,
  Box,
  Tooltip,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import {
  IconSettings,
  IconInfoCircle,
  IconAlertTriangle,
} from '@tabler/icons-react';
import { useState } from 'react';
import type {
  AutoTradingConfig,
  AutomationSettings,
} from '../../types/automation';

interface AutoTradingConfigModalProps {
  opened: boolean;
  onClose: () => void;
  currentConfig?: AutomationSettings;
  onSave: (config: AutoTradingConfig) => Promise<void>;
}

export function AutoTradingConfigModal({
  opened,
  onClose,
  currentConfig,
  onSave,
}: AutoTradingConfigModalProps) {
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<AutoTradingConfig>({
    initialValues: {
      enabled: currentConfig?.config.enabled ?? false,
      max_concurrent_positions:
        currentConfig?.config.max_concurrent_positions ?? 5,
      market_scan_interval: currentConfig?.config.market_scan_interval ?? 30,
      position_monitor_interval:
        currentConfig?.config.position_monitor_interval ?? 10,
      auto_stop_loss: currentConfig?.config.auto_stop_loss ?? true,
      auto_take_profit: currentConfig?.config.auto_take_profit ?? true,
    },
    validate: {
      max_concurrent_positions: value => {
        if (value < 1) return 'Must be at least 1';
        if (value > 10) return 'Cannot exceed 10 positions';
        return null;
      },
      market_scan_interval: value => {
        if (value < 10) return 'Minimum interval is 10 seconds';
        if (value > 300) return 'Maximum interval is 300 seconds';
        return null;
      },
      position_monitor_interval: value => {
        if (value < 5) return 'Minimum interval is 5 seconds';
        if (value > 60) return 'Maximum interval is 60 seconds';
        return null;
      },
    },
  });

  // Reset form when modal opens with new data
  const handleModalOpen = () => {
    if (currentConfig) {
      form.setValues({
        enabled: currentConfig.config.enabled,
        max_concurrent_positions: currentConfig.config.max_concurrent_positions,
        market_scan_interval: currentConfig.config.market_scan_interval,
        position_monitor_interval:
          currentConfig.config.position_monitor_interval,
        auto_stop_loss: currentConfig.config.auto_stop_loss,
        auto_take_profit: currentConfig.config.auto_take_profit,
      });
    }
  };

  const handleSubmit = async (values: AutoTradingConfig) => {
    setIsLoading(true);
    try {
      await onSave(values);
      onClose();
    } catch (error) {
      console.error('Failed to save config:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskLevel = () => {
    const values = form.values;

    if (!values.enabled)
      return { level: 'none', color: 'gray', text: 'Disabled' };

    let riskScore = 0;

    // Higher concurrent positions = higher risk
    if (values.max_concurrent_positions >= 8) riskScore += 3;
    else if (values.max_concurrent_positions >= 5) riskScore += 2;
    else riskScore += 1;

    // Faster scanning = higher activity = higher risk
    if (values.market_scan_interval <= 15) riskScore += 2;
    else if (values.market_scan_interval <= 30) riskScore += 1;

    // No safety features = higher risk
    if (!values.auto_stop_loss) riskScore += 2;
    if (!values.auto_take_profit) riskScore += 1;

    if (riskScore <= 3)
      return { level: 'low', color: 'green', text: 'Low Risk' };
    if (riskScore <= 5)
      return { level: 'medium', color: 'yellow', text: 'Medium Risk' };
    return { level: 'high', color: 'red', text: 'High Risk' };
  };

  const riskLevel = getRiskLevel();

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      onOpen={handleModalOpen}
      title={
        <Group gap='sm'>
          <IconSettings size={20} />
          <Text fw={600}>Auto Trading Configuration</Text>
        </Group>
      }
      size='lg'
      centered
    >
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <Stack gap='lg'>
          {/* Risk Level Indicator */}
          <Box>
            <Group justify='space-between' mb='sm'>
              <Text size='sm' fw={500}>
                Risk Assessment
              </Text>
              <Badge color={riskLevel.color} variant='filled'>
                {riskLevel.text}
              </Badge>
            </Group>

            {riskLevel.level === 'high' && (
              <Alert
                icon={<IconAlertTriangle size={16} />}
                color='red'
                title='High Risk Configuration'
                mb='md'
              >
                This configuration may result in higher trading frequency and
                risk. Please review your settings carefully.
              </Alert>
            )}
          </Box>

          {/* Enable/Disable Auto Trading */}
          <Group justify='space-between'>
            <Box>
              <Text fw={500} mb={4}>
                Enable Auto Trading
              </Text>
              <Text size='sm' c='dimmed'>
                Allow the system to automatically execute trades based on AI
                analysis
              </Text>
            </Box>
            <Switch
              size='lg'
              checked={form.values.enabled}
              onChange={event =>
                form.setFieldValue('enabled', event.currentTarget.checked)
              }
              color='green'
            />
          </Group>

          <Divider />

          {/* Position Limits */}
          <Box>
            <Text fw={500} mb='md'>
              Position Management
            </Text>
            <Stack gap='md'>
              <NumberInput
                label='Maximum Concurrent Positions'
                description='Maximum number of open positions at the same time'
                min={1}
                max={10}
                {...form.getInputProps('max_concurrent_positions')}
              />
            </Stack>
          </Box>

          <Divider />

          {/* Monitoring Intervals */}
          <Box>
            <Text fw={500} mb='md'>
              Monitoring Intervals
            </Text>
            <Stack gap='md'>
              <NumberInput
                label='Market Scan Interval (seconds)'
                description='How often to scan markets for new opportunities'
                min={10}
                max={300}
                suffix=' seconds'
                {...form.getInputProps('market_scan_interval')}
              />

              <NumberInput
                label='Position Monitor Interval (seconds)'
                description='How often to check existing positions'
                min={5}
                max={60}
                suffix=' seconds'
                {...form.getInputProps('position_monitor_interval')}
              />
            </Stack>
          </Box>

          <Divider />

          {/* Risk Management */}
          <Box>
            <Text fw={500} mb='md'>
              Risk Management
            </Text>
            <Stack gap='md'>
              <Group justify='space-between'>
                <Box>
                  <Text size='sm' fw={500}>
                    Auto Stop Loss
                  </Text>
                  <Text size='xs' c='dimmed'>
                    Automatically close losing positions based on your stop loss
                    settings
                  </Text>
                </Box>
                <Switch
                  checked={form.values.auto_stop_loss}
                  onChange={event =>
                    form.setFieldValue(
                      'auto_stop_loss',
                      event.currentTarget.checked
                    )
                  }
                  color='red'
                />
              </Group>

              <Group justify='space-between'>
                <Box>
                  <Text size='sm' fw={500}>
                    Auto Take Profit
                  </Text>
                  <Text size='xs' c='dimmed'>
                    Automatically close profitable positions based on your take
                    profit settings
                  </Text>
                </Box>
                <Switch
                  checked={form.values.auto_take_profit}
                  onChange={event =>
                    form.setFieldValue(
                      'auto_take_profit',
                      event.currentTarget.checked
                    )
                  }
                  color='green'
                />
              </Group>
            </Stack>
          </Box>

          {/* Information Alert */}
          <Alert
            icon={<IconInfoCircle size={16} />}
            color='blue'
            title='Important Information'
          >
            <Text size='sm'>
              • Auto trading will only work when your trading parameters are
              properly configured
              <br />
              • The system respects your risk limits and daily loss limits
              <br />
              • You can disable auto trading at any time using the emergency
              stop
              <br />• All trades are logged and can be reviewed in your trading
              history
            </Text>
          </Alert>

          {/* Action Buttons */}
          <Group justify='flex-end' gap='sm'>
            <Button variant='subtle' onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button
              type='submit'
              loading={isLoading}
              disabled={!form.isValid()}
            >
              Save Configuration
            </Button>
          </Group>
        </Stack>
      </form>
    </Modal>
  );
}
