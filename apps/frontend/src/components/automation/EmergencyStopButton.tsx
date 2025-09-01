/**
 * Emergency Stop Button component for quick access
 */

import { useState } from 'react';
import { Button, Modal, Text, Alert, Stack, Textarea, Group } from '@mantine/core';
import { IconAlertTriangle, IconPlayerStop } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { useDisclosure } from '@mantine/hooks';
import { useAutomationStore } from '../../stores/automation';
import type { EmergencyStopRequest } from '../../types/automation';

interface EmergencyStopButtonProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'filled' | 'light' | 'outline' | 'subtle';
  fullWidth?: boolean;
  disabled?: boolean;
}

export function EmergencyStopButton({ 
  size = 'sm', 
  variant = 'filled',
  fullWidth = false,
  disabled = false
}: EmergencyStopButtonProps) {
  const [opened, { open, close }] = useDisclosure(false);
  const [reason, setReason] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { triggerEmergencyStop } = useAutomationStore();

  const handleEmergencyStop = async () => {
    if (!reason.trim()) {
      notifications.show({
        title: 'Reason Required',
        message: 'Please provide a reason for the emergency stop.',
        color: 'orange',
      });
      return;
    }

    setIsLoading(true);
    try {
      const request: EmergencyStopRequest = {
        reason: reason.trim(),
        close_positions: true,
      };
      
      await triggerEmergencyStop(request);
      
      notifications.show({
        title: 'Emergency Stop Triggered',
        message: 'All positions are being closed and auto trading has been disabled.',
        color: 'red',
        icon: <IconAlertTriangle size={16} />,
      });
      
      close();
      setReason('');
    } catch (error) {
      notifications.show({
        title: 'Emergency Stop Failed',
        message: 'Failed to trigger emergency stop. Please try again.',
        color: 'red',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Button
        color="red"
        variant={variant}
        size={size}
        fullWidth={fullWidth}
        disabled={disabled}
        onClick={open}
        leftSection={<IconPlayerStop size={16} />}
      >
        Emergency Stop
      </Button>

      <Modal
        opened={opened}
        onClose={close}
        title="Emergency Stop"
        centered
        closeOnClickOutside={!isLoading}
        closeOnEscape={!isLoading}
      >
        <Stack gap="md">
          <Alert
            icon={<IconAlertTriangle size={16} />}
            color="red"
            title="Emergency Stop Warning"
          >
            This will immediately:
            <ul style={{ marginTop: '8px', marginBottom: '0', paddingLeft: '20px' }}>
              <li>Disable auto trading</li>
              <li>Close all open positions</li>
              <li>Stop all background workers</li>
            </ul>
            <Text size="sm" fw={600} mt="xs">
              This action cannot be undone.
            </Text>
          </Alert>

          <div>
            <Text size="sm" fw={500} mb="xs">
              Reason for Emergency Stop <Text component="span" c="red">*</Text>
            </Text>
            <Textarea
              placeholder="Please provide a detailed reason for the emergency stop..."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              required
              error={!reason.trim() && reason.length > 0 ? 'Reason is required' : null}
            />
          </div>

          <Group justify="flex-end" gap="sm">
            <Button 
              variant="subtle" 
              onClick={close} 
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              color="red"
              loading={isLoading}
              onClick={handleEmergencyStop}
              leftSection={<IconPlayerStop size={16} />}
            >
              Emergency Stop
            </Button>
          </Group>
        </Stack>
      </Modal>
    </>
  );
}
